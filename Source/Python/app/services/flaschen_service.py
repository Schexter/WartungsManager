# Flaschen-Management Service für WartungsManager
# Geschäftslogik für Flaschen-Verwaltung und TÜV-Management

from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, List
import logging
from app import db
from app.models import Flasche, Kunde

logger = logging.getLogger(__name__)

class FlaschenService:
    """
    Service für Flaschen-Management
    
    Funktionen:
    - Flaschen-Registry Management
    - TÜV-Prüfungs-Verwaltung
    - Vormerkungssystem für Bulk-Füllungen
    - Barcode/Scanning-Integration
    """
    
    @staticmethod
    def flasche_erstellen(kunde_id: int, daten: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt neue Flasche für einen Kunden
        
        Args:
            kunde_id: ID des Besitzer-Kunden
            daten: Dict mit Flaschen-Daten
        
        Returns:
            Dict mit Ergebnis und Flaschen-Daten
        """
        
        try:
            # Kunde prüfen
            kunde = Kunde.query.get(kunde_id)
            if not kunde:
                return {
                    'success': False,
                    'error': 'Kunde nicht gefunden'
                }
            
            if not kunde.ist_aktiv:
                return {
                    'success': False,
                    'error': 'Flasche kann nicht für inaktiven Kunden erstellt werden'
                }
            
            # Flaschennummer generieren oder prüfen
            flaschennummer = daten.get('flaschennummer') or Flasche.get_naechste_flaschennummer()
            
            # Prüfe ob Flaschennummer bereits existiert
            if Flasche.query.filter_by(flaschennummer=flaschennummer).first():
                return {
                    'success': False,
                    'error': f'Flaschennummer {flaschennummer} bereits vergeben'
                }
            
            # Barcode prüfen falls angegeben
            if daten.get('barcode'):
                if Flasche.query.filter_by(barcode=daten['barcode']).first():
                    return {
                        'success': False,
                        'error': f'Barcode {daten["barcode"]} bereits vergeben'
                    }
            
            # TÜV-Prüfung Datum verarbeiten
            pruef_datum = None
            naechste_pruefung = None
            
            if daten.get('pruef_datum'):
                if isinstance(daten['pruef_datum'], str):
                    pruef_datum = datetime.strptime(daten['pruef_datum'], '%Y-%m-%d').date()
                else:
                    pruef_datum = daten['pruef_datum']
                
                # Automatisch nächste Prüfung berechnen (5 Jahre)
                naechste_pruefung = pruef_datum + timedelta(days=5*365)
            
            if daten.get('naechste_pruefung'):
                if isinstance(daten['naechste_pruefung'], str):
                    naechste_pruefung = datetime.strptime(daten['naechste_pruefung'], '%Y-%m-%d').date()
                else:
                    naechste_pruefung = daten['naechste_pruefung']
            
            # Neue Flasche erstellen
            neue_flasche = Flasche(
                flaschennummer=flaschennummer,
                kunde_id=kunde_id,
                barcode=daten.get('barcode'),
                groesse_liter=float(daten.get('groesse_liter', 11.0)),
                flaschen_typ=daten.get('flaschen_typ', 'Standard'),
                farbe=daten.get('farbe'),
                hersteller=daten.get('hersteller'),
                pruef_datum=pruef_datum,
                naechste_pruefung=naechste_pruefung,
                max_druck_bar=int(daten.get('max_druck_bar', 300)),
                notizen=daten.get('notizen')
            )
            
            db.session.add(neue_flasche)
            db.session.commit()
            
            logger.info(f"Neue Flasche erstellt: {flaschennummer} für {kunde.vollname}")
            
            return {
                'success': True,
                'message': f'Flasche {flaschennummer} erfolgreich erstellt',
                'flasche': neue_flasche.to_dict(include_besitzer=True)
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Flasche: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler: {str(e)}'
            }
    
    @staticmethod
    def flasche_suchen(suchbegriff: str) -> Dict[str, Any]:
        """
        Sucht Flaschen nach verschiedenen Kriterien
        
        Args:
            suchbegriff: Suchtext (Flaschennummer, Barcode, Besitzer, etc.)
        
        Returns:
            Dict mit Suchergebnissen
        """
        
        try:
            if not suchbegriff or len(suchbegriff.strip()) < 2:
                return {
                    'success': False,
                    'error': 'Suchbegriff muss mindestens 2 Zeichen lang sein',
                    'flaschen': []
                }
            
            flaschen = Flasche.suche_flaschen(suchbegriff.strip())
            
            flaschen_data = []
            for flasche in flaschen:
                flasche_dict = flasche.to_dict(include_besitzer=True)
                # Zusätzliche Such-relevante Informationen
                flasche_dict['kann_gefuellt_werden'] = flasche.ist_fuellbereit
                flasche_dict['tage_bis_pruefung'] = flasche.pruefung_faellig_in_tagen
                flaschen_data.append(flasche_dict)
            
            logger.info(f"Flaschensuche '{suchbegriff}': {len(flaschen)} Ergebnisse")
            
            return {
                'success': True,
                'anzahl': len(flaschen),
                'suchbegriff': suchbegriff,
                'flaschen': flaschen_data
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Flaschensuche: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'flaschen': []
            }
    
    @staticmethod
    def flasche_details_abrufen(flasche_id: int = None, flaschennummer: str = None, 
                               barcode: str = None) -> Dict[str, Any]:
        """
        Ruft detaillierte Flascheninformationen ab
        
        Args:
            flasche_id: ID der Flasche
            flaschennummer: Flaschennummer
            barcode: Barcode der Flasche
        
        Returns:
            Dict mit Flaschendetails
        """
        
        try:
            if flasche_id:
                flasche = Flasche.query.get(flasche_id)
            elif flaschennummer:
                flasche = Flasche.query.filter_by(flaschennummer=flaschennummer).first()
            elif barcode:
                flasche = Flasche.query.filter_by(barcode=barcode).first()
            else:
                return {
                    'success': False,
                    'error': 'Flasche-ID, Flaschennummer oder Barcode muss angegeben werden'
                }
            
            if not flasche:
                return {
                    'success': False,
                    'error': 'Flasche nicht gefunden'
                }
            
            # Detaillierte Flaschen-Daten
            flasche_data = flasche.to_dict(include_besitzer=True)
            
            # Füllhistorie (TODO: Implementieren wenn Füllvorgang-Beziehung erstellt)
            # flasche_data['fuellhistorie'] = []
            
            return {
                'success': True,
                'flasche': flasche_data
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Flaschendetails: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def flasche_aktualisieren(flasche_id: int, daten: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktualisiert Flaschendaten
        
        Args:
            flasche_id: ID der Flasche
            daten: Dict mit zu aktualisierenden Daten
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            flasche = Flasche.query.get(flasche_id)
            if not flasche:
                return {
                    'success': False,
                    'error': 'Flasche nicht gefunden'
                }
            
            # Aktualisierbare Felder
            aktualisierbare_felder = [
                'groesse_liter', 'flaschen_typ', 'farbe', 'hersteller',
                'max_druck_bar', 'letzter_fuellstand', 'notizen'
            ]
            
            changed_fields = []
            for feld in aktualisierbare_felder:
                if feld in daten and daten[feld] != getattr(flasche, feld):
                    old_value = getattr(flasche, feld)
                    
                    # Spezielle Behandlung für numerische Felder
                    if feld in ['groesse_liter', 'max_druck_bar', 'letzter_fuellstand']:
                        setattr(flasche, feld, float(daten[feld]) if daten[feld] else None)
                    else:
                        setattr(flasche, feld, daten[feld])
                    
                    changed_fields.append(f"{feld}: '{old_value}' → '{daten[feld]}'")
            
            # Spezielle Behandlung für Datumsfelder
            datum_felder = ['pruef_datum', 'naechste_pruefung']
            for feld in datum_felder:
                if feld in daten:
                    new_date = None
                    if daten[feld]:
                        if isinstance(daten[feld], str):
                            new_date = datetime.strptime(daten[feld], '%Y-%m-%d').date()
                        else:
                            new_date = daten[feld]
                    
                    if new_date != getattr(flasche, feld):
                        old_value = getattr(flasche, feld)
                        setattr(flasche, feld, new_date)
                        changed_fields.append(f"{feld}: '{old_value}' → '{new_date}'")
            
            if not changed_fields:
                return {
                    'success': True,
                    'message': 'Keine Änderungen vorgenommen',
                    'flasche': flasche.to_dict(include_besitzer=True)
                }
            
            flasche.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Flasche {flasche.flaschennummer} aktualisiert: {', '.join(changed_fields)}")
            
            return {
                'success': True,
                'message': 'Flasche erfolgreich aktualisiert',
                'flasche': flasche.to_dict(include_besitzer=True),
                'geaenderte_felder': changed_fields
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Flasche: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def flasche_tuev_erneuern(flasche_id: int, neues_pruef_datum: date, 
                             naechste_pruefung: date = None) -> Dict[str, Any]:
        """
        Erneuert TÜV-Prüfung einer Flasche
        
        Args:
            flasche_id: ID der Flasche
            neues_pruef_datum: Datum der neuen Prüfung
            naechste_pruefung: Optional nächstes Prüfdatum (sonst automatisch +5 Jahre)
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            flasche = Flasche.query.get(flasche_id)
            if not flasche:
                return {
                    'success': False,
                    'error': 'Flasche nicht gefunden'
                }
            
            # Datum validieren
            if isinstance(neues_pruef_datum, str):
                neues_pruef_datum = datetime.strptime(neues_pruef_datum, '%Y-%m-%d').date()
            
            if naechste_pruefung and isinstance(naechste_pruefung, str):
                naechste_pruefung = datetime.strptime(naechste_pruefung, '%Y-%m-%d').date()
            
            # Prüfung erneuern
            flasche.pruefung_erneuern(neues_pruef_datum, naechste_pruefung)
            db.session.commit()
            
            logger.info(f"TÜV-Prüfung erneuert für Flasche {flasche.flaschennummer}: {neues_pruef_datum}")
            
            return {
                'success': True,
                'message': f'TÜV-Prüfung erneuert bis {flasche.naechste_pruefung}',
                'flasche': flasche.to_dict(include_besitzer=True)
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Erneuern der TÜV-Prüfung: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def flasche_vormerkung_setzen(flasche_ids: List[int], vorgemerkt: bool = True) -> Dict[str, Any]:
        """
        Setzt Vormerkung für Bulk-Füllung für mehrere Flaschen
        
        Args:
            flasche_ids: Liste von Flaschen-IDs
            vorgemerkt: True für vormerken, False für entfernen
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            if not flasche_ids:
                return {
                    'success': False,
                    'error': 'Keine Flaschen-IDs angegeben'
                }
            
            flaschen = Flasche.query.filter(Flasche.id.in_(flasche_ids)).all()
            
            if not flaschen:
                return {
                    'success': False,
                    'error': 'Keine Flaschen gefunden'
                }
            
            erfolgreiche_aenderungen = []
            fehler = []
            
            for flasche in flaschen:
                try:
                    if not flasche.ist_aktiv:
                        fehler.append(f"{flasche.flaschennummer}: Flasche nicht aktiv")
                        continue
                    
                    if vorgemerkt and flasche.pruefung_faellig:
                        fehler.append(f"{flasche.flaschennummer}: TÜV-Prüfung fällig")
                        continue
                    
                    if flasche.ist_zum_fuellen_vorgemerkt != vorgemerkt:
                        flasche.vormerkung_setzen(vorgemerkt)
                        erfolgreiche_aenderungen.append(flasche.flaschennummer)
                    
                except Exception as e:
                    fehler.append(f"{flasche.flaschennummer}: {str(e)}")
            
            db.session.commit()
            
            action = "vorgemerkt" if vorgemerkt else "Vormerkung entfernt"
            logger.info(f"{len(erfolgreiche_aenderungen)} Flaschen {action}")
            
            return {
                'success': True,
                'message': f'{len(erfolgreiche_aenderungen)} Flaschen {action}',
                'erfolgreiche_aenderungen': erfolgreiche_aenderungen,
                'fehler': fehler,
                'anzahl_erfolgreich': len(erfolgreiche_aenderungen),
                'anzahl_fehler': len(fehler)
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Setzen der Vormerkung: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_vorgemerkte_flaschen() -> Dict[str, Any]:
        """
        Gibt alle zum Füllen vorgemerkten Flaschen zurück
        
        Returns:
            Dict mit vorgemerkten Flaschen
        """
        
        try:
            vorgemerkte_flaschen = Flasche.get_vorgemerkte_flaschen()
            
            flaschen_data = []
            for flasche in vorgemerkte_flaschen:
                flasche_dict = flasche.to_dict(include_besitzer=True)
                flasche_dict['kann_gefuellt_werden'] = flasche.ist_fuellbereit
                flaschen_data.append(flasche_dict)
            
            return {
                'success': True,
                'anzahl': len(vorgemerkte_flaschen),
                'flaschen': flaschen_data
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen vorgemerkter Flaschen: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'flaschen': []
            }
    
    @staticmethod
    def get_pruefung_faellige_flaschen() -> Dict[str, Any]:
        """
        Gibt Flaschen mit fälliger TÜV-Prüfung zurück
        
        Returns:
            Dict mit prüfungsfälligen Flaschen
        """
        
        try:
            faellige_flaschen = Flasche.get_pruefung_faellige_flaschen()
            
            flaschen_data = []
            for flasche in faellige_flaschen:
                flasche_dict = flasche.to_dict(include_besitzer=True)
                flaschen_data.append(flasche_dict)
            
            # Nach Dringlichkeit sortieren
            flaschen_data.sort(key=lambda x: x['pruefung_faellig_in_tagen'])
            
            return {
                'success': True,
                'anzahl': len(faellige_flaschen),
                'flaschen': flaschen_data
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen prüfungsfälliger Flaschen: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'flaschen': []
            }
    
    @staticmethod
    def get_flaschen_statistiken() -> Dict[str, Any]:
        """
        Gibt umfassende Flaschen-Statistiken zurück
        
        Returns:
            Dict mit Statistiken
        """
        
        try:
            stats = Flasche.get_flaschen_statistiken()
            
            # Zusätzliche Berechnungen
            # Top-Besitzer nach Flaschen-Anzahl
            top_besitzer = db.session.query(
                Kunde.vorname,
                Kunde.nachname,
                Kunde.mitgliedsnummer,
                db.func.count(Flasche.id).label('anzahl_flaschen')
            ).join(
                Flasche, Kunde.id == Flasche.kunde_id
            ).filter(
                Flasche.ist_aktiv == True
            ).group_by(
                Kunde.id
            ).order_by(
                db.func.count(Flasche.id).desc()
            ).limit(5).all()
            
            # Flaschen nach Alter (basierend auf Prüfdatum)
            heute = datetime.utcnow().date()
            sehr_alte_flaschen = Flasche.query.filter(
                Flasche.pruef_datum < (heute - timedelta(days=10*365)),  # Älter als 10 Jahre
                Flasche.ist_aktiv == True
            ).count()
            
            stats['top_besitzer'] = [
                {
                    'name': f"{besitzer[0]} {besitzer[1]}",
                    'mitgliedsnummer': besitzer[2],
                    'anzahl_flaschen': besitzer[3]
                }
                for besitzer in top_besitzer
            ]
            
            stats['sehr_alte_flaschen'] = sehr_alte_flaschen
            
            return {
                'success': True,
                'statistiken': stats
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Flaschen-Statistiken: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def flasche_besitzer_wechseln(flasche_id: int, neuer_kunde_id: int, 
                                 grund: str = None) -> Dict[str, Any]:
        """
        Wechselt den Besitzer einer Flasche
        
        Args:
            flasche_id: ID der Flasche
            neuer_kunde_id: ID des neuen Besitzers
            grund: Grund für den Besitzerwechsel
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            flasche = Flasche.query.get(flasche_id)
            if not flasche:
                return {
                    'success': False,
                    'error': 'Flasche nicht gefunden'
                }
            
            neuer_kunde = Kunde.query.get(neuer_kunde_id)
            if not neuer_kunde:
                return {
                    'success': False,
                    'error': 'Neuer Kunde nicht gefunden'
                }
            
            if not neuer_kunde.ist_aktiv:
                return {
                    'success': False,
                    'error': 'Neuer Kunde ist nicht aktiv'
                }
            
            alter_besitzer = flasche.besitzer.vollname
            flasche.kunde_id = neuer_kunde_id
            
            # Notiz hinzufügen
            notiz = f"Besitzerwechsel von {alter_besitzer} zu {neuer_kunde.vollname}"
            if grund:
                notiz += f" - Grund: {grund}"
            notiz += f" ({datetime.utcnow().strftime('%d.%m.%Y %H:%M')})"
            
            flasche.notizen = flasche.notizen or ""
            flasche.notizen += f"\n{notiz}"
            flasche.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Besitzerwechsel für Flasche {flasche.flaschennummer}: {alter_besitzer} → {neuer_kunde.vollname}")
            
            return {
                'success': True,
                'message': f'Besitzer erfolgreich gewechselt von {alter_besitzer} zu {neuer_kunde.vollname}',
                'flasche': flasche.to_dict(include_besitzer=True)
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Besitzerwechsel: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_flaschen_daten(daten: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validiert Flaschen-Daten
        
        Args:
            daten: Dict mit Flaschen-Daten
        
        Returns:
            Dict mit Validierungs-Ergebnis
        """
        
        errors = []
        warnings = []
        
        # Größe prüfen
        if daten.get('groesse_liter'):
            try:
                groesse = float(daten['groesse_liter'])
                if groesse <= 0 or groesse > 50:
                    warnings.append("Ungewöhnliche Flaschengröße (0-50 Liter erwartet)")
            except ValueError:
                errors.append("Flaschengröße muss eine Zahl sein")
        
        # Druck prüfen
        if daten.get('max_druck_bar'):
            try:
                druck = int(daten['max_druck_bar'])
                if druck < 100 or druck > 500:
                    warnings.append("Ungewöhnlicher Maximaldruck (100-500 Bar erwartet)")
            except ValueError:
                errors.append("Maximaldruck muss eine ganze Zahl sein")
        
        # Prüfdatum prüfen
        if daten.get('pruef_datum'):
            try:
                if isinstance(daten['pruef_datum'], str):
                    pruef_datum = datetime.strptime(daten['pruef_datum'], '%Y-%m-%d').date()
                else:
                    pruef_datum = daten['pruef_datum']
                
                heute = datetime.utcnow().date()
                if pruef_datum > heute:
                    warnings.append("Prüfdatum liegt in der Zukunft")
                elif (heute - pruef_datum).days > 10*365:
                    warnings.append("Prüfdatum ist sehr alt (über 10 Jahre)")
                    
            except ValueError:
                errors.append("Prüfdatum muss im Format YYYY-MM-DD sein")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    @staticmethod
    def leere_flasche_annehmen(barcode: str, kunde_name: str, status: str = 'leer', 
                              notizen: str = None, ohne_kompressor: bool = True) -> Dict[str, Any]:
        """
        Nimmt leere Flaschen ohne Kompressor-Betrieb an
        
        Args:
            barcode: Barcode der Flasche
            kunde_name: Name des Kunden (Besitzers)
            status: Status der angenommenen Flasche
            notizen: Optionale Notizen
            ohne_kompressor: Flag dass ohne Kompressor angenommen
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            # Kunde suchen oder erstellen
            from app.services.kunden_service import KundenService
            
            kunde_result = KundenService.kunde_finden_oder_erstellen(kunde_name)
            if not kunde_result['success']:
                return {
                    'success': False,
                    'error': f'Kunde-Problem: {kunde_result["error"]}'
                }
            
            kunde = kunde_result['kunde']
            
            # Prüfe ob Flasche bereits existiert
            existierende_flasche = Flasche.query.filter_by(barcode=barcode.strip()).first()
            
            if existierende_flasche:
                # Flasche existiert - nur Status aktualisieren
                old_status = existierende_flasche.ist_zum_fuellen_vorgemerkt
                
                if status == 'leer':
                    existierende_flasche.ist_zum_fuellen_vorgemerkt = True
                    existierende_flasche.ist_aktiv = True
                elif status == 'leer_wartung':
                    existierende_flasche.ist_zum_fuellen_vorgemerkt = False
                    existierende_flasche.ist_aktiv = True
                elif status == 'defekt':
                    existierende_flasche.ist_aktiv = False
                    existierende_flasche.ist_zum_fuellen_vorgemerkt = False
                
                # Notizen hinzufügen
                notiz = f"Leere Flasche angenommen ({status}) - ohne Kompressor"
                if notizen:
                    notiz += f": {notizen}"
                notiz += f" ({datetime.utcnow().strftime('%d.%m.%Y %H:%M')})"
                
                existierende_flasche.notizen = existierende_flasche.notizen or ""
                existierende_flasche.notizen += f"\n{notiz}"
                existierende_flasche.updated_at = datetime.utcnow()
                
                db.session.commit()
                
                logger.info(f"Leere Flasche aktualisiert: {existierende_flasche.flaschennummer} - Status: {status}")
                
                return {
                    'success': True,
                    'message': f'Leere Flasche {existierende_flasche.flaschennummer} aktualisiert',
                    'flasche': existierende_flasche.to_dict(include_besitzer=True),
                    'war_bereits_vorhanden': True
                }
            else:
                # Neue Flasche erstellen
                flaschennummer = Flasche.get_naechste_flaschennummer()
                
                neue_flasche = Flasche(
                    flaschennummer=flaschennummer,
                    barcode=barcode.strip(),
                    kunde_id=kunde['id'],
                    groesse_liter=11.0,  # Standard
                    flaschen_typ='Standard',
                    max_druck_bar=300,
                    ist_aktiv=(status != 'defekt'),
                    ist_zum_fuellen_vorgemerkt=(status == 'leer')
                )
                
                # Notizen hinzufügen
                notiz = f"Neue leere Flasche angenommen ({status}) - ohne Kompressor"
                if notizen:
                    notiz += f": {notizen}"
                notiz += f" ({datetime.utcnow().strftime('%d.%m.%Y %H:%M')})"
                
                neue_flasche.notizen = notiz
                
                db.session.add(neue_flasche)
                db.session.commit()
                
                logger.info(f"Neue leere Flasche erstellt: {flaschennummer} für {kunde_name} - Status: {status}")
                
                return {
                    'success': True,
                    'message': f'Neue Flasche {flaschennummer} erfolgreich angelegt',
                    'flasche': neue_flasche.to_dict(include_besitzer=True),
                    'war_bereits_vorhanden': False
                }
            
        except Exception as e:
            logger.error(f"Fehler beim Annehmen der leeren Flasche: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler: {str(e)}'
            }

class FlaschenScanService:
    """
    Service für Barcode-Scanning und Flaschen-Identifikation
    """
    
    @staticmethod
    def flasche_by_barcode_finden(barcode: str) -> Dict[str, Any]:
        """
        Findet Flasche anhand Barcode
        
        Args:
            barcode: Barcode der Flasche
        
        Returns:
            Dict mit Flasche oder Fehler
        """
        
        try:
            flasche = Flasche.query.filter_by(barcode=barcode.strip()).first()
            
            if not flasche:
                return {
                    'found': False,
                    'error': f'Keine Flasche mit Barcode {barcode} gefunden'
                }
            
            return {
                'found': True,
                'flasche': flasche.to_dict(include_besitzer=True),
                'kann_gefuellt_werden': flasche.ist_fuellbereit,
                'warnungen': [] if flasche.ist_fuellbereit else [flasche.pruefung_status_text]
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Barcode-Suche: {str(e)}")
            return {
                'found': False,
                'error': str(e)
            }
    
    @staticmethod
    def mehrere_flaschen_scannen(barcodes: List[str]) -> Dict[str, Any]:
        """
        Verarbeitet mehrere gescannte Barcodes
        
        Args:
            barcodes: Liste von Barcodes
        
        Returns:
            Dict mit Scan-Ergebnissen
        """
        
        try:
            gefundene_flaschen = []
            nicht_gefundene = []
            nicht_fuellbar = []
            
            for barcode in barcodes:
                result = FlaschenScanService.flasche_by_barcode_finden(barcode)
                
                if result['found']:
                    if result['kann_gefuellt_werden']:
                        gefundene_flaschen.append(result['flasche'])
                    else:
                        nicht_fuellbar.append({
                            'flasche': result['flasche'],
                            'grund': result['warnungen'][0] if result['warnungen'] else 'Unbekannt'
                        })
                else:
                    nicht_gefundene.append(barcode)
            
            return {
                'success': True,
                'gescannt': len(barcodes),
                'gefunden': len(gefundene_flaschen),
                'nicht_gefunden': len(nicht_gefundene),
                'nicht_fuellbar': len(nicht_fuellbar),
                'flaschen': gefundene_flaschen,
                'probleme': {
                    'nicht_gefundene_barcodes': nicht_gefundene,
                    'nicht_fuellbare_flaschen': nicht_fuellbar
                }
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Mehrfach-Scannen: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
