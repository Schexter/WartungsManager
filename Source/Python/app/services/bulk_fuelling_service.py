# Bulk-Füllvorgang Service für WartungsManager
# Geschäftslogik für Mehrfach-Füllungen

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from app import db
from app.models import BulkFuellvorgang, FlascheFuellvorgang, Flasche, Kunde, KompressorBetrieb

logger = logging.getLogger(__name__)

class BulkFuellvorgangService:
    """
    Service für Bulk-Füllvorgänge (mehrere Flaschen gleichzeitig)
    
    Funktionen:
    - Bulk-Füllvorgang erstellen und verwalten
    - Flaschen hinzufügen/entfernen
    - Füllstatus tracking
    - Automatische Kompressor-Verknüpfung
    """
    
    @staticmethod
    def bulk_vorgang_erstellen(operator: str, operator_id: int = None, 
                              flaschen_ids: List[int] = None) -> Dict[str, Any]:
        """
        Erstellt neuen Bulk-Füllvorgang
        
        Args:
            operator: Name des Operators
            operator_id: User-ID des Operators
            flaschen_ids: Optional Liste von Flaschen-IDs
        
        Returns:
            Dict mit Ergebnis und Bulk-Vorgang Daten
        """
        
        try:
            # Prüfe ob bereits ein Bulk-Vorgang aktiv ist
            aktiver_vorgang = BulkFuellvorgang.get_aktiver_bulk_vorgang()
            if aktiver_vorgang:
                logger.warning(f"Bulk-Füllvorgang bereits aktiv: {aktiver_vorgang.id}")
                return {
                    'success': False,
                    'error': 'Es läuft bereits ein Bulk-Füllvorgang',
                    'aktiver_vorgang': aktiver_vorgang.to_dict()
                }
            
            # Prüfe ob Kompressor läuft
            kompressor = KompressorBetrieb.get_aktiver_kompressor()
            if not kompressor:
                return {
                    'success': False,
                    'error': 'Kompressor muss eingeschaltet sein für Bulk-Füllvorgang'
                }
            
            # Neuen Bulk-Vorgang erstellen
            bulk_vorgang = BulkFuellvorgang(
                operator=operator,
                operator_id=operator_id,
                kompressor_betrieb_id=kompressor.id,
                status='vorbereitung'
            )
            
            db.session.add(bulk_vorgang)
            db.session.flush()  # Für ID
            
            # Flaschen hinzufügen falls angegeben
            hinzugefuegte_flaschen = 0
            if flaschen_ids:
                for flasche_id in flaschen_ids:
                    result = BulkFuellvorgangService.flasche_hinzufuegen(
                        bulk_vorgang.id, flasche_id, commit=False
                    )
                    if result['success']:
                        hinzugefuegte_flaschen += 1
            
            db.session.commit()
            
            logger.info(f"Bulk-Füllvorgang erstellt von {operator} mit {hinzugefuegte_flaschen} Flaschen")
            
            return {
                'success': True,
                'message': f'Bulk-Füllvorgang erstellt mit {hinzugefuegte_flaschen} Flaschen',
                'bulk_vorgang': bulk_vorgang.to_dict(include_flaschen=True),
                'kompressor_id': kompressor.id
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Bulk-Vorgangs: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler: {str(e)}'
            }
    
    @staticmethod
    def flasche_hinzufuegen(bulk_vorgang_id: int, flasche_id: int, 
                           ziel_druck: int = 300, commit: bool = True) -> Dict[str, Any]:
        """
        Fügt Flasche zum Bulk-Füllvorgang hinzu
        
        Args:
            bulk_vorgang_id: ID des Bulk-Vorgangs
            flasche_id: ID der Flasche
            ziel_druck: Zieldruck in Bar
            commit: DB-Commit ausführen
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            # Bulk-Vorgang finden
            bulk_vorgang = BulkFuellvorgang.query.get(bulk_vorgang_id)
            if not bulk_vorgang:
                return {
                    'success': False,
                    'error': 'Bulk-Füllvorgang nicht gefunden'
                }
            
            if bulk_vorgang.status not in ['vorbereitung', 'laufend']:
                return {
                    'success': False,
                    'error': 'Flaschen können nur in Vorbereitung oder laufendem Vorgang hinzugefügt werden'
                }
            
            # Flasche finden und prüfen
            flasche = Flasche.query.get(flasche_id)
            if not flasche:
                return {
                    'success': False,
                    'error': 'Flasche nicht gefunden'
                }
            
            if not flasche.ist_fuellbereit:
                return {
                    'success': False,
                    'error': f'Flasche {flasche.flaschennummer} ist nicht füllbereit (TÜV, Status, etc.)'
                }
            
            # Prüfe ob Flasche bereits hinzugefügt
            existing = bulk_vorgang.flasche_fuellungen.filter_by(flasche_id=flasche_id).first()
            if existing:
                return {
                    'success': False,
                    'error': f'Flasche {flasche.flaschennummer} bereits im Bulk-Vorgang'
                }
            
            # Flasche hinzufügen
            flasche_fuellung = FlascheFuellvorgang(
                bulk_fuellvorgang_id=bulk_vorgang_id,
                flasche_id=flasche_id,
                ziel_druck=ziel_druck,
                status='wartend'
            )
            
            db.session.add(flasche_fuellung)
            bulk_vorgang.anzahl_flaschen += 1
            
            # Flasche als vorgemerkt markieren
            flasche.vormerkung_setzen(True)
            
            if commit:
                db.session.commit()
            
            logger.info(f"Flasche {flasche.flaschennummer} zu Bulk-Vorgang {bulk_vorgang_id} hinzugefügt")
            
            return {
                'success': True,
                'message': f'Flasche {flasche.flaschennummer} hinzugefügt',
                'flasche_fuellung': flasche_fuellung.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Flasche: {str(e)}")
            if commit:
                db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler: {str(e)}'
            }
    
    @staticmethod
    def flasche_entfernen(bulk_vorgang_id: int, flasche_id: int) -> Dict[str, Any]:
        """
        Entfernt Flasche aus Bulk-Füllvorgang
        
        Args:
            bulk_vorgang_id: ID des Bulk-Vorgangs
            flasche_id: ID der Flasche
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            # Bulk-Vorgang finden
            bulk_vorgang = BulkFuellvorgang.query.get(bulk_vorgang_id)
            if not bulk_vorgang:
                return {
                    'success': False,
                    'error': 'Bulk-Füllvorgang nicht gefunden'
                }
            
            # Flasche-Füllung finden
            flasche_fuellung = bulk_vorgang.flasche_fuellungen.filter_by(flasche_id=flasche_id).first()
            if not flasche_fuellung:
                return {
                    'success': False,
                    'error': 'Flasche nicht im Bulk-Vorgang gefunden'
                }
            
            # Nur wartende Flaschen können entfernt werden
            if flasche_fuellung.status != 'wartend':
                return {
                    'success': False,
                    'error': f'Flasche kann nicht entfernt werden (Status: {flasche_fuellung.status})'
                }
            
            flasche = flasche_fuellung.flasche
            
            # Flasche-Füllung entfernen
            db.session.delete(flasche_fuellung)
            bulk_vorgang.anzahl_flaschen -= 1
            
            # Flasche-Vormerkung entfernen
            flasche.vormerkung_setzen(False)
            
            db.session.commit()
            
            logger.info(f"Flasche {flasche.flaschennummer} aus Bulk-Vorgang {bulk_vorgang_id} entfernt")
            
            return {
                'success': True,
                'message': f'Flasche {flasche.flaschennummer} entfernt'
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Entfernen der Flasche: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler: {str(e)}'
            }
    
    @staticmethod
    def bulk_vorgang_starten(bulk_vorgang_id: int) -> Dict[str, Any]:
        """
        Startet Bulk-Füllvorgang
        
        Args:
            bulk_vorgang_id: ID des Bulk-Vorgangs
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            bulk_vorgang = BulkFuellvorgang.query.get(bulk_vorgang_id)
            if not bulk_vorgang:
                return {
                    'success': False,
                    'error': 'Bulk-Füllvorgang nicht gefunden'
                }
            
            if bulk_vorgang.anzahl_flaschen == 0:
                return {
                    'success': False,
                    'error': 'Keine Flaschen im Bulk-Vorgang'
                }
            
            # Prüfe ob Kompressor noch läuft
            if not bulk_vorgang.kompressor_betrieb or not bulk_vorgang.kompressor_betrieb.ist_aktiv:
                return {
                    'success': False,
                    'error': 'Kompressor läuft nicht mehr'
                }
            
            bulk_vorgang.starten()
            db.session.commit()
            
            logger.info(f"Bulk-Füllvorgang {bulk_vorgang_id} gestartet mit {bulk_vorgang.anzahl_flaschen} Flaschen")
            
            return {
                'success': True,
                'message': f'Bulk-Füllvorgang gestartet mit {bulk_vorgang.anzahl_flaschen} Flaschen',
                'bulk_vorgang': bulk_vorgang.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Starten des Bulk-Vorgangs: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler: {str(e)}'
            }
    
    @staticmethod
    def flasche_als_gefuellt_markieren(bulk_vorgang_id: int, flasche_id: int, 
                                     erreicher_druck: int = None) -> Dict[str, Any]:
        """
        Markiert Flasche als erfolgreich gefüllt
        
        Args:
            bulk_vorgang_id: ID des Bulk-Vorgangs
            flasche_id: ID der Flasche
            erreicher_druck: Erreichter Druck in Bar
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            bulk_vorgang = BulkFuellvorgang.query.get(bulk_vorgang_id)
            if not bulk_vorgang:
                return {
                    'success': False,
                    'error': 'Bulk-Füllvorgang nicht gefunden'
                }
            
            # Flasche-Füllung finden
            flasche_fuellung = bulk_vorgang.flasche_fuellungen.filter_by(flasche_id=flasche_id).first()
            if not flasche_fuellung:
                return {
                    'success': False,
                    'error': 'Flasche nicht im Bulk-Vorgang gefunden'
                }
            
            if flasche_fuellung.status != 'wartend':
                return {
                    'success': False,
                    'error': f'Flasche bereits bearbeitet (Status: {flasche_fuellung.status})'
                }
            
            # Als erfolgreich markieren
            flasche_fuellung.als_erfolgreich_markieren(erreicher_druck)
            bulk_vorgang.erfolgreich_gefuellt += 1
            
            # Flasche-Vormerkung entfernen und letzten Füllstand aktualisieren
            flasche = flasche_fuellung.flasche
            flasche.vormerkung_setzen(False)
            if erreicher_druck:
                flasche.letzter_fuellstand = erreicher_druck
            
            db.session.commit()
            
            logger.info(f"Flasche {flasche.flaschennummer} als gefüllt markiert ({erreicher_druck} Bar)")
            
            return {
                'success': True,
                'message': f'Flasche {flasche.flaschennummer} erfolgreich gefüllt',
                'flasche_fuellung': flasche_fuellung.to_dict(),
                'bulk_status': {
                    'bearbeitet': bulk_vorgang.bearbeitete_flaschen,
                    'offen': bulk_vorgang.offene_flaschen,
                    'erfolgsquote': bulk_vorgang.erfolgsquote_prozent
                }
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Markieren der Flasche als gefüllt: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler: {str(e)}'
            }
    
    @staticmethod
    def flasche_als_fehlgeschlagen_markieren(bulk_vorgang_id: int, flasche_id: int, 
                                           grund: str = None) -> Dict[str, Any]:
        """
        Markiert Flasche als fehlgeschlagen
        
        Args:
            bulk_vorgang_id: ID des Bulk-Vorgangs
            flasche_id: ID der Flasche
            grund: Grund für Fehlschlag
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            bulk_vorgang = BulkFuellvorgang.query.get(bulk_vorgang_id)
            if not bulk_vorgang:
                return {
                    'success': False,
                    'error': 'Bulk-Füllvorgang nicht gefunden'
                }
            
            # Flasche-Füllung finden
            flasche_fuellung = bulk_vorgang.flasche_fuellungen.filter_by(flasche_id=flasche_id).first()
            if not flasche_fuellung:
                return {
                    'success': False,
                    'error': 'Flasche nicht im Bulk-Vorgang gefunden'
                }
            
            if flasche_fuellung.status != 'wartend':
                return {
                    'success': False,
                    'error': f'Flasche bereits bearbeitet (Status: {flasche_fuellung.status})'
                }
            
            # Als fehlgeschlagen markieren
            flasche_fuellung.als_fehlgeschlagen_markieren(grund)
            bulk_vorgang.fehlgeschlagen += 1
            
            # Flasche-Vormerkung entfernen
            flasche = flasche_fuellung.flasche
            flasche.vormerkung_setzen(False)
            
            db.session.commit()
            
            logger.warning(f"Flasche {flasche.flaschennummer} als fehlgeschlagen markiert: {grund}")
            
            return {
                'success': True,
                'message': f'Flasche {flasche.flaschennummer} als fehlgeschlagen markiert',
                'flasche_fuellung': flasche_fuellung.to_dict(),
                'bulk_status': {
                    'bearbeitet': bulk_vorgang.bearbeitete_flaschen,
                    'offen': bulk_vorgang.offene_flaschen,
                    'erfolgsquote': bulk_vorgang.erfolgsquote_prozent
                }
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Markieren der Flasche als fehlgeschlagen: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler: {str(e)}'
            }
    
    @staticmethod
    def bulk_vorgang_beenden(bulk_vorgang_id: int, notizen: str = None) -> Dict[str, Any]:
        """
        Beendet Bulk-Füllvorgang
        
        Args:
            bulk_vorgang_id: ID des Bulk-Vorgangs
            notizen: Optional Abschluss-Notizen
        
        Returns:
            Dict mit Ergebnis und Statistiken
        """
        
        try:
            bulk_vorgang = BulkFuellvorgang.query.get(bulk_vorgang_id)
            if not bulk_vorgang:
                return {
                    'success': False,
                    'error': 'Bulk-Füllvorgang nicht gefunden'
                }
            
            if bulk_vorgang.status == 'beendet':
                return {
                    'success': False,
                    'error': 'Bulk-Füllvorgang bereits beendet'
                }
            
            # Alle noch wartenden Flaschen als "nicht bearbeitet" markieren
            wartende_flaschen = bulk_vorgang.flasche_fuellungen.filter_by(status='wartend').all()
            for ff in wartende_flaschen:
                ff.als_fehlgeschlagen_markieren("Bulk-Vorgang beendet")
                bulk_vorgang.fehlgeschlagen += 1
                ff.flasche.vormerkung_setzen(False)
            
            # Bulk-Vorgang beenden
            bulk_vorgang.beenden()
            if notizen:
                bulk_vorgang.notizen = bulk_vorgang.notizen or ""
                bulk_vorgang.notizen += f"\nAbschluss: {notizen}"
            
            db.session.commit()
            
            logger.info(f"Bulk-Füllvorgang {bulk_vorgang_id} beendet - {bulk_vorgang.erfolgreich_gefuellt}/{bulk_vorgang.anzahl_flaschen} erfolgreich")
            
            return {
                'success': True,
                'message': f'Bulk-Füllvorgang beendet',
                'bulk_vorgang': bulk_vorgang.to_dict(include_flaschen=True),
                'statistik': {
                    'gesamt_flaschen': bulk_vorgang.anzahl_flaschen,
                    'erfolgreich': bulk_vorgang.erfolgreich_gefuellt,
                    'fehlgeschlagen': bulk_vorgang.fehlgeschlagen,
                    'erfolgsquote_prozent': bulk_vorgang.erfolgsquote_prozent,
                    'gesamtdauer_stunden': bulk_vorgang.gesamtdauer_stunden
                }
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Beenden des Bulk-Vorgangs: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Fehler: {str(e)}'
            }
    
    @staticmethod
    def get_aktiver_bulk_vorgang() -> Dict[str, Any]:
        """
        Gibt aktuell aktiven Bulk-Füllvorgang zurück
        
        Returns:
            Dict mit Bulk-Vorgang oder None
        """
        
        try:
            aktiver_vorgang = BulkFuellvorgang.get_aktiver_bulk_vorgang()
            
            if not aktiver_vorgang:
                return {
                    'aktiver_vorgang': None,
                    'ist_aktiv': False
                }
            
            return {
                'aktiver_vorgang': aktiver_vorgang.to_dict(include_flaschen=True),
                'ist_aktiv': True,
                'flaschen_status': {
                    'gesamt': aktiver_vorgang.anzahl_flaschen,
                    'bearbeitet': aktiver_vorgang.bearbeitete_flaschen,
                    'offen': aktiver_vorgang.offene_flaschen,
                    'erfolgreich': aktiver_vorgang.erfolgreich_gefuellt,
                    'fehlgeschlagen': aktiver_vorgang.fehlgeschlagen
                }
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des aktiven Bulk-Vorgangs: {str(e)}")
            return {
                'aktiver_vorgang': None,
                'ist_aktiv': False,
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
                # Zusätzliche Informationen
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
