# Service für Patronen-Einkauf - WartungsManager
# Geschäftslogik für Einkauf und Verwaltung von Patronenmaterial

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from app import db
from app.models.patrone_erweitert import PatroneEinkauf

logger = logging.getLogger(__name__)

class PatroneEinkaufService:
    """
    Service für Patronen-Einkauf
    
    Funktionen:
    - Gekaufte Patronen/Material einbuchen
    - Lieferanten verwalten
    - Kleber für Einkäufe drucken
    - Lagerbestand überwachen
    """
    
    @staticmethod
    def neuen_einkauf_einbuchen(eingekauft_von: str,
                               lieferant: str,
                               produkt_name: str,
                               produkt_typ: str,
                               menge: float,
                               einheit: str,
                               einkauf_datum: str = None,
                               einzelpreis: float = None,
                               gesamtpreis: float = None,
                               lieferdatum: str = None,
                               charge_nummer_lieferant: str = None,
                               haltbarkeitsdatum: str = None,
                               lagerort: str = None,
                               notizen: str = None,
                               kleber_drucken: bool = True) -> Dict[str, Any]:
        """
        Bucht einen neuen Patronen-Einkauf ein
        
        Args:
            eingekauft_von: Wer hat eingekauft
            lieferant: Name des Lieferanten
            produkt_name: Produktbezeichnung
            produkt_typ: 'Molekularsieb', 'Kohle', etc.
            menge: Menge (Anzahl/Gewicht)
            einheit: 'kg', 'Stück', etc.
            einkauf_datum: Bestelldatum (optional, default: heute)
            einzelpreis: Preis pro Einheit
            gesamtpreis: Gesamtpreis
            lieferdatum: Datum der Lieferung
            charge_nummer_lieferant: Chargennummer vom Lieferanten
            haltbarkeitsdatum: Haltbarkeitsdatum
            lagerort: Wo wird gelagert
            notizen: Zusätzliche Notizen
            kleber_drucken: Soll Kleber gedruckt werden
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            # Validierung
            if not eingekauft_von or len(eingekauft_von.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Name der einkaufenden Person ist erforderlich'
                }
            
            if not lieferant or len(lieferant.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Lieferant ist erforderlich'
                }
            
            if not produkt_name or len(produkt_name.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Produktname ist erforderlich'
                }
            
            if not produkt_typ or produkt_typ not in ['Molekularsieb', 'Kohle', 'Sonstiges']:
                return {
                    'success': False,
                    'error': 'Produkt-Typ muss "Molekularsieb", "Kohle" oder "Sonstiges" sein'
                }
            
            if not menge or menge <= 0:
                return {
                    'success': False,
                    'error': 'Menge muss größer als 0 sein'
                }
            
            if not einheit or len(einheit.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Einheit ist erforderlich'
                }
            
            # Datum parsen
            einkauf_datum_obj = datetime.utcnow()
            if einkauf_datum:
                try:
                    einkauf_datum_obj = datetime.fromisoformat(einkauf_datum.replace('Z', '+00:00'))
                except:
                    einkauf_datum_obj = datetime.utcnow()
            
            lieferdatum_obj = None
            if lieferdatum:
                try:
                    lieferdatum_obj = datetime.fromisoformat(lieferdatum.replace('Z', '+00:00'))
                except:
                    pass
            
            haltbarkeitsdatum_obj = None
            if haltbarkeitsdatum:
                try:
                    haltbarkeitsdatum_obj = datetime.fromisoformat(haltbarkeitsdatum.replace('Z', '+00:00'))
                except:
                    pass
            
            # Neuen Einkauf erstellen
            neuer_einkauf = PatroneEinkauf(
                eingekauft_von=eingekauft_von.strip(),
                einkauf_datum=einkauf_datum_obj,
                lieferant=lieferant.strip(),
                produkt_name=produkt_name.strip(),
                produkt_typ=produkt_typ,
                menge=menge,
                einheit=einheit.strip(),
                einzelpreis=einzelpreis,
                gesamtpreis=gesamtpreis,
                lieferdatum=lieferdatum_obj,
                ist_geliefert=lieferdatum_obj is not None,
                charge_nummer_lieferant=charge_nummer_lieferant.strip() if charge_nummer_lieferant else None,
                haltbarkeitsdatum=haltbarkeitsdatum_obj,
                lagerort=lagerort.strip() if lagerort else None,
                notizen=notizen.strip() if notizen else None
            )
            
            db.session.add(neuer_einkauf)
            db.session.commit()
            
            logger.info(f"EINKAUF EINGEBUCHT: {produkt_name} von {lieferant} ({menge} {einheit})")
            
            # Kleber drucken wenn gewünscht
            kleber_erfolg = False
            if kleber_drucken:
                kleber_result = PatroneEinkaufService.kleber_drucken(
                    neuer_einkauf.id
                )
                kleber_erfolg = kleber_result.get('success', False)
            
            return {
                'success': True,
                'message': f'Einkauf {produkt_name} von {lieferant} erfolgreich eingebucht',
                'einkauf': neuer_einkauf.to_dict(),
                'kleber_gedruckt': kleber_erfolg
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Einkaufs-Einbuchung: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unerwarteter Fehler: {str(e)}'
            }
    
    @staticmethod
    def kleber_drucken(einkauf_id: int) -> Dict[str, Any]:
        """
        Druckt Kleber für gekaufte Ware mit Lieferant und Datum
        
        Args:
            einkauf_id: ID des Einkaufs
        
        Returns:
            Dict mit Druckergebnis
        """
        
        try:
            einkauf = PatroneEinkauf.query.get(einkauf_id)
            if not einkauf:
                return {
                    'success': False,
                    'error': 'Einkauf nicht gefunden'
                }
            
            # Kleber-Daten zusammenstellen
            kleber_data = {
                'produkt': einkauf.produkt_name,
                'typ': einkauf.produkt_typ,
                'lieferant': einkauf.lieferant,
                'einkauf_datum': einkauf.einkauf_datum.strftime('%d.%m.%Y'),
                'lieferdatum': einkauf.lieferdatum.strftime('%d.%m.%Y') if einkauf.lieferdatum else 'Ausstehend',
                'menge': einkauf.menge,
                'einheit': einkauf.einheit,
                'charge_lieferant': einkauf.charge_nummer_lieferant,
                'haltbarkeit': einkauf.haltbarkeitsdatum.strftime('%d.%m.%Y') if einkauf.haltbarkeitsdatum else None,
                'lagerort': einkauf.lagerort
            }
            
            # Kleber-Layout erstellen
            kleber_text = PatroneEinkaufService._erstelle_kleber_layout(kleber_data)
            
            # TODO: Hier würde die tatsächliche Druckansteuerung implementiert
            # Für jetzt simulieren wir erfolgreiches Drucken
            
            # Druckstatus in DB aktualisieren
            einkauf.kleber_gedruckt = True
            einkauf.kleber_gedruckt_am = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"KLEBER GEDRUCKT: Einkauf {einkauf.produkt_name} ({einkauf.id})")
            
            return {
                'success': True,
                'message': 'Kleber erfolgreich gedruckt',
                'kleber_text': kleber_text,
                'einkauf': einkauf.to_dict()
            }
            
        except Exception as e:
            logger.error(f"FEHLER beim Kleber-Druck: {str(e)}")
            return {
                'success': False,
                'error': f'Fehler beim Drucken: {str(e)}'
            }
    
    @staticmethod
    def _erstelle_kleber_layout(data: Dict[str, Any]) -> str:
        """
        Erstellt Layout für Lager-Kleber
        
        Args:
            data: Kleber-Daten
        
        Returns:
            Formatierter Kleber-Text
        """
        
        # Kleber-Layout für Lagerung
        layout = f"""
┌──────────────────────────────────────────────────────────────┐
│                      PATRONEN-MATERIAL                      │
├──────────────────────────────────────────────────────────────┤
│ PRODUKT: {data['produkt']:<48} │
│ TYP: {data['typ']:<52} │
│ LIEFERANT: {data['lieferant']:<46} │
│                                                              │
│ EINGEKAUFT: {data['einkauf_datum']:<43} │
│ GELIEFERT: {data['lieferdatum']:<44} │
│ MENGE: {str(data['menge']) + ' ' + data['einheit']:<50} │
│                                                              │
│ CHARGE: {data['charge_lieferant'] or 'N/A':<49} │
│ HALTBAR BIS: {data['haltbarkeit'] or 'Unbegrenzt':<42} │
│ LAGERORT: {data['lagerort'] or 'Nicht angegeben':<45} │
│                                                              │
│                    🏭 MAGIC FACTORY 🏭                     │
└──────────────────────────────────────────────────────────────┘
        """.strip()
        
        return layout
    
    @staticmethod
    def lieferung_erhalten(einkauf_id: int, lieferdatum: str = None) -> Dict[str, Any]:
        """
        Markiert einen Einkauf als geliefert
        
        Args:
            einkauf_id: ID des Einkaufs
            lieferdatum: Lieferdatum (optional, default: heute)
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            einkauf = PatroneEinkauf.query.get(einkauf_id)
            if not einkauf:
                return {
                    'success': False,
                    'error': 'Einkauf nicht gefunden'
                }
            
            # Lieferdatum setzen
            if lieferdatum:
                try:
                    lieferdatum_obj = datetime.fromisoformat(lieferdatum.replace('Z', '+00:00'))
                except:
                    lieferdatum_obj = datetime.utcnow()
            else:
                lieferdatum_obj = datetime.utcnow()
            
            einkauf.lieferdatum = lieferdatum_obj
            einkauf.ist_geliefert = True
            db.session.commit()
            
            logger.info(f"LIEFERUNG ERHALTEN: {einkauf.produkt_name} von {einkauf.lieferant}")
            
            return {
                'success': True,
                'message': f'Lieferung für {einkauf.produkt_name} als erhalten markiert',
                'einkauf': einkauf.to_dict()
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Lieferung-Update: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def material_verbrauchen(einkauf_id: int, verbrauchte_menge: float, notizen: str = None) -> Dict[str, Any]:
        """
        Dokumentiert Verbrauch von eingekauftem Material
        
        Args:
            einkauf_id: ID des Einkaufs
            verbrauchte_menge: Menge die verbraucht wurde
            notizen: Notizen zum Verbrauch
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            einkauf = PatroneEinkauf.query.get(einkauf_id)
            if not einkauf:
                return {
                    'success': False,
                    'error': 'Einkauf nicht gefunden'
                }
            
            # Validierung
            if verbrauchte_menge <= 0:
                return {
                    'success': False,
                    'error': 'Verbrauchte Menge muss größer als 0 sein'
                }
            
            neue_verbraucht_menge = einkauf.verbraucht_menge + verbrauchte_menge
            if neue_verbraucht_menge > einkauf.menge:
                return {
                    'success': False,
                    'error': f'Nicht genug Material vorhanden. Verfügbar: {einkauf.menge - einkauf.verbraucht_menge} {einkauf.einheit}'
                }
            
            # Verbrauch dokumentieren
            einkauf.verbraucht_menge = neue_verbraucht_menge
            einkauf.verbleibende_menge = einkauf.menge - neue_verbraucht_menge
            
            if notizen:
                datum_str = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
                verbrauch_notiz = f"[{datum_str}] Verbrauch: {verbrauchte_menge} {einkauf.einheit} - {notizen}"
                
                if einkauf.notizen:
                    einkauf.notizen += f"\n{verbrauch_notiz}"
                else:
                    einkauf.notizen = verbrauch_notiz
            
            db.session.commit()
            
            logger.info(f"MATERIAL VERBRAUCHT: {verbrauchte_menge} {einkauf.einheit} von {einkauf.produkt_name}")
            
            return {
                'success': True,
                'message': f'{verbrauchte_menge} {einkauf.einheit} {einkauf.produkt_name} als verbraucht markiert',
                'einkauf': einkauf.to_dict(),
                'verbleibende_menge': einkauf.verbleibende_menge
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Material-Verbrauch: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_lagerbestand() -> Dict[str, Any]:
        """
        Gibt aktuellen Lagerbestand zurück
        
        Returns:
            Dict mit Lagerbestand-Informationen
        """
        
        try:
            einkäufe = PatroneEinkauf.query.filter_by(ist_aktiv=True).all()
            
            # Gruppierung nach Produkt-Typ
            lagerbestand = {}
            for einkauf in einkäufe:
                typ = einkauf.produkt_typ
                if typ not in lagerbestand:
                    lagerbestand[typ] = []
                
                verbleibend = einkauf.verbleibende_menge_berechnet
                if verbleibend > 0:  # Nur Artikel mit Bestand
                    lagerbestand[typ].append({
                        'einkauf': einkauf.to_dict(),
                        'verbleibende_menge': verbleibend,
                        'prozent_verbleibend': (verbleibend / einkauf.menge) * 100
                    })
            
            # Niedrige Bestände ermitteln (< 20%)
            niedrige_bestaende = []
            for typ, artikel in lagerbestand.items():
                for artikel_info in artikel:
                    if artikel_info['prozent_verbleibend'] < 20:
                        niedrige_bestaende.append(artikel_info)
            
            return {
                'success': True,
                'lagerbestand_nach_typ': lagerbestand,
                'niedrige_bestaende': niedrige_bestaende,
                'warnung_anzahl': len(niedrige_bestaende)
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Lagerbestand-Abfrage: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'lagerbestand_nach_typ': {}
            }
    
    @staticmethod
    def get_einkaufs_historie(limit: int = 50) -> Dict[str, Any]:
        """
        Gibt Einkaufs-Historie zurück
        
        Args:
            limit: Anzahl der Einträge
        
        Returns:
            Dict mit Einkaufs-Historie
        """
        
        try:
            einkäufe = PatroneEinkauf.query.order_by(
                PatroneEinkauf.einkauf_datum.desc()
            ).limit(limit).all()
            
            # Statistiken
            gesamt_anzahl = PatroneEinkauf.query.count()
            gesamt_wert = db.session.query(db.func.sum(PatroneEinkauf.gesamtpreis)).scalar() or 0
            ausstehende_lieferungen = PatroneEinkauf.query.filter_by(
                ist_geliefert=False, ist_aktiv=True
            ).count()
            
            return {
                'success': True,
                'einkäufe': [e.to_dict() for e in einkäufe],
                'statistiken': {
                    'gesamt_einkäufe': gesamt_anzahl,
                    'gesamt_wert_eur': round(gesamt_wert, 2),
                    'ausstehende_lieferungen': ausstehende_lieferungen
                }
            }
            
        except Exception as e:
            logger.error(f"FEHLER bei Einkaufs-Historie: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'einkäufe': []
            }
