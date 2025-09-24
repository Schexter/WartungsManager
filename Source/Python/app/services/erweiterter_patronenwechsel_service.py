# Erweiterter Patronenwechsel Service - WartungsManager
# Neuer Service für Patronenwechsel mit vorbereiteten Patronen

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from app import db
from app.models.patronenwechsel import Patronenwechsel, PatronenwechselKonfiguration
from app.models.patrone_erweitert import PatroneVorbereitung, PatroneWechselProtokoll
from app.models.kompressor import KompressorBetrieb
from app.services.patrone_vorbereitung_service import PatroneVorbereitungService

logger = logging.getLogger(__name__)

class ErweiterterPatronenwechselService:
    """
    Erweiterter Service für Patronenwechsel mit vorbereiteten Patronen
    
    Funktionen:
    - Patronenwechsel mit vorbereiteten Patronen aus DB
    - Erweiterte Dokumentation mit Gewichten
    - Integration mit Vorbereitung und Einkauf
    - Detailliertes Logbuch
    """
    
    @staticmethod
    def patronenwechsel_mit_vorbereiteten_patronen(passwort: str,
                                                  gewechselt_von: str,
                                                  molekularsieb_1_vorbereitung_id: int = None,
                                                  molekularsieb_2_vorbereitung_id: int = None,
                                                  kohle_vorbereitung_id: int = None,
                                                  alte_mol_1_gewicht: float = None,
                                                  alte_mol_2_gewicht: float = None,
                                                  alte_kohle_gewicht: float = None,
                                                  wechsel_grund: str = "Planmäßiger Wechsel",
                                                  alte_patronen_zustand: str = None,
                                                  notizen: str = None) -> Dict[str, Any]:
        """
        Führt Patronenwechsel mit vorbereiteten Patronen durch
        
        Args:
            passwort: Wartungspasswort
            gewechselt_von: Wer führt den Wechsel durch
            molekularsieb_1_vorbereitung_id: ID der vorbereiteten Patrone
            molekularsieb_2_vorbereitung_id: ID der vorbereiteten Patrone
            kohle_vorbereitung_id: ID der vorbereiteten Patrone
            alte_mol_1_gewicht: Gewicht der alten Patrone
            alte_mol_2_gewicht: Gewicht der alten Patrone
            alte_kohle_gewicht: Gewicht der alten Patrone
            wechsel_grund: Grund für den Wechsel
            alte_patronen_zustand: Zustand der alten Patronen
            notizen: Zusätzliche Notizen
        
        Returns:
            Dict mit Ergebnis
        """
        
        # Passwort-Validierung
        WARTUNGS_PASSWORT = "Magicfactory15!"
        if passwort != WARTUNGS_PASSWORT:
            logger.warning(f"FEHLGESCHLAGENER PATRONENWECHSEL: Falsches Passwort von {gewechselt_von}")
            return {
                'success': False,
                'error': 'Ungültiges Passwort für Patronenwechsel'
            }
        
        try:
            # Mindestens eine Patrone muss gewechselt werden
            if not any([molekularsieb_1_vorbereitung_id, molekularsieb_2_vorbereitung_id, kohle_vorbereitung_id]):
                return {
                    'success': False,
                    'error': 'Mindestens eine Patrone muss gewechselt werden'
                }
            
            # Vorbereitete Patronen validieren und laden
            vorbereitete_patronen = {}
            neue_patronen_info = []
            
            if molekularsieb_1_vorbereitung_id:
                mol_1 = PatroneVorbereitung.query.get(molekularsieb_1_vorbereitung_id)
                if not mol_1 or mol_1.ist_verwendet:
                    return {
                        'success': False,
                        'error': 'Molekularsieb Patrone 1 ist nicht verfügbar oder bereits verwendet'
                    }
                vorbereitete_patronen['molekularsieb_1'] = mol_1
                neue_patronen_info.append(f"Molekularsieb 1: {mol_1.charge_nummer}")
            
            if molekularsieb_2_vorbereitung_id:
                mol_2 = PatroneVorbereitung.query.get(molekularsieb_2_vorbereitung_id)
                if not mol_2 or mol_2.ist_verwendet:
                    return {
                        'success': False,
                        'error': 'Molekularsieb Patrone 2 ist nicht verfügbar oder bereits verwendet'
                    }
                vorbereitete_patronen['molekularsieb_2'] = mol_2
                neue_patronen_info.append(f"Molekularsieb 2: {mol_2.charge_nummer}")
            
            if kohle_vorbereitung_id:
                kohle = PatroneVorbereitung.query.get(kohle_vorbereitung_id)
                if not kohle or kohle.ist_verwendet:
                    return {
                        'success': False,
                        'error': 'Kohle-Filter ist nicht verfügbar oder bereits verwendet'
                    }
                vorbereitete_patronen['kohle'] = kohle
                neue_patronen_info.append(f"Kohle: {kohle.charge_nummer}")
            
            # Status vor Wechsel für Protokoll
            alter_status = Patronenwechsel.get_patronenwechsel_status()
            
            # Basis-Patronenwechsel erstellen
            neuer_wechsel = Patronenwechsel.neuer_patronenwechsel(
                durchgefuehrt_von=gewechselt_von,
                wechsel_datum=datetime.utcnow(),
                molekularsieb_1=molekularsieb_1_vorbereitung_id is not None,
                molekularsieb_2=molekularsieb_2_vorbereitung_id is not None,
                kohle_filter=kohle_vorbereitung_id is not None,
                mol_1_charge=vorbereitete_patronen.get('molekularsieb_1').charge_nummer if 'molekularsieb_1' in vorbereitete_patronen else None,
                mol_2_charge=vorbereitete_patronen.get('molekularsieb_2').charge_nummer if 'molekularsieb_2' in vorbereitete_patronen else None,
                kohle_charge=vorbereitete_patronen.get('kohle').charge_nummer if 'kohle' in vorbereitete_patronen else None,
                notizen=notizen
            )
            
            logger.info(f"ERWEITERTER PATRONENWECHSEL DURCHGEFÜHRT: {gewechselt_von}, Patronen: {', '.join(neue_patronen_info)}, Betriebsstunden: {neuer_wechsel.betriebsstunden_bei_wechsel}h")
            
            return {
                'success': True,
                'message': 'Patronenwechsel mit vorbereiteten Patronen erfolgreich durchgeführt',
                'patronenwechsel': neuer_wechsel.to_dict(),
                'gewechselte_patronen': neue_patronen_info,
                'alter_status': alter_status,
                'neuer_status': Patronenwechsel.get_patronenwechsel_status()
            }
            
        except Exception as e:
            logger.error(f"FEHLER beim erweiterten Patronenwechsel: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler beim Patronenwechsel: {str(e)}'
            }
    
    @staticmethod
    def get_dashboard_status_minimal() -> Dict[str, Any]:
        """
        Gibt minimalen Status für Dashboard zurück (nur Countdown)
        
        Returns:
            Dict mit minimalem Dashboard-Status
        """
        
        try:
            status = Patronenwechsel.get_patronenwechsel_status()
            
            # Nur die wichtigsten Infos für Dashboard
            countdown_text = "Bereit"
            countdown_class = "text-success"
            countdown_icon = "✅"
            
            if status['wechsel_faellig']:
                countdown_text = "WECHSEL FÄLLIG!"
                countdown_class = "text-danger"
                countdown_icon = "🚨"
            elif status['warnung_aktiv']:
                stunden_bis = status['stunden_bis_wechsel']
                countdown_text = f"Wechsel in {stunden_bis:.1f}h"
                countdown_class = "text-warning"
                countdown_icon = "⚠️"
            else:
                stunden_bis = status['stunden_bis_wechsel']
                countdown_text = f"Nächster Wechsel in {stunden_bis:.1f}h"
                countdown_class = "text-success"
                countdown_icon = "✅"
            
            return {
                'countdown_text': countdown_text,
                'countdown_class': countdown_class,
                'countdown_icon': countdown_icon,
                'stunden_bis_wechsel': status['stunden_bis_wechsel'],
                'wechsel_faellig': status['wechsel_faellig'],
                'warnung_aktiv': status['warnung_aktiv']
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Dashboard-Status: {str(e)}")
            return {
                'countdown_text': "Fehler",
                'countdown_class': "text-danger",
                'countdown_icon': "❌",
                'stunden_bis_wechsel': 0.0,
                'wechsel_faellig': True,
                'warnung_aktiv': True,
                'error': str(e)
            }
    
    @staticmethod
    def get_wechsel_historie_erweitert(limit: int = 20) -> Dict[str, Any]:
        """
        Gibt erweiterte Wechsel-Historie zurück
        
        Args:
            limit: Anzahl der Einträge
        
        Returns:
            Dict mit erweiterter Historie
        """
        
        try:
            wechsel = Patronenwechsel.query.order_by(
                Patronenwechsel.wechsel_datum.desc()
            ).limit(limit).all()
            
            erweiterte_historie = []
            for w in wechsel:
                wechsel_dict = w.to_dict()
                wechsel_dict['hat_erweiterte_protokolle'] = False  # Simplified
                erweiterte_historie.append(wechsel_dict)
            
            # Statistiken
            total_wechsel = Patronenwechsel.query.count()
            
            return {
                'success': True,
                'wechsel_historie': erweiterte_historie,
                'statistiken': {
                    'total_wechsel': total_wechsel,
                    'erweiterte_wechsel': 0,  # Simplified
                    'prozent_erweitert': 0
                }
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei erweiterter Wechsel-Historie: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'wechsel_historie': []
            }
