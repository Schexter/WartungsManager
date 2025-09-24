# Wartungsintervall Service für WartungsManager
# Geschäftslogik für Wartungsintervall-Management

from datetime import datetime
from typing import Dict, Any, Optional
import logging
from app import db
from app.models.wartungsintervall import Wartungsintervall
from app.models.kompressor import KompressorBetrieb

logger = logging.getLogger(__name__)

class WartungsintervallService:
    """
    Service für Wartungsintervall-Management
    
    Funktionen:
    - Wartungsintervall nach Patronenwechsel zurücksetzen
    - Getrennte Verwaltung von Gesamt-Betriebszeit und Wartungsintervall
    - Wartungserinnerungen und Statistiken
    """
    
    @staticmethod
    def intervall_reset_patronenwechsel(passwort: str, durchgefuehrt_von: str, 
                                       wartungsintervall_stunden: float = 100.0,
                                       notizen: str = None) -> Dict[str, Any]:
        """
        Setzt Wartungsintervall nach Patronenwechsel zurück
        
        Args:
            passwort: Authentifizierungspasswort
            durchgefuehrt_von: Wer hat den Patronenwechsel durchgeführt
            wartungsintervall_stunden: Stunden bis zur nächsten Wartung
            notizen: Zusätzliche Notizen
        
        Returns:
            Dict mit Reset-Ergebnis
        """
        
        # Passwort-Validierung
        WARTUNGS_PASSWORT = "Magicfactory15!"
        if passwort != WARTUNGS_PASSWORT:
            logger.warning(f"FEHLGESCHLAGENER WARTUNGSINTERVALL-RESET: Falsches Passwort von {durchgefuehrt_von}")
            return {
                'success': False,
                'error': 'Ungültiges Passwort für Wartungsintervall-Reset'
            }
        
        try:
            # Aktuelles Intervall für Protokoll
            altes_intervall = Wartungsintervall.get_aktuelles_intervall()
            alte_intervall_stunden = altes_intervall.intervall_betriebsstunden if altes_intervall else 0.0
            
            # Gesamt-Betriebszeit für Dokumentation
            gesamt_betriebszeit = KompressorBetrieb.get_gesamt_betriebsstunden()
            
            # Neues Wartungsintervall starten
            grund = f"Patronenwechsel nach {alte_intervall_stunden:.1f}h Betrieb"
            if notizen:
                grund += f" - {notizen}"
            
            neues_intervall = Wartungsintervall.neues_intervall_starten(
                name="Patronenwechsel",
                grund=grund,
                wartungsintervall_stunden=wartungsintervall_stunden,
                durchgefuehrt_von=durchgefuehrt_von
            )
            
            if notizen:
                neues_intervall.notizen = notizen
                db.session.commit()
            
            logger.info(f"WARTUNGSINTERVALL RESET: Patronenwechsel durchgeführt von {durchgefuehrt_von}, alte Intervall-Zeit: {alte_intervall_stunden:.1f}h")
            
            return {
                'success': True,
                'message': 'Wartungsintervall erfolgreich zurückgesetzt',
                'reset_info': {
                    'alte_intervall_stunden': alte_intervall_stunden,
                    'gesamt_betriebszeit_unveraendert': gesamt_betriebszeit,
                    'neues_wartungsintervall': wartungsintervall_stunden,
                    'durchgefuehrt_von': durchgefuehrt_von,
                    'grund': grund
                },
                'neues_intervall': neues_intervall.to_dict()
            }
            
        except Exception as e:
            logger.error(f"FEHLER beim Wartungsintervall-Reset: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler beim Wartungsintervall-Reset: {str(e)}'
            }
    
    @staticmethod
    def gesamt_betriebszeit_korrigieren(passwort: str, neue_gesamt_stunden: float,
                                       grund: str = "Korrektur der Gesamt-Betriebszeit") -> Dict[str, Any]:
        """
        Korrigiert die Gesamt-Betriebszeit des Kompressors (einmalige Korrektur)
        
        Args:
            passwort: Authentifizierungspasswort
            neue_gesamt_stunden: Korrekte Gesamt-Betriebsstunden (z.B. 246h)
            grund: Grund für die Korrektur
        
        Returns:
            Dict mit Korrektur-Ergebnis
        """
        
        # Passwort-Validierung
        WARTUNGS_PASSWORT = "Magicfactory15!"
        if passwort != WARTUNGS_PASSWORT:
            logger.warning(f"FEHLGESCHLAGENE GESAMT-STUNDEN KORREKTUR: Falsches Passwort")
            return {
                'success': False,
                'error': 'Ungültiges Passwort für Gesamt-Betriebszeit Korrektur'
            }
        
        try:
            # Aktuelle Berechnung
            aktuelle_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
            differenz = neue_gesamt_stunden - aktuelle_stunden
            
            if abs(differenz) < 0.1:  # Weniger als 0.1h Differenz
                return {
                    'success': True,
                    'message': 'Gesamt-Betriebszeit ist bereits korrekt',
                    'aktuelle_stunden': aktuelle_stunden,
                    'ziel_stunden': neue_gesamt_stunden
                }
            
            # Korrektur-Eintrag erstellen
            korrektur_minuten = int(differenz * 60)
            
            if korrektur_minuten > 0:
                # Positive Korrektur: Zusätzliche Betriebszeit hinzufügen
                korrektur_eintrag = KompressorBetrieb(
                    fueller="SYSTEM_KORREKTUR",
                    start_zeit=datetime.utcnow() - timedelta(minutes=korrektur_minuten),
                    end_zeit=datetime.utcnow(),
                    betriebsdauer_minuten=korrektur_minuten,
                    status='beendet',
                    oel_getestet=False,
                    notizen=f"KORREKTUR: {grund} - Differenz: +{differenz:.1f}h"
                )
            else:
                # Negative Korrektur: Abzug durch negativen Eintrag
                korrektur_eintrag = KompressorBetrieb(
                    fueller="SYSTEM_KORREKTUR",
                    start_zeit=datetime.utcnow(),
                    end_zeit=datetime.utcnow(),
                    betriebsdauer_minuten=korrektur_minuten,  # Negativ
                    status='beendet',
                    oel_getestet=False,
                    notizen=f"KORREKTUR: {grund} - Differenz: {differenz:.1f}h"
                )
            
            db.session.add(korrektur_eintrag)
            db.session.commit()
            
            # Prüfung nach Korrektur
            neue_berechnung = KompressorBetrieb.get_gesamt_betriebsstunden()
            
            logger.info(f"GESAMT-BETRIEBSZEIT KORRIGIERT: {aktuelle_stunden:.1f}h → {neue_berechnung:.1f}h (Ziel: {neue_gesamt_stunden:.1f}h)")
            
            return {
                'success': True,
                'message': 'Gesamt-Betriebszeit erfolgreich korrigiert',
                'korrektur_info': {
                    'alte_stunden': aktuelle_stunden,
                    'neue_stunden': neue_berechnung,
                    'ziel_stunden': neue_gesamt_stunden,
                    'differenz': differenz,
                    'grund': grund
                }
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Gesamt-Betriebszeit Korrektur: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler bei Korrektur: {str(e)}'
            }
    
    @staticmethod
    def get_wartungsintervall_status() -> Dict[str, Any]:
        """
        Gibt aktuellen Wartungsintervall-Status zurück
        
        Returns:
            Dict mit Wartungsintervall-Informationen
        """
        
        try:
            # Wartungsintervall-Statistiken
            wartung_stats = Wartungsintervall.get_wartungsstatistiken()
            
            # Gesamt-Betriebszeit
            gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
            
            # Kompressor-Status
            aktiver_kompressor = KompressorBetrieb.get_aktiver_kompressor()
            
            return {
                'gesamt_betriebszeit': gesamt_stunden,
                'wartungsintervall': wartung_stats,
                'kompressor_aktiv': aktiver_kompressor is not None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Wartungsintervall-Status: {str(e)}")
            return {
                'error': str(e),
                'gesamt_betriebszeit': 0.0,
                'wartungsintervall': {'hat_intervall': False}
            }
    
    @staticmethod
    def erstelle_standard_wartungsintervall(gesamt_stunden: float = 246.0) -> Dict[str, Any]:
        """
        Erstellt Standard-Wartungsintervall wenn noch keines existiert
        
        Args:
            gesamt_stunden: Aktuelle Gesamt-Betriebszeit des Kompressors
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            # Prüfe ob bereits ein Intervall existiert
            aktuelles = Wartungsintervall.get_aktuelles_intervall()
            if aktuelles:
                return {
                    'success': True,
                    'message': 'Wartungsintervall existiert bereits',
                    'intervall': aktuelles.to_dict()
                }
            
            # Standard-Intervall erstellen
            intervall = Wartungsintervall(
                name="Initial Setup",
                reset_grund=f"Initiales Wartungsintervall bei {gesamt_stunden}h Gesamt-Betriebszeit",
                startstand_stunden=gesamt_stunden,
                wartungsintervall_stunden=100.0,
                naechste_wartung_bei=gesamt_stunden + 100.0,
                durchgefuehrt_von="SYSTEM_SETUP",
                ist_aktiv=True,
                notizen="Automatisch erstelltes Standard-Wartungsintervall"
            )
            
            db.session.add(intervall)
            db.session.commit()
            
            logger.info(f"Standard-Wartungsintervall erstellt bei {gesamt_stunden}h Gesamt-Betriebszeit")
            
            return {
                'success': True,
                'message': 'Standard-Wartungsintervall erfolgreich erstellt',
                'intervall': intervall.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Standard-Wartungsintervalls: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler beim Erstellen: {str(e)}'
            }

# Hilfsfunktionen für Import
from datetime import timedelta
