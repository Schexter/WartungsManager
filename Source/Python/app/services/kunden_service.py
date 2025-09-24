# Kunden-Management Service für WartungsManager
# Geschäftslogik für Kunden/Mitglieder-Verwaltung

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from app import db
from app.models import Kunde, Flasche

logger = logging.getLogger(__name__)

class KundenService:
    """
    Service für Kunden/Mitglieder-Management
    
    Funktionen:
    - Automatische Kundenanlage
    - Kundensuche und -verwaltung
    - Mitgliedsnummern-System
    - Kunden-Flaschen Beziehungen
    """
    
    @staticmethod
    def kunde_erstellen_oder_finden(daten: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt neuen Kunden oder findet existierenden
        
        Args:
            daten: Dict mit Kundendaten (vorname, nachname, email, etc.)
        
        Returns:
            Dict mit Kunde und Ergebnis-Informationen
        """
        
        try:
            # Validiere Pflichtfelder
            if not daten.get('vorname') or not daten.get('nachname'):
                return {
                    'success': False,
                    'error': 'Vorname und Nachname sind Pflichtfelder'
                }
            
            # Prüfe ob Kunde bereits existiert
            existierender_kunde = Kunde.pruefen_kunde_existiert(
                vorname=daten.get('vorname'),
                nachname=daten.get('nachname'),
                email=daten.get('email'),
                mitgliedsnummer=daten.get('mitgliedsnummer')
            )
            
            if existierender_kunde:
                logger.info(f"Existierender Kunde gefunden: {existierender_kunde.vollname}")
                return {
                    'success': True,
                    'kunde': existierender_kunde.to_dict(include_flaschen=True),
                    'neu_erstellt': False,
                    'message': f'Kunde bereits vorhanden: {existierender_kunde.vollname} ({existierender_kunde.mitgliedsnummer})'
                }
            
            # Neuen Kunden erstellen
            neue_mitgliedsnummer = daten.get('mitgliedsnummer') or Kunde.get_naechste_mitgliedsnummer()
            
            # Prüfe ob Mitgliedsnummer bereits existiert
            if Kunde.query.filter_by(mitgliedsnummer=neue_mitgliedsnummer).first():
                return {
                    'success': False,
                    'error': f'Mitgliedsnummer {neue_mitgliedsnummer} bereits vergeben'
                }
            
            neuer_kunde = Kunde(
                mitgliedsnummer=neue_mitgliedsnummer,
                vorname=daten['vorname'],
                nachname=daten['nachname'],
                firma=daten.get('firma'),
                email=daten.get('email'),
                telefon=daten.get('telefon'),
                strasse=daten.get('strasse'),
                plz=daten.get('plz'),
                ort=daten.get('ort'),
                mitgliedschaft_typ=daten.get('mitgliedschaft_typ', 'Standard'),
                notizen=daten.get('notizen')
            )
            
            db.session.add(neuer_kunde)
            db.session.commit()
            
            logger.info(f"Neuer Kunde erstellt: {neuer_kunde.vollname} ({neue_mitgliedsnummer})")
            
            return {
                'success': True,
                'kunde': neuer_kunde.to_dict(include_flaschen=True),
                'neu_erstellt': True,
                'message': f'Neuer Kunde erstellt: {neuer_kunde.vollname} ({neue_mitgliedsnummer})'
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Kunde erstellen/finden: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler: {str(e)}'
            }
    
    @staticmethod
    def kunde_suchen(suchbegriff: str) -> Dict[str, Any]:
        """
        Sucht Kunden nach verschiedenen Kriterien
        
        Args:
            suchbegriff: Suchtext (Name, Mitgliedsnummer, Email, etc.)
        
        Returns:
            Dict mit Suchergebnissen
        """
        
        try:
            if not suchbegriff or len(suchbegriff.strip()) < 2:
                return {
                    'success': False,
                    'error': 'Suchbegriff muss mindestens 2 Zeichen lang sein',
                    'kunden': []
                }
            
            kunden = Kunde.suche_kunde(suchbegriff.strip())
            
            kunden_data = []
            for kunde in kunden:
                kunde_dict = kunde.to_dict()
                # Zusätzliche Informationen für Suchresultate
                kunde_dict['anzahl_aktive_flaschen'] = kunde.aktive_flaschen.count()
                kunden_data.append(kunde_dict)
            
            logger.info(f"Kundensuche '{suchbegriff}': {len(kunden)} Ergebnisse")
            
            return {
                'success': True,
                'anzahl': len(kunden),
                'suchbegriff': suchbegriff,
                'kunden': kunden_data
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Kundensuche: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'kunden': []
            }
    
    @staticmethod
    def kunde_details_abrufen(kunde_id: int = None, mitgliedsnummer: str = None) -> Dict[str, Any]:
        """
        Ruft detaillierte Kundeninformationen ab
        
        Args:
            kunde_id: ID des Kunden (Alternative zu Mitgliedsnummer)
            mitgliedsnummer: Mitgliedsnummer des Kunden
        
        Returns:
            Dict mit Kundendetails
        """
        
        try:
            if kunde_id:
                kunde = Kunde.query.get(kunde_id)
            elif mitgliedsnummer:
                kunde = Kunde.query.filter_by(mitgliedsnummer=mitgliedsnummer).first()
            else:
                return {
                    'success': False,
                    'error': 'Kunde-ID oder Mitgliedsnummer muss angegeben werden'
                }
            
            if not kunde:
                return {
                    'success': False,
                    'error': 'Kunde nicht gefunden'
                }
            
            # Detaillierte Kundendaten mit Flaschen
            kunde_data = kunde.to_dict(include_flaschen=True)
            
            # Zusätzliche Statistiken
            aktive_flaschen = kunde.aktive_flaschen.all()
            flaschen_mit_pruefung_faellig = [f for f in aktive_flaschen if f.pruefung_faellig]
            
            kunde_data['statistiken'] = {
                'anzahl_flaschen_gesamt': kunde.anzahl_flaschen,
                'anzahl_aktive_flaschen': len(aktive_flaschen),
                'flaschen_pruefung_faellig': len(flaschen_mit_pruefung_faellig),
                'mitglied_seit_tagen': (datetime.utcnow().date() - kunde.mitglied_seit).days
            }
            
            return {
                'success': True,
                'kunde': kunde_data
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Kundendetails: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def kunde_aktualisieren(kunde_id: int, daten: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktualisiert Kundendaten
        
        Args:
            kunde_id: ID des Kunden
            daten: Dict mit zu aktualisierenden Daten
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            kunde = Kunde.query.get(kunde_id)
            if not kunde:
                return {
                    'success': False,
                    'error': 'Kunde nicht gefunden'
                }
            
            # Aktualisierbare Felder
            aktualisierbare_felder = [
                'vorname', 'nachname', 'firma', 'email', 'telefon',
                'strasse', 'plz', 'ort', 'mitgliedschaft_typ', 'notizen'
            ]
            
            changed_fields = []
            for feld in aktualisierbare_felder:
                if feld in daten and daten[feld] != getattr(kunde, feld):
                    old_value = getattr(kunde, feld)
                    setattr(kunde, feld, daten[feld])
                    changed_fields.append(f"{feld}: '{old_value}' → '{daten[feld]}'")
            
            if not changed_fields:
                return {
                    'success': True,
                    'message': 'Keine Änderungen vorgenommen',
                    'kunde': kunde.to_dict()
                }
            
            kunde.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Kunde {kunde.vollname} aktualisiert: {', '.join(changed_fields)}")
            
            return {
                'success': True,
                'message': f'Kunde erfolgreich aktualisiert',
                'kunde': kunde.to_dict(),
                'geaenderte_felder': changed_fields
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Kunden: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def kunde_deaktivieren(kunde_id: int, grund: str = None) -> Dict[str, Any]:
        """
        Deaktiviert einen Kunden
        
        Args:
            kunde_id: ID des Kunden
            grund: Grund für Deaktivierung
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            kunde = Kunde.query.get(kunde_id)
            if not kunde:
                return {
                    'success': False,
                    'error': 'Kunde nicht gefunden'
                }
            
            if not kunde.ist_aktiv:
                return {
                    'success': False,
                    'error': 'Kunde ist bereits deaktiviert'
                }
            
            kunde.deaktivieren(grund)
            
            # Alle Flaschen des Kunden auch deaktivieren
            aktive_flaschen = kunde.aktive_flaschen.all()
            for flasche in aktive_flaschen:
                flasche.deaktivieren(f"Kunde deaktiviert: {grund}")
            
            db.session.commit()
            
            logger.warning(f"Kunde {kunde.vollname} deaktiviert: {grund}")
            
            return {
                'success': True,
                'message': f'Kunde deaktiviert ({len(aktive_flaschen)} Flaschen ebenfalls deaktiviert)',
                'kunde': kunde.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Deaktivieren des Kunden: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def kunde_reaktivieren(kunde_id: int, grund: str = None) -> Dict[str, Any]:
        """
        Reaktiviert einen Kunden
        
        Args:
            kunde_id: ID des Kunden
            grund: Grund für Reaktivierung
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            kunde = Kunde.query.get(kunde_id)
            if not kunde:
                return {
                    'success': False,
                    'error': 'Kunde nicht gefunden'
                }
            
            if kunde.ist_aktiv:
                return {
                    'success': False,
                    'error': 'Kunde ist bereits aktiv'
                }
            
            kunde.reaktivieren(grund)
            db.session.commit()
            
            logger.info(f"Kunde {kunde.vollname} reaktiviert: {grund}")
            
            return {
                'success': True,
                'message': 'Kunde erfolgreich reaktiviert (Flaschen müssen einzeln reaktiviert werden)',
                'kunde': kunde.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Reaktivieren des Kunden: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_kunden_statistiken() -> Dict[str, Any]:
        """
        Gibt umfassende Kunden-Statistiken zurück
        
        Returns:
            Dict mit Statistiken
        """
        
        try:
            stats = Kunde.get_kunden_statistiken()
            
            # Zusätzliche Berechnungen
            heute = datetime.utcnow().date()
            
            # Top-Kunden nach Flaschen-Anzahl
            top_kunden = db.session.query(
                Kunde.vorname,
                Kunde.nachname,
                Kunde.mitgliedsnummer,
                db.func.count(Flasche.id).label('anzahl_flaschen')
            ).join(
                Flasche, Kunde.id == Flasche.kunde_id
            ).filter(
                Kunde.ist_aktiv == True,
                Flasche.ist_aktiv == True
            ).group_by(
                Kunde.id
            ).order_by(
                db.func.count(Flasche.id).desc()
            ).limit(5).all()
            
            # Neueste Mitglieder
            neue_mitglieder = Kunde.query.filter_by(
                ist_aktiv=True
            ).order_by(
                Kunde.mitglied_seit.desc()
            ).limit(5).all()
            
            stats['top_kunden_nach_flaschen'] = [
                {
                    'name': f"{kunde[0]} {kunde[1]}",
                    'mitgliedsnummer': kunde[2],
                    'anzahl_flaschen': kunde[3]
                }
                for kunde in top_kunden
            ]
            
            stats['neueste_mitglieder'] = [
                {
                    'name': kunde.vollname,
                    'mitgliedsnummer': kunde.mitgliedsnummer,
                    'mitglied_seit': kunde.mitglied_seit.isoformat(),
                    'tage_mitglied': (heute - kunde.mitglied_seit).days
                }
                for kunde in neue_mitglieder
            ]
            
            return {
                'success': True,
                'statistiken': stats
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Kunden-Statistiken: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def quick_kundenanlage_fuer_fuellung(vorname: str, nachname: str, 
                                        telefon: str = None, email: str = None) -> Dict[str, Any]:
        """
        Schnelle Kundenanlage für Füllvorgänge
        
        Args:
            vorname: Vorname des Kunden
            nachname: Nachname des Kunden
            telefon: Optional Telefonnummer
            email: Optional Email
        
        Returns:
            Dict mit Kunde und Ergebnis
        """
        
        try:
            # Minimaldaten für schnelle Anlage
            daten = {
                'vorname': vorname.strip(),
                'nachname': nachname.strip(),
                'telefon': telefon.strip() if telefon else None,
                'email': email.strip() if email else None,
                'mitgliedschaft_typ': 'Standard',
                'notizen': f'Schnellanlage vom {datetime.utcnow().strftime("%d.%m.%Y %H:%M")}'
            }
            
            result = KundenService.kunde_erstellen_oder_finden(daten)
            
            if result['success']:
                logger.info(f"Quick-Kundenanlage: {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei Quick-Kundenanlage: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_kundendaten(daten: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validiert Kundendaten
        
        Args:
            daten: Dict mit Kundendaten
        
        Returns:
            Dict mit Validierungs-Ergebnis
        """
        
        errors = []
        warnings = []
        
        # Pflichtfelder prüfen
        if not daten.get('vorname') or len(daten['vorname'].strip()) < 2:
            errors.append("Vorname muss mindestens 2 Zeichen lang sein")
        
        if not daten.get('nachname') or len(daten['nachname'].strip()) < 2:
            errors.append("Nachname muss mindestens 2 Zeichen lang sein")
        
        # Email-Format prüfen (basic)
        if daten.get('email'):
            email = daten['email'].strip()
            if '@' not in email or '.' not in email:
                warnings.append("Email-Format scheint ungültig zu sein")
        
        # Telefon prüfen
        if daten.get('telefon'):
            telefon = daten['telefon'].strip()
            if len(telefon) < 6:
                warnings.append("Telefonnummer scheint zu kurz zu sein")
        
        # Adresse-Vollständigkeit prüfen
        adress_felder = ['strasse', 'plz', 'ort']
        adress_angegeben = [feld for feld in adress_felder if daten.get(feld)]
        
        if adress_angegeben and len(adress_angegeben) < 3:
            warnings.append("Adresse ist unvollständig (Straße, PLZ, Ort)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
