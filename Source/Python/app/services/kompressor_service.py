# Kompressor Service-Klassen für WartungsManager
# Geschäftslogik für Kompressor An/Aus Steuerung

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from app import db
from app.models import KompressorBetrieb, User

logger = logging.getLogger(__name__)

class KompressorService:
    """
    Service für Kompressor-Steuerung und Betriebsstunden-Management
    
    Funktionen:
    - Kompressor An/Aus schalten
    - Öl-Test Management
    - Betriebsstunden-Tracking
    - Statistiken und Berichte
    """
    
    @staticmethod
    def kompressor_einschalten(fueller: str, oel_getestet: bool = False, 
                              oel_test_ergebnis: str = None, oel_tester: str = None,
                              fueller_id: int = None, oel_tester_id: int = None) -> Dict[str, Any]:
        """
        Schaltet Kompressor ein und startet Betriebsstunden-Tracking
        
        Args:
            fueller: Name des Füller/Operators
            oel_getestet: Wurde Öl getestet?
            oel_test_ergebnis: 'OK' oder 'NOK'
            oel_tester: Name des Öl-Testers
            fueller_id: User-ID des Füllers
            oel_tester_id: User-ID des Öl-Testers
        
        Returns:
            Dict mit Ergebnis und Kompressor-Betrieb Daten
        """
        
        try:
            # Prüfe ob bereits ein Kompressor läuft
            aktiver_kompressor = KompressorBetrieb.get_aktiver_kompressor()
            if aktiver_kompressor:
                logger.warning(f"Kompressor bereits aktiv seit {aktiver_kompressor.start_zeit}")
                return {
                    'success': False,
                    'error': 'Kompressor läuft bereits',
                    'aktiver_kompressor': aktiver_kompressor.to_dict()
                }
            
            # Validierung der Öl-Test Daten
            if oel_getestet and not oel_test_ergebnis:
                return {
                    'success': False,
                    'error': 'Öl-Test Ergebnis muss angegeben werden wenn getestet wurde'
                }
            
            if oel_getestet and oel_test_ergebnis not in ['OK', 'NOK']:
                return {
                    'success': False,
                    'error': "Öl-Test Ergebnis muss 'OK' oder 'NOK' sein"
                }
            
            if oel_getestet and not oel_tester:
                return {
                    'success': False,
                    'error': 'Öl-Tester muss angegeben werden wenn getestet wurde'
                }
            
            # Neuen Kompressor-Betrieb erstellen
            kompressor_betrieb = KompressorBetrieb(
                fueller=fueller,
                fueller_id=fueller_id,
                oel_getestet=oel_getestet,
                oel_test_ergebnis=oel_test_ergebnis if oel_getestet else None,
                oel_tester=oel_tester if oel_getestet else None,
                oel_tester_id=oel_tester_id if oel_getestet else None,
                status='laufend'
            )
            
            db.session.add(kompressor_betrieb)
            db.session.commit()
            
            logger.info(f"Kompressor eingeschaltet von {fueller}, Öl-Test: {oel_getestet}")
            
            return {
                'success': True,
                'message': 'Kompressor erfolgreich eingeschaltet',
                'kompressor_betrieb': kompressor_betrieb.to_dict(),
                'betriebsstunden_gesamt': KompressorBetrieb.get_gesamt_betriebsstunden()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Einschalten des Kompressors: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler: {str(e)}'
            }
    
    @staticmethod
    def kompressor_ausschalten(notizen: str = None) -> Dict[str, Any]:
        """
        Schaltet Kompressor aus und beendet Betriebsstunden-Tracking
        
        Args:
            notizen: Optional Notizen zum Abschalten
        
        Returns:
            Dict mit Ergebnis und Betriebsdaten
        """
        
        try:
            # Aktuell laufenden Kompressor finden
            aktiver_kompressor = KompressorBetrieb.get_aktiver_kompressor()
            if not aktiver_kompressor:
                logger.warning("Kein aktiver Kompressor zum Ausschalten gefunden")
                return {
                    'success': False,
                    'error': 'Kein aktiver Kompressor gefunden'
                }
            
            # Kompressor ausschalten
            aktiver_kompressor.kompressor_ausschalten(notizen=notizen)
            db.session.commit()
            
            logger.info(f"Kompressor ausgeschaltet nach {aktiver_kompressor.betriebsdauer_stunden}h")
            
            return {
                'success': True,
                'message': 'Kompressor erfolgreich ausgeschaltet',
                'kompressor_betrieb': aktiver_kompressor.to_dict(),
                'betriebsdauer_stunden': aktiver_kompressor.betriebsdauer_stunden,
                'betriebsstunden_gesamt': KompressorBetrieb.get_gesamt_betriebsstunden()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Ausschalten des Kompressors: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler: {str(e)}'
            }
    
    @staticmethod
    def kompressor_notaus(grund: str = "Not-Aus Taste gedrückt") -> Dict[str, Any]:
        """
        Not-Aus des Kompressors
        
        Args:
            grund: Grund für den Not-Aus
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            aktiver_kompressor = KompressorBetrieb.get_aktiver_kompressor()
            if not aktiver_kompressor:
                return {
                    'success': False,
                    'error': 'Kein aktiver Kompressor für Not-Aus gefunden'
                }
            
            aktiver_kompressor.notaus(grund)
            db.session.commit()
            
            logger.warning(f"NOTAUS: {grund} - Kompressor gestoppt")
            
            return {
                'success': True,
                'message': f'Not-Aus ausgeführt: {grund}',
                'kompressor_betrieb': aktiver_kompressor.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Not-Aus: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler beim Not-Aus: {str(e)}'
            }
    
    @staticmethod
    def get_kompressor_status() -> Dict[str, Any]:
        """
        Gibt aktuellen Kompressor-Status zurück
        
        Returns:
            Dict mit Status-Informationen
        """
        
        try:
            aktiver_kompressor = KompressorBetrieb.get_aktiver_kompressor()
            statistiken = KompressorBetrieb.get_kompressor_statistiken()
            
            return {
                'ist_an': aktiver_kompressor is not None,
                'aktiver_kompressor': aktiver_kompressor.to_dict() if aktiver_kompressor else None,
                'statistiken': statistiken,
                'gesamt_betriebsstunden': KompressorBetrieb.get_gesamt_betriebsstunden()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Kompressor-Status: {str(e)}")
            return {
                'ist_an': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_betriebsstunden_report(tage: int = 30) -> Dict[str, Any]:
        """
        Erstellt Betriebsstunden-Report
        
        Args:
            tage: Anzahl Tage für den Report
        
        Returns:
            Dict mit Report-Daten
        """
        
        try:
            seit_datum = datetime.utcnow().date() - timedelta(days=tage)
            
            # Betriebsstunden seit Datum
            betriebsstunden_periode = KompressorBetrieb.get_betriebsstunden_seit(seit_datum)
            gesamt_betriebsstunden = KompressorBetrieb.get_gesamt_betriebsstunden()
            
            # Anzahl Starts in Periode
            starts_periode = KompressorBetrieb.query.filter(
                KompressorBetrieb.start_zeit >= seit_datum
            ).count()
            
            # Öl-Test Statistiken
            oel_stats = KompressorBetrieb.get_oel_test_statistiken()
            
            # Durchschnittliche Laufzeit
            avg_laufzeit = betriebsstunden_periode / starts_periode if starts_periode > 0 else 0
            
            return {
                'periode_tage': tage,
                'seit_datum': seit_datum.isoformat(),
                'betriebsstunden_periode': betriebsstunden_periode,
                'gesamt_betriebsstunden': gesamt_betriebsstunden,
                'starts_periode': starts_periode,
                'durchschnitt_laufzeit_stunden': round(avg_laufzeit, 2),
                'oel_statistiken': oel_stats
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Betriebsstunden-Reports: {str(e)}")
            return {
                'error': str(e)
            }
    
    @staticmethod
    def get_oel_test_reminder() -> Dict[str, Any]:
        """
        Prüft ob Öl-Tests regelmäßig durchgeführt werden
        
        Returns:
            Dict mit Erinnerungs-Informationen
        """
        
        try:
            # Letzte 10 Starts prüfen
            letzte_starts = KompressorBetrieb.query.order_by(
                KompressorBetrieb.start_zeit.desc()
            ).limit(10).all()
            
            if not letzte_starts:
                return {
                    'reminder_needed': False,
                    'message': 'Keine Kompressor-Starts gefunden'
                }
            
            # Prüfe Öl-Test Quote der letzten Starts
            getestete_starts = sum(1 for start in letzte_starts if start.oel_getestet)
            test_quote = (getestete_starts / len(letzte_starts)) * 100
            
            reminder_needed = test_quote < 80  # Weniger als 80% getestet
            
            return {
                'reminder_needed': reminder_needed,
                'letzte_10_starts': len(letzte_starts),
                'davon_oel_getestet': getestete_starts,
                'test_quote_prozent': round(test_quote, 1),
                'message': f'Öl-Test Quote: {test_quote:.1f}% - {"Erinnerung erforderlich" if reminder_needed else "Gut"}'
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Öl-Test Erinnerung: {str(e)}")
            return {
                'reminder_needed': True,
                'error': str(e)
            }
    
    @staticmethod
    def kompressor_reset_passwortgeschuetzt(passwort: str, grund: str = "Manueller Reset") -> Dict[str, Any]:
        """
        Setzt den aktuell laufenden Kompressor zurück (Reset auf 00:00:00)
        Erfordert Passwort: Magicfactory15!
        
        Args:
            passwort: Authentifizierungspasswort
            grund: Grund für den Reset
        
        Returns:
            Dict mit Reset-Ergebnis
        """
        
        # Passwort-Validierung
        RESET_PASSWORT = "Magicfactory15!"
        if passwort != RESET_PASSWORT:
            logger.warning(f"FEHLGESCHLAGENER RESET-VERSUCH: Falsches Passwort verwendet")
            return {
                'success': False,
                'error': 'Ungültiges Passwort für Reset-Funktion'
            }
        
        try:
            # Aktuell laufenden Kompressor finden
            aktiver_kompressor = KompressorBetrieb.get_aktiver_kompressor()
            if not aktiver_kompressor:
                logger.warning("RESET: Kein aktiver Kompressor zum Zurücksetzen gefunden")
                return {
                    'success': False,
                    'error': 'Kein aktiver Kompressor zum Zurücksetzen gefunden'
                }
            
            # Alte Start-Zeit für Protokoll speichern
            alte_startzeit = aktiver_kompressor.start_zeit
            alte_laufzeit_minuten = aktiver_kompressor.aktuelle_betriebsdauer
            
            # Reset: Start-Zeit auf jetzt setzen
            aktiver_kompressor.start_zeit = datetime.utcnow()
            aktiver_kompressor.notizen = aktiver_kompressor.notizen or ""
            aktiver_kompressor.notizen += f"\nRESET durchgeführt: {grund} (alte Laufzeit: {alte_laufzeit_minuten:.0f} min)"
            aktiver_kompressor.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"KOMPRESSOR RESET: Erfolgreich zurückgesetzt. Alte Laufzeit: {alte_laufzeit_minuten:.0f} min, Grund: {grund}")
            
            return {
                'success': True,
                'message': 'Kompressor erfolgreich zurückgesetzt',
                'reset_info': {
                    'alte_startzeit': alte_startzeit.isoformat(),
                    'alte_laufzeit_minuten': round(alte_laufzeit_minuten, 1),
                    'neue_startzeit': aktiver_kompressor.start_zeit.isoformat(),
                    'grund': grund
                },
                'kompressor_betrieb': aktiver_kompressor.to_dict()
            }
            
        except Exception as e:
            logger.error(f"FEHLER beim Kompressor-Reset: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler beim Reset: {str(e)}'
            }
    
    @staticmethod
    def validate_oel_test_data(oel_getestet: bool, oel_test_ergebnis: str = None, 
                              oel_tester: str = None) -> Dict[str, Any]:
        """
        Validiert Öl-Test Daten
        
        Returns:
            Dict mit Validierungs-Ergebnis
        """
        
        errors = []
        
        if oel_getestet:
            if not oel_test_ergebnis:
                errors.append("Öl-Test Ergebnis muss angegeben werden")
            elif oel_test_ergebnis not in ['OK', 'NOK']:
                errors.append("Öl-Test Ergebnis muss 'OK' oder 'NOK' sein")
            
            if not oel_tester or len(oel_tester.strip()) == 0:
                errors.append("Öl-Tester Name muss angegeben werden")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

class KompressorScheduleService:
    """
    Service für geplante Kompressor-Wartungen und Erinnerungen
    """
    
    @staticmethod
    def check_wartung_faellig() -> Dict[str, Any]:
        """
        Prüft ob Kompressor-Wartung fällig ist
        
        Returns:
            Dict mit Wartungs-Status
        """
        
        try:
            gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
            
            # Standard-Wartungsintervall: alle 100 Stunden
            wartungsintervall = 100
            naechste_wartung_bei = (int(gesamt_stunden / wartungsintervall) + 1) * wartungsintervall
            stunden_bis_wartung = naechste_wartung_bei - gesamt_stunden
            
            wartung_faellig = stunden_bis_wartung <= 10  # Warnung bei 10h vor Wartung
            
            return {
                'wartung_faellig': wartung_faellig,
                'gesamt_betriebsstunden': gesamt_stunden,
                'naechste_wartung_bei': naechste_wartung_bei,
                'stunden_bis_wartung': round(stunden_bis_wartung, 1),
                'wartungsintervall': wartungsintervall
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Wartungs-Check: {str(e)}")
            return {
                'wartung_faellig': True,  # Im Fehlerfall: sicher ist sicher
                'error': str(e)
            }
