# Patronenwechsel Service für WartungsManager
# Geschäftslogik für Patronenwechsel-Management

from datetime import datetime
from typing import Dict, Any, Optional
import logging
from app import db
from app.models.patronenwechsel import Patronenwechsel, PatronenwechselKonfiguration
from app.models.kompressor import KompressorBetrieb

logger = logging.getLogger(__name__)

class PatronenwechselService:
    """
    Service für Patronenwechsel-Management
    
    Funktionen:
    - Patronenwechsel durchführen und dokumentieren
    - Konfigurierbares Wechselintervall (Standard: 12h)
    - Countdown bis zum nächsten Wechsel
    - Verwaltung von Molekularsieb und Kohle-Filter
    """
    
    @staticmethod
    def patronenwechsel_durchfuehren(passwort: str, durchgefuehrt_von: str,
                                    wechsel_datum: str = None,
                                    molekularsieb_1: bool = True,
                                    molekularsieb_2: bool = True,
                                    kohle_filter: bool = True,
                                    mol_1_charge: str = None,
                                    mol_2_charge: str = None,
                                    kohle_charge: str = None,
                                    alte_mol_1: str = None,
                                    alte_mol_2: str = None,
                                    alte_kohle: str = None,
                                    notizen: str = None) -> Dict[str, Any]:
        """
        Führt einen Patronenwechsel durch und dokumentiert ihn
        
        Args:
            passwort: Authentifizierungspasswort
            durchgefuehrt_von: Wer führt den Wechsel durch
            wechsel_datum: Datum des Wechsels (optional, default: jetzt)
            molekularsieb_1/2: Ob Patrone gewechselt wurde
            kohle_filter: Ob Kohle-Filter gewechselt wurde
            *_charge: Chargennummern der neuen Patronen
            alte_*: Chargennummern der entfernten Patronen
            notizen: Zusätzliche Notizen
        
        Returns:
            Dict mit Ergebnis
        """
        
        # Passwort-Validierung
        WARTUNGS_PASSWORT = "Magicfactory15!"
        if passwort != WARTUNGS_PASSWORT:
            logger.warning(f"FEHLGESCHLAGENER PATRONENWECHSEL: Falsches Passwort von {durchgefuehrt_von}")
            return {
                'success': False,
                'error': 'Ungültiges Passwort für Patronenwechsel'
            }
        
        try:
            # Wechsel-Datum parsen
            if wechsel_datum:
                try:
                    wechsel_datum_obj = datetime.fromisoformat(wechsel_datum.replace('Z', '+00:00'))
                except:
                    wechsel_datum_obj = datetime.utcnow()
            else:
                wechsel_datum_obj = datetime.utcnow()
            
            # Status vor Wechsel für Protokoll
            alter_status = Patronenwechsel.get_patronenwechsel_status()
            
            # Neuen Patronenwechsel erstellen
            neuer_wechsel = Patronenwechsel.neuer_patronenwechsel(
                durchgefuehrt_von=durchgefuehrt_von,
                wechsel_datum=wechsel_datum_obj,
                molekularsieb_1=molekularsieb_1,
                molekularsieb_2=molekularsieb_2,
                kohle_filter=kohle_filter,
                mol_1_charge=mol_1_charge,
                mol_2_charge=mol_2_charge,
                kohle_charge=kohle_charge,
                alte_mol_1=alte_mol_1,
                alte_mol_2=alte_mol_2,
                alte_kohle=alte_kohle,
                notizen=notizen
            )
            
            # Anzahl gewechselter Patronen
            gewechselte_patronen = []
            if molekularsieb_1:
                gewechselte_patronen.append("Molekularsieb Patrone 1")
            if molekularsieb_2:
                gewechselte_patronen.append("Molekularsieb Patrone 2")
            if kohle_filter:
                gewechselte_patronen.append("Kohle Filter")
            
            logger.info(f"PATRONENWECHSEL DURCHGEFÜHRT: {durchgefuehrt_von}, Patronen: {', '.join(gewechselte_patronen)}, Betriebsstunden: {neuer_wechsel.betriebsstunden_bei_wechsel}h")
            
            return {
                'success': True,
                'message': 'Patronenwechsel erfolgreich durchgeführt',
                'patronenwechsel': neuer_wechsel.to_dict(),
                'gewechselte_patronen': gewechselte_patronen,
                'alter_status': alter_status,
                'neuer_status': Patronenwechsel.get_patronenwechsel_status()
            }
            
        except Exception as e:
            logger.error(f"FEHLER beim Patronenwechsel: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler beim Patronenwechsel: {str(e)}'
            }
    
    @staticmethod
    def konfiguration_aktualisieren(passwort: str, 
                                   patronenwechsel_intervall_stunden: float,
                                   warnung_vor_stunden: float = 2.0,
                                   erstellt_von: str = "Benutzer") -> Dict[str, Any]:
        """
        Aktualisiert die Patronenwechsel-Konfiguration
        
        Args:
            passwort: Authentifizierungspasswort
            patronenwechsel_intervall_stunden: Neues Intervall (z.B. 12.0)
            warnung_vor_stunden: Warnung X Stunden vorher
            erstellt_von: Wer hat die Konfiguration geändert
        
        Returns:
            Dict mit Ergebnis
        """
        
        # Passwort-Validierung
        WARTUNGS_PASSWORT = "Magicfactory15!"
        if passwort != WARTUNGS_PASSWORT:
            logger.warning(f"FEHLGESCHLAGENE KONFIGURATION: Falsches Passwort von {erstellt_von}")
            return {
                'success': False,
                'error': 'Ungültiges Passwort für Konfiguration'
            }
        
        try:
            # Alte Konfiguration deaktivieren
            alte_config = PatronenwechselKonfiguration.get_aktuelle_konfiguration()
            if alte_config:
                alte_config.ist_aktiv = False
            
            # Neue Konfiguration erstellen
            neue_config = PatronenwechselKonfiguration(
                patronenwechsel_intervall_stunden=patronenwechsel_intervall_stunden,
                warnung_vor_stunden=warnung_vor_stunden,
                erstellt_von=erstellt_von,
                ist_aktiv=True
            )
            
            db.session.add(neue_config)
            db.session.commit()
            
            logger.info(f"PATRONENWECHSEL-KONFIGURATION AKTUALISIERT: {patronenwechsel_intervall_stunden}h Intervall von {erstellt_von}")
            
            return {
                'success': True,
                'message': 'Patronenwechsel-Konfiguration erfolgreich aktualisiert',
                'alte_konfiguration': {
                    'intervall_stunden': alte_config.patronenwechsel_intervall_stunden if alte_config else 12.0,
                    'warnung_vor_stunden': alte_config.warnung_vor_stunden if alte_config else 2.0
                },
                'neue_konfiguration': {
                    'intervall_stunden': neue_config.patronenwechsel_intervall_stunden,
                    'warnung_vor_stunden': neue_config.warnung_vor_stunden,
                    'erstellt_von': neue_config.erstellt_von
                }
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Konfiguration: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler bei Konfiguration: {str(e)}'
            }
    
    @staticmethod
    def get_patronenwechsel_dashboard_status() -> Dict[str, Any]:
        """
        Gibt Patronenwechsel-Status für Dashboard zurück
        
        Returns:
            Dict mit Dashboard-Informationen
        """
        
        try:
            status = Patronenwechsel.get_patronenwechsel_status()
            gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
            
            # Dashboard-spezifische Aufbereitung
            countdown_text = "Bereit"
            countdown_class = "text-success"
            
            if status['wechsel_faellig']:
                countdown_text = "WECHSEL FÄLLIG!"
                countdown_class = "text-danger"
            elif status['warnung_aktiv']:
                stunden_bis = status['stunden_bis_wechsel']
                countdown_text = f"Wechsel in {stunden_bis:.1f}h"
                countdown_class = "text-warning"
            else:
                stunden_bis = status['stunden_bis_wechsel']
                countdown_text = f"Nächster Wechsel in {stunden_bis:.1f}h"
                countdown_class = "text-success"
            
            # Patronenwechsel-Historie (letzte 5)
            letzte_wechsel = Patronenwechsel.query.order_by(
                Patronenwechsel.wechsel_datum.desc()
            ).limit(5).all()
            
            return {
                'countdown_text': countdown_text,
                'countdown_class': countdown_class,
                'stunden_bis_wechsel': status['stunden_bis_wechsel'],
                'wechsel_faellig': status['wechsel_faellig'],
                'warnung_aktiv': status['warnung_aktiv'],
                'konfiguration': status['konfiguration'],
                'gesamt_betriebsstunden': gesamt_stunden,
                'letzte_wechsel': [w.to_dict() for w in letzte_wechsel],
                'status_details': status
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Dashboard-Status: {str(e)}")
            return {
                'countdown_text': "Fehler",
                'countdown_class': "text-danger",
                'stunden_bis_wechsel': 0.0,
                'wechsel_faellig': True,
                'warnung_aktiv': True,
                'error': str(e)
            }
    
    @staticmethod
    def get_patronenwechsel_historie(limit: int = 20) -> Dict[str, Any]:
        """
        Gibt Patronenwechsel-Historie zurück
        
        Args:
            limit: Anzahl der zurückzugebenden Einträge
        
        Returns:
            Dict mit Historie-Daten
        """
        
        try:
            wechsel = Patronenwechsel.query.order_by(
                Patronenwechsel.wechsel_datum.desc()
            ).limit(limit).all()
            
            config = PatronenwechselKonfiguration.get_aktuelle_konfiguration()
            
            # Statistiken berechnen
            total_wechsel = Patronenwechsel.query.count()
            
            if wechsel:
                erster_wechsel = Patronenwechsel.query.order_by(
                    Patronenwechsel.wechsel_datum.asc()
                ).first()
                
                letzter_wechsel = wechsel[0]
                
                # Durchschnittliches Wechselintervall
                if total_wechsel > 1:
                    zeitspanne = letzter_wechsel.wechsel_datum - erster_wechsel.wechsel_datum
                    avg_intervall_tage = zeitspanne.days / (total_wechsel - 1)
                else:
                    avg_intervall_tage = 0
            else:
                avg_intervall_tage = 0
                letzter_wechsel = None
            
            return {
                'success': True,
                'patronenwechsel': [w.to_dict() for w in wechsel],
                'statistiken': {
                    'total_wechsel': total_wechsel,
                    'letzter_wechsel': letzter_wechsel.to_dict() if letzter_wechsel else None,
                    'durchschnittliches_intervall_tage': round(avg_intervall_tage, 1)
                },
                'aktuelle_konfiguration': {
                    'intervall_stunden': config.patronenwechsel_intervall_stunden,
                    'warnung_vor_stunden': config.warnung_vor_stunden
                }
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Historie: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'patronenwechsel': []
            }
    
    @staticmethod
    def validate_patronenwechsel_daten(durchgefuehrt_von: str, 
                                      molekularsieb_1: bool,
                                      molekularsieb_2: bool,
                                      kohle_filter: bool) -> Dict[str, Any]:
        """
        Validiert Patronenwechsel-Daten
        
        Returns:
            Dict mit Validierungs-Ergebnis
        """
        
        errors = []
        
        if not durchgefuehrt_von or len(durchgefuehrt_von.strip()) == 0:
            errors.append("Name der durchführenden Person ist erforderlich")
        
        if not any([molekularsieb_1, molekularsieb_2, kohle_filter]):
            errors.append("Mindestens eine Patrone muss gewechselt werden")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
