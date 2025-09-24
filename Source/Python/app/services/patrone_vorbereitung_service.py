# Service für Patronenvorbereitung - WartungsManager
# Geschäftslogik für das Vorbereiten von Patronen

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from app import db
from app.models.patrone_erweitert import PatroneVorbereitung

logger = logging.getLogger(__name__)

class PatroneVorbereitungService:
    """
    Service für Patronenvorbereitung
    
    Funktionen:
    - Neue Patronen vorbereiten und dokumentieren
    - Etiketten für vorbereitete Patronen drucken
    - Verfügbare Patronen verwalten
    - Qualitätskontrolle und Gewichtsmessung
    """
    
    @staticmethod
    def neue_patrone_vorbereiten(vorbereitet_von: str,
                                patrone_typ: str,
                                charge_nummer: str,
                                patrone_nummer: str = None,
                                gewicht_vor_fuellen: float = None,
                                gewicht_nach_fuellen: float = None,
                                material_verwendet: str = None,
                                notizen: str = None,
                                etikett_drucken: bool = True) -> Dict[str, Any]:
        """
        Bereitet eine neue Patrone vor und dokumentiert den Prozess
        
        Args:
            vorbereitet_von: Name der Person die vorbereitet
            patrone_typ: 'Molekularsieb' oder 'Kohle'
            charge_nummer: Eindeutige Chargennummer
            patrone_nummer: Nummer bei Molekularsieb (1 oder 2)
            gewicht_vor_fuellen: Leergewicht der Patrone
            gewicht_nach_fuellen: Gewicht nach Befüllung
            material_verwendet: Was wurde eingefüllt
            notizen: Zusätzliche Notizen
            etikett_drucken: Soll Etikett gedruckt werden
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            # Validierung
            if not vorbereitet_von or len(vorbereitet_von.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Name der vorbereitenden Person ist erforderlich'
                }
            
            if not patrone_typ or patrone_typ not in ['Molekularsieb', 'Kohle']:
                return {
                    'success': False,
                    'error': 'Patronen-Typ muss "Molekularsieb" oder "Kohle" sein'
                }
            
            if not charge_nummer or len(charge_nummer.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Chargennummer ist erforderlich'
                }
            
            # Prüfen ob Chargennummer bereits existiert
            existierende_patrone = PatroneVorbereitung.query.filter_by(
                charge_nummer=charge_nummer.strip(),
                ist_verwendet=False
            ).first()
            
            if existierende_patrone:
                return {
                    'success': False,
                    'error': f'Chargennummer "{charge_nummer}" ist bereits in Verwendung'
                }
            
            # Neue Vorbereitung erstellen
            neue_vorbereitung = PatroneVorbereitung(
                vorbereitet_von=vorbereitet_von.strip(),
                patrone_typ=patrone_typ,
                patrone_nummer=patrone_nummer.strip() if patrone_nummer else None,
                charge_nummer=charge_nummer.strip(),
                gewicht_vor_fuellen=gewicht_vor_fuellen,
                gewicht_nach_fuellen=gewicht_nach_fuellen,
                material_verwendet=material_verwendet.strip() if material_verwendet else None,
                notizen=notizen.strip() if notizen else None,
                ist_bereit=True
            )
            
            db.session.add(neue_vorbereitung)
            db.session.commit()
            
            logger.info(f"PATRONE VORBEREITET: {patrone_typ} {charge_nummer} von {vorbereitet_von}")
            
            # Etikett drucken wenn gewünscht
            etikett_erfolg = False
            if etikett_drucken:
                etikett_result = PatroneVorbereitungService.etikett_drucken(
                    neue_vorbereitung.id
                )
                etikett_erfolg = etikett_result.get('success', False)
            
            return {
                'success': True,
                'message': f'Patrone {patrone_typ} ({charge_nummer}) erfolgreich vorbereitet',
                'vorbereitung': neue_vorbereitung.to_dict(),
                'etikett_gedruckt': etikett_erfolg
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Patronenvorbereitung: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler: {str(e)}'
            }
    
    @staticmethod
    def etikett_drucken(vorbereitung_id: int) -> Dict[str, Any]:
        """
        Druckt Etikett für vorbereitete Patrone (62cm Endlos-Etikettendrucker)
        
        Args:
            vorbereitung_id: ID der Vorbereitung
        
        Returns:
            Dict mit Druckergebnis
        """
        
        try:
            vorbereitung = PatroneVorbereitung.query.get(vorbereitung_id)
            if not vorbereitung:
                return {
                    'success': False,
                    'error': 'Vorbereitung nicht gefunden'
                }
            
            # Etikett-Daten zusammenstellen
            etikett_data = {
                'typ': vorbereitung.patrone_typ,
                'nummer': vorbereitung.patrone_nummer,
                'charge': vorbereitung.charge_nummer,
                'vorbereitet_von': vorbereitung.vorbereitet_von,
                'vorbereitet_am': vorbereitung.vorbereitet_am.strftime('%d.%m.%Y %H:%M'),
                'gewicht_nach': vorbereitung.gewicht_nach_fuellen,
                'material': vorbereitung.material_verwendet
            }
            
            # Etikett-Layout für 62cm Endlos-Drucker
            etikett_text = PatroneVorbereitungService._erstelle_etikett_layout(etikett_data)
            
            # TODO: Hier würde die tatsächliche Druckansteuerung implementiert
            # Für jetzt simulieren wir erfolgreiches Drucken
            
            # Druckstatus in DB aktualisieren
            vorbereitung.etikett_gedruckt = True
            vorbereitung.etikett_gedruckt_am = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"ETIKETT GEDRUCKT: Patrone {vorbereitung.charge_nummer}")
            
            return {
                'success': True,
                'message': 'Etikett erfolgreich gedruckt',
                'etikett_text': etikett_text,
                'vorbereitung': vorbereitung.to_dict()
            }
            
        except Exception as e:
            logger.error(f"FEHLER beim Etikettendruck: {str(e)}")
            return {
                'success': False,
                'error': f'Fehler beim Drucken: {str(e)}'
            }
    
    @staticmethod
    def _erstelle_etikett_layout(data: Dict[str, Any]) -> str:
        """
        Erstellt Layout für 62cm Endlos-Etikett
        
        Args:
            data: Etikett-Daten
        
        Returns:
            Formatierter Etikett-Text
        """
        
        # Etikett-Layout für 62cm breite Etiketten
        layout = f"""
╔══════════════════════════════════════════════════════════════╗
║                    PATRONE VORBEREITET                      ║
╠══════════════════════════════════════════════════════════════╣
║ TYP: {data['typ']:<25} NR: {data['nummer'] or 'N/A':<15} ║
║ CHARGE: {data['charge']:<49} ║
║                                                              ║
║ VORBEREITET VON: {data['vorbereitet_von']:<38} ║
║ DATUM/ZEIT: {data['vorbereitet_am']:<44} ║
║                                                              ║
║ GEWICHT: {str(data['gewicht_nach']) + ' kg' if data['gewicht_nach'] else 'N/A':<52} ║
║ MATERIAL: {data['material'] or 'Standard':<50} ║
║                                                              ║
║              ⚠️  NUR FÜR WARTUNG VERWENDEN  ⚠️              ║
╚══════════════════════════════════════════════════════════════╝
        """.strip()
        
        return layout
    
    @staticmethod
    def get_verfuegbare_patronen(patrone_typ: str = None) -> Dict[str, Any]:
        """
        Gibt verfügbare (nicht verwendete) Patronen zurück
        
        Args:
            patrone_typ: Filter für Patronen-Typ (optional)
        
        Returns:
            Dict mit verfügbaren Patronen
        """
        
        try:
            patronen = PatroneVorbereitung.get_verfuegbare_patronen(patrone_typ)
            
            # Gruppierung nach Typ
            patronen_gruppiert = {}
            for patrone in patronen:
                typ = patrone.patrone_typ
                if typ not in patronen_gruppiert:
                    patronen_gruppiert[typ] = []
                patronen_gruppiert[typ].append(patrone.to_dict())
            
            return {
                'success': True,
                'patronen_nach_typ': patronen_gruppiert,
                'gesamt_anzahl': len(patronen),
                'molekularsieb_anzahl': len([p for p in patronen if p.patrone_typ == 'Molekularsieb']),
                'kohle_anzahl': len([p for p in patronen if p.patrone_typ == 'Kohle'])
            }
            
        except Exception as e:
            logger.error(f"FEHLER beim Abrufen verfügbarer Patronen: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'patronen_nach_typ': {},
                'gesamt_anzahl': 0
            }
    
    @staticmethod
    def patrone_als_verwendet_markieren(vorbereitung_id: int) -> Dict[str, Any]:
        """
        Markiert eine Patrone als verwendet (beim Wechsel)
        
        Args:
            vorbereitung_id: ID der verwendeten Vorbereitung
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            vorbereitung = PatroneVorbereitung.query.get(vorbereitung_id)
            if not vorbereitung:
                return {
                    'success': False,
                    'error': 'Vorbereitung nicht gefunden'
                }
            
            if vorbereitung.ist_verwendet:
                return {
                    'success': False,
                    'error': 'Patrone wurde bereits verwendet'
                }
            
            vorbereitung.ist_verwendet = True
            vorbereitung.verwendung_datum = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"PATRONE ALS VERWENDET MARKIERT: {vorbereitung.charge_nummer}")
            
            return {
                'success': True,
                'message': f'Patrone {vorbereitung.charge_nummer} als verwendet markiert',
                'vorbereitung': vorbereitung.to_dict()
            }
            
        except Exception as e:
            logger.error(f"FEHLER beim Markieren als verwendet: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_vorbereitungs_historie(limit: int = 50) -> Dict[str, Any]:
        """
        Gibt Historie der Patronenvorbereitungen zurück
        
        Args:
            limit: Anzahl der Einträge
        
        Returns:
            Dict mit Historie
        """
        
        try:
            vorbereitungen = PatroneVorbereitung.query.order_by(
                PatroneVorbereitung.vorbereitet_am.desc()
            ).limit(limit).all()
            
            # Statistiken
            gesamt_anzahl = PatroneVorbereitung.query.count()
            verwendete_anzahl = PatroneVorbereitung.query.filter_by(ist_verwendet=True).count()
            verfuegbare_anzahl = PatroneVorbereitung.query.filter_by(ist_verwendet=False).count()
            
            return {
                'success': True,
                'vorbereitungen': [v.to_dict() for v in vorbereitungen],
                'statistiken': {
                    'gesamt_vorbereitet': gesamt_anzahl,
                    'verwendet': verwendete_anzahl,
                    'verfuegbar': verfuegbare_anzahl
                }
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Vorbereitungs-Historie: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'vorbereitungen': []
            }
