# Intelligenter Kunden-Service mit verbesserter Suche und Verwaltung
# Erstellt von Hans Hahn - Alle Rechte vorbehalten
# Datum: 04.07.2025

from app import db
from app.models.kunden import Kunde
from app.models.flaschen import Flasche
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func
import re
from difflib import SequenceMatcher

class IntelligenterKundenService:
    """
    Erweiterter Service für intelligente Kundensuche und -verwaltung
    
    Features:
    - Fuzzy-Suche mit Tippfehler-Toleranz
    - Priorisierung nach Aktivität
    - Quick-Create für schnelle Kundenanlage
    - Duplikat-Erkennung
    - Flaschen-Verknüpfung
    """
    
    @staticmethod
    def intelligente_suche(suchbegriff, limit=10, min_score=0.5):
        """
        Intelligente Kundensuche mit Fuzzy-Matching
        
        Args:
            suchbegriff: Suchstring
            limit: Maximale Anzahl Ergebnisse
            min_score: Minimale Ähnlichkeit (0-1)
            
        Returns:
            Liste von Kunden mit Relevanz-Score
        """
        if not suchbegriff or len(suchbegriff.strip()) == 0:
            return []
            
        suchbegriff = suchbegriff.strip().lower()
        alle_kunden = Kunde.query.filter_by(ist_aktiv=True).all()
        
        ergebnisse = []
        
        for kunde in alle_kunden:
            # Berechne Ähnlichkeits-Scores für verschiedene Felder
            scores = []
            
            # Vollname
            vollname = f"{kunde.vorname} {kunde.nachname or ''}".lower().strip()
            scores.append(SequenceMatcher(None, suchbegriff, vollname).ratio())
            
            # Nur Vorname
            scores.append(SequenceMatcher(None, suchbegriff, kunde.vorname.lower()).ratio())
            
            # Nur Nachname
            if kunde.nachname:
                scores.append(SequenceMatcher(None, suchbegriff, kunde.nachname.lower()).ratio())
            
            # Mitgliedsnummer
            if kunde.mitgliedsnummer:
                scores.append(SequenceMatcher(None, suchbegriff, kunde.mitgliedsnummer.lower()).ratio())
            
            # Externe Nummer
            if kunde.externe_kundennummer:
                scores.append(SequenceMatcher(None, suchbegriff, kunde.externe_kundennummer.lower()).ratio())
            
            # Telefon (ohne Formatierung)
            if kunde.telefon:
                telefon_clean = re.sub(r'[^\d]', '', kunde.telefon)
                suchbegriff_clean = re.sub(r'[^\d]', '', suchbegriff)
                if suchbegriff_clean:
                    scores.append(SequenceMatcher(None, suchbegriff_clean, telefon_clean).ratio())
            
            # Email
            if kunde.email:
                scores.append(SequenceMatcher(None, suchbegriff, kunde.email.lower()).ratio())
            
            # Firma
            if kunde.firma:
                scores.append(SequenceMatcher(None, suchbegriff, kunde.firma.lower()).ratio() * 0.8)  # Etwas niedriger gewichtet
            
            # Höchster Score zählt
            max_score = max(scores) if scores else 0
            
            # Bonus für kürzlich aktive Kunden
            if hasattr(kunde, 'letzter_besuch') and kunde.letzter_besuch:
                tage_seit_besuch = (datetime.utcnow() - kunde.letzter_besuch).days
                if tage_seit_besuch < 30:
                    max_score += 0.1  # 10% Bonus für Aktivität in letzten 30 Tagen
                elif tage_seit_besuch < 90:
                    max_score += 0.05  # 5% Bonus für Aktivität in letzten 90 Tagen
            
            # Bonus für Stammkunden
            if hasattr(kunde, 'stammkunde') and kunde.stammkunde:
                max_score += 0.05
            
            if max_score >= min_score:
                ergebnisse.append({
                    'kunde': kunde,
                    'score': min(max_score, 1.0),  # Cap bei 1.0
                    'match_type': IntelligenterKundenService._bestimme_match_typ(kunde, suchbegriff, scores)
                })
        
        # Sortiere nach Score (höchste zuerst)
        ergebnisse.sort(key=lambda x: x['score'], reverse=True)
        
        # Limitiere Ergebnisse
        return ergebnisse[:limit]
    
    @staticmethod
    def _bestimme_match_typ(kunde, suchbegriff, scores):
        """Bestimmt, wo der beste Match gefunden wurde"""
        vollname = f"{kunde.vorname} {kunde.nachname or ''}".lower().strip()
        
        if vollname == suchbegriff:
            return "Exakte Übereinstimmung"
        elif kunde.vorname.lower() == suchbegriff:
            return "Vorname"
        elif kunde.nachname and kunde.nachname.lower() == suchbegriff:
            return "Nachname"
        elif kunde.mitgliedsnummer and kunde.mitgliedsnummer.lower() == suchbegriff:
            return "Mitgliedsnummer"
        elif kunde.externe_kundennummer and kunde.externe_kundennummer.lower() == suchbegriff:
            return "Externe Nummer"
        else:
            return "Teilübereinstimmung"
    
    @staticmethod
    def quick_kunde_anlegen(vorname, nachname=None, telefon=None, externe_nummer=None):
        """
        Schnelles Anlegen eines Kunden mit minimalen Daten
        
        Args:
            vorname: Pflichtfeld
            nachname: Optional
            telefon: Optional
            externe_nummer: Optional
            
        Returns:
            Dict mit Kunde und Status
        """
        if not vorname or not vorname.strip():
            return {
                'success': False,
                'error': 'Vorname ist erforderlich'
            }
        
        vorname = vorname.strip()
        nachname = nachname.strip() if nachname else ''
        
        # Prüfe auf mögliche Duplikate
        duplikate = IntelligenterKundenService.pruefe_duplikate(
            vorname=vorname,
            nachname=nachname,
            telefon=telefon
        )
        
        if duplikate:
            return {
                'success': False,
                'error': 'Mögliches Duplikat gefunden',
                'duplikate': duplikate
            }
        
        try:
            # Generiere Mitgliedsnummer
            mitgliedsnummer = Kunde.get_naechste_mitgliedsnummer()
            
            # Erstelle Kunde
            neuer_kunde = Kunde(
                mitgliedsnummer=mitgliedsnummer,
                vorname=vorname,
                nachname=nachname,
                telefon=telefon,
                externe_kundennummer=externe_nummer,
                externe_system='Quick-Create' if externe_nummer else None,
                mitglied_seit=datetime.utcnow().date(),
                erstellt_am=datetime.utcnow()
            )
            
            # Setze letzten Besuch auf jetzt
            if hasattr(neuer_kunde, 'letzter_besuch'):
                neuer_kunde.letzter_besuch = datetime.utcnow()
            
            db.session.add(neuer_kunde)
            db.session.commit()
            
            return {
                'success': True,
                'kunde': neuer_kunde,
                'message': f'Kunde {vollname} erfolgreich angelegt (Nr: {mitgliedsnummer})'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler beim Anlegen: {str(e)}'
            }
    
    @staticmethod
    def pruefe_duplikate(vorname, nachname=None, telefon=None, email=None):
        """
        Prüft auf mögliche Duplikate
        
        Returns:
            Liste möglicher Duplikate
        """
        duplikate = []
        
        # Exakte Namensübereinstimmung
        if vorname and nachname:
            exact_match = Kunde.query.filter_by(
                vorname=vorname,
                nachname=nachname
            ).first()
            if exact_match:
                duplikate.append({
                    'kunde': exact_match,
                    'grund': 'Exakter Name'
                })
        
        # Telefonnummer (falls vorhanden)
        if telefon:
            telefon_clean = re.sub(r'[^\d]', '', telefon)
            if telefon_clean:
                # Suche nach ähnlichen Telefonnummern
                alle_kunden = Kunde.query.filter(Kunde.telefon.isnot(None)).all()
                for kunde in alle_kunden:
                    kunde_telefon_clean = re.sub(r'[^\d]', '', kunde.telefon)
                    if telefon_clean == kunde_telefon_clean:
                        duplikate.append({
                            'kunde': kunde,
                            'grund': 'Gleiche Telefonnummer'
                        })
        
        # Email (falls vorhanden)
        if email:
            email_match = Kunde.query.filter_by(email=email).first()
            if email_match:
                duplikate.append({
                    'kunde': email_match,
                    'grund': 'Gleiche Email'
                })
        
        # Entferne Duplikate aus der Liste
        seen = set()
        unique_duplikate = []
        for dup in duplikate:
            if dup['kunde'].id not in seen:
                seen.add(dup['kunde'].id)
                unique_duplikate.append(dup)
        
        return unique_duplikate
    
    @staticmethod
    def kunde_mit_flaschen_verknuepfen(kunde_id, flasche_ids):
        """
        Verknüpft einen Kunden mit mehreren Flaschen
        
        Args:
            kunde_id: ID des Kunden
            flasche_ids: Liste von Flaschen-IDs
            
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
            
            verknuepfte = []
            fehler = []
            
            for flasche_id in flasche_ids:
                flasche = Flasche.query.get(flasche_id)
                if not flasche:
                    fehler.append(f'Flasche {flasche_id} nicht gefunden')
                    continue
                
                # Prüfe ob Flasche bereits einem anderen Kunden gehört
                if flasche.kunde_id and flasche.kunde_id != kunde_id:
                    alter_kunde = Kunde.query.get(flasche.kunde_id)
                    fehler.append(
                        f'Flasche {flasche.flasche_nummer} gehört bereits {alter_kunde.vollname}'
                    )
                    continue
                
                # Verknüpfe Flasche
                flasche.kunde_id = kunde_id
                verknuepfte.append(flasche.flasche_nummer)
            
            # Aktualisiere letzten Besuch
            if hasattr(kunde, 'letzter_besuch'):
                kunde.letzter_besuch = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'verknuepfte': verknuepfte,
                'fehler': fehler,
                'message': f'{len(verknuepfte)} Flaschen verknüpft'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler beim Verknüpfen: {str(e)}'
            }
    
    @staticmethod
    def hole_kunden_flaschen(kunde_id, nur_aktive=True):
        """
        Holt alle Flaschen eines Kunden
        
        Args:
            kunde_id: ID des Kunden
            nur_aktive: Nur aktive Flaschen anzeigen
            
        Returns:
            Liste von Flaschen mit Status
        """
        try:
            kunde = Kunde.query.get(kunde_id)
            if not kunde:
                return []
            
            query = kunde.flaschen
            if nur_aktive:
                query = query.filter_by(ist_aktiv=True)
            
            flaschen = query.all()
            
            # Erweitere mit Status-Informationen
            flaschen_mit_status = []
            for flasche in flaschen:
                # Prüfe ob in Warteliste
                from app.models.warteliste import Warteliste
                in_warteliste = Warteliste.query.filter_by(
                    flasche_id=flasche.id,
                    status='wartend'
                ).first()
                
                flaschen_mit_status.append({
                    'flasche': flasche,
                    'status': 'In Warteliste' if in_warteliste else 'Beim Kunden',
                    'pruefung_status': flasche.pruefung_status_text,
                    'ist_fuellbereit': flasche.ist_fuellbereit
                })
            
            return flaschen_mit_status
            
        except Exception as e:
            print(f'Fehler beim Laden der Flaschen: {str(e)}')
            return []
    
    @staticmethod
    def aktualisiere_letzten_besuch(kunde_id):
        """Aktualisiert den letzten Besuch eines Kunden"""
        try:
            kunde = Kunde.query.get(kunde_id)
            if kunde and hasattr(kunde, 'letzter_besuch'):
                kunde.letzter_besuch = datetime.utcnow()
                db.session.commit()
                return True
        except:
            db.session.rollback()
        return False
    
    @staticmethod
    def hole_favoriten_kunden(limit=10):
        """
        Holt die am häufigsten aktiven Kunden
        
        Returns:
            Liste der Top-Kunden
        """
        try:
            # Basiere auf letztem Besuch wenn verfügbar
            query = Kunde.query.filter_by(ist_aktiv=True)
            
            # Sortiere nach letztem Besuch oder Erstelldatum
            if hasattr(Kunde, 'letzter_besuch'):
                kunden = query.order_by(Kunde.letzter_besuch.desc().nullslast()).limit(limit).all()
            else:
                # Fallback: Neueste zuerst
                kunden = query.order_by(Kunde.erstellt_am.desc()).limit(limit).all()
            
            return kunden
            
        except Exception as e:
            print(f'Fehler beim Laden der Favoriten: {str(e)}')
            return []
    
    @staticmethod
    def statistiken_fuer_kunde(kunde_id):
        """
        Erstellt detaillierte Statistiken für einen Kunden
        
        Returns:
            Dict mit Statistiken
        """
        try:
            kunde = Kunde.query.get(kunde_id)
            if not kunde:
                return None
            
            # Basis-Statistiken
            stats = {
                'anzahl_flaschen': kunde.anzahl_flaschen,
                'aktive_flaschen': kunde.aktive_flaschen.count(),
                'mitglied_seit_tagen': (datetime.utcnow().date() - kunde.mitglied_seit).days,
                'mitgliedschaft_jahre': kunde.mitgliedschaft_dauer_jahre
            }
            
            # Füllungen (aus Warteliste/Archiv)
            from app.models.warteliste import Warteliste
            from app.models.fuelling import FuellingEintrag
            
            # Anzahl Füllungen
            fuellungen = FuellingEintrag.query.join(Flasche).filter(
                Flasche.kunde_id == kunde_id
            ).count()
            stats['anzahl_fuellungen'] = fuellungen
            
            # Letzte Füllung
            letzte_fuellung = FuellingEintrag.query.join(Flasche).filter(
                Flasche.kunde_id == kunde_id
            ).order_by(FuellingEintrag.erstellt_am.desc()).first()
            
            if letzte_fuellung:
                stats['letzte_fuellung'] = letzte_fuellung.erstellt_am
                stats['tage_seit_letzter_fuellung'] = (
                    datetime.utcnow() - letzte_fuellung.erstellt_am
                ).days
            else:
                stats['letzte_fuellung'] = None
                stats['tage_seit_letzter_fuellung'] = None
            
            # Prüfungen fällig
            pruefungen_faellig = 0
            for flasche in kunde.aktive_flaschen:
                if flasche.pruefung_faellig:
                    pruefungen_faellig += 1
            stats['pruefungen_faellig'] = pruefungen_faellig
            
            return stats
            
        except Exception as e:
            print(f'Fehler bei Statistiken: {str(e)}')
            return None
