"""
Prüfungsmanagement-Service für Flaschen
Verwaltet TÜV-Prüfungen, Benachrichtigungen und Prüfungshistorie
"""

from datetime import datetime, timedelta, date
from app.models.flaschen import Flasche
from app.models.kunden import Kunde
from app import db
import json
from typing import List, Dict, Optional


class FlaschenpruefungsManager:
    """
    Service-Klasse für das Management von Flaschenprüfungen
    """
    
    def __init__(self):
        self.benachrichtigung_vorlauf_tage = 30  # Standard: 30 Tage vor Ablauf
    
    def hole_faellige_pruefungen(self, vorlauf_tage: Optional[int] = None) -> List[Flasche]:
        """
        Holt alle Flaschen, deren Prüfung fällig ist oder bald fällig wird
        
        Args:
            vorlauf_tage: Tage im Voraus, ab wann Prüfung als 'bald fällig' gilt
        
        Returns:
            Liste von Flaschen mit fälliger oder bald fälliger Prüfung
        """
        if vorlauf_tage is None:
            vorlauf_tage = self.benachrichtigung_vorlauf_tage
        
        heute = date.today()
        stichtag = heute + timedelta(days=vorlauf_tage)
        
        # Flaschen mit fälliger Prüfung
        faellige_flaschen = Flasche.query.filter(
            Flasche.ist_aktiv == True,
            db.or_(
                Flasche.naechste_pruefung == None,  # Kein Prüfdatum
                Flasche.naechste_pruefung <= stichtag  # Fällig oder bald fällig
            )
        ).order_by(Flasche.naechste_pruefung).all()
        
        return faellige_flaschen
    
    def hole_nicht_benachrichtigte_pruefungen(self, vorlauf_tage: Optional[int] = None) -> List[Flasche]:
        """
        Holt Flaschen mit fälliger Prüfung, für die noch keine Benachrichtigung gesendet wurde
        """
        if vorlauf_tage is None:
            vorlauf_tage = self.benachrichtigung_vorlauf_tage
        
        heute = date.today()
        stichtag = heute + timedelta(days=vorlauf_tage)
        
        flaschen = Flasche.query.filter(
            Flasche.ist_aktiv == True,
            db.or_(
                Flasche.naechste_pruefung == None,
                Flasche.naechste_pruefung <= stichtag
            ),
            db.or_(
                Flasche.pruefung_benachrichtigt == False,
                Flasche.pruefung_benachrichtigt == None\n            )\n        ).all()\n        \n        return flaschen\n    \n    def markiere_benachrichtigung_gesendet(self, flasche: Flasche, datum: Optional[date] = None):\n        \"\"\"Markiert eine Prüfungsbenachrichtigung als gesendet\"\"\"\n        if datum is None:\n            datum = date.today()\n        \n        flasche.pruefung_benachrichtigt = True\n        flasche.pruefung_benachrichtigung_datum = datum\n        db.session.commit()\n    \n    def aktualisiere_pruefung(self, flasche: Flasche, neues_pruef_datum: date, \n                             protokoll: Optional[str] = None):\n        \"\"\"Aktualisiert Prüfungsdaten nach durchgeführter Prüfung\"\"\"\n        \n        # Berechne nächste Prüfung (Standard: 2.5 Jahre für Druckflaschen)\n        naechste_pruefung = neues_pruef_datum + timedelta(days=912)  # ~2.5 Jahre\n        \n        flasche.pruef_datum = neues_pruef_datum\n        flasche.naechste_pruefung = naechste_pruefung\n        flasche.pruefung_benachrichtigt = False  # Reset für nächste Prüfung\n        flasche.pruefung_benachrichtigung_datum = None\n        \n        if protokoll:\n            flasche.letzte_pruefung_protokoll = protokoll\n        \n        db.session.commit()\n    \n    def erstelle_pruefungs_protokoll(self, flasche: Flasche, pruef_ergebnis: Dict) -> str:\n        \"\"\"Erstellt ein strukturiertes Prüfungsprotokoll als JSON\"\"\"\n        \n        protokoll = {\n            'datum': datetime.now().isoformat(),\n            'flasche_id': flasche.id,\n            'flasche_nummer': flasche.flasche_nummer,\n            'pruef_datum': pruef_ergebnis.get('pruef_datum', date.today()).isoformat(),\n            'pruefer': pruef_ergebnis.get('pruefer', ''),\n            'pruef_stelle': pruef_ergebnis.get('pruef_stelle', ''),\n            'ergebnis': pruef_ergebnis.get('ergebnis', 'bestanden'),\n            'max_druck_getestet': pruef_ergebnis.get('max_druck_getestet'),\n            'gewicht_gemessen': pruef_ergebnis.get('gewicht_gemessen'),\n            'maengel': pruef_ergebnis.get('maengel', []),\n            'bemerkungen': pruef_ergebnis.get('bemerkungen', ''),\n            'naechste_pruefung': pruef_ergebnis.get('naechste_pruefung', ''),\n            'zertifikat_nummer': pruef_ergebnis.get('zertifikat_nummer', '')\n        }\n        \n        return json.dumps(protokoll, ensure_ascii=False, indent=2)\n    \n    def hole_pruefungs_statistiken(self) -> Dict:\n        \"\"\"Erstellt Statistiken über Prüfungsstatus\"\"\"\n        \n        heute = date.today()\n        \n        # Grundzahlen\n        total_flaschen = Flasche.query.filter_by(ist_aktiv=True).count()\n        \n        # Überfällige Prüfungen\n        ueberfaellig = Flasche.query.filter(\n            Flasche.ist_aktiv == True,\n            db.or_(\n                Flasche.naechste_pruefung == None,\n                Flasche.naechste_pruefung < heute\n            )\n        ).count()\n        \n        # Bald fällige Prüfungen (nächste 30 Tage)\n        bald_faellig = Flasche.query.filter(\n            Flasche.ist_aktiv == True,\n            Flasche.naechste_pruefung.between(\n                heute, heute + timedelta(days=30)\n            )\n        ).count()\n        \n        # Gültige Prüfungen\n        gueltig = Flasche.query.filter(\n            Flasche.ist_aktiv == True,\n            Flasche.naechste_pruefung > heute + timedelta(days=30)\n        ).count()\n        \n        # Noch nicht benachrichtigt\n        nicht_benachrichtigt = len(self.hole_nicht_benachrichtigte_pruefungen())\n        \n        return {\n            'total_flaschen': total_flaschen,\n            'ueberfaellig': ueberfaellig,\n            'bald_faellig': bald_faellig,\n            'gueltig': gueltig,\n            'kein_pruef_datum': total_flaschen - (ueberfaellig + bald_faellig + gueltig),\n            'nicht_benachrichtigt': nicht_benachrichtigt,\n            'benachrichtigung_quote': (total_flaschen - nicht_benachrichtigt) / total_flaschen * 100 if total_flaschen > 0 else 0\n        }\n    \n    def generiere_pruefungs_reminder_liste(self) -> List[Dict]:\n        \"\"\"Generiert eine Liste für Prüfungs-Reminder\"\"\"\n        \n        faellige_flaschen = self.hole_faellige_pruefungen()\n        reminder_liste = []\n        \n        for flasche in faellige_flaschen:\n            besitzer = flasche.besitzer if hasattr(flasche, 'besitzer') else None\n            \n            reminder_info = {\n                'flasche_id': flasche.id,\n                'flasche_nummer': flasche.flasche_nummer,\n                'externe_nummer': flasche.externe_flasche_nummer,\n                'seriennummer': flasche.seriennummer,\n                'besitzer': {\n                    'id': besitzer.id if besitzer else None,\n                    'name': besitzer.vollname if besitzer else 'Unbekannt',\n                    'mitgliedsnummer': besitzer.mitgliedsnummer if besitzer else '',\n                    'email': besitzer.email if besitzer else '',\n                    'telefon': besitzer.telefon if besitzer else ''\n                } if besitzer else None,\n                'naechste_pruefung': flasche.naechste_pruefung.isoformat() if flasche.naechste_pruefung else None,\n                'tage_bis_pruefung': flasche.pruefung_faellig_in_tagen,\n                'status': flasche.pruefung_status_text,\n                'ist_ueberfaellig': flasche.pruefung_faellig,\n                'benachrichtigt': flasche.pruefung_benachrichtigt or False,\n                'benachrichtigung_datum': flasche.pruefung_benachrichtigung_datum.isoformat() if hasattr(flasche, 'pruefung_benachrichtigung_datum') and flasche.pruefung_benachrichtigung_datum else None\n            }\n            \n            reminder_liste.append(reminder_info)\n        \n        # Sortiere nach Dringlichkeit\n        reminder_liste.sort(key=lambda x: x['tage_bis_pruefung'] if x['tage_bis_pruefung'] is not None else -999)\n        \n        return reminder_liste\n    \n    def pruefe_flasche_fuer_fuelling(self, flasche: Flasche) -> Dict:\n        \"\"\"Prüft ob eine Flasche für Befüllung geeignet ist\"\"\"\n        \n        pruef_ergebnis = {\n            'flasche_id': flasche.id,\n            'flasche_nummer': flasche.flasche_nummer,\n            'ist_fuellbereit': flasche.ist_fuellbereit,\n            'probleme': [],\n            'warnungen': []\n        }\n        \n        # Prüfung von Grundvoraussetzungen\n        if not flasche.ist_aktiv:\n            pruef_ergebnis['probleme'].append('Flasche ist inaktiv')\n        \n        if flasche.pruefung_faellig:\n            if flasche.pruefung_faellig_in_tagen < -30:\n                pruef_ergebnis['probleme'].append(f'TÜV-Prüfung stark überfällig ({abs(flasche.pruefung_faellig_in_tagen)} Tage)')\n            else:\n                pruef_ergebnis['warnungen'].append('TÜV-Prüfung ist fällig')\n        \n        if not flasche.naechste_pruefung:\n            pruef_ergebnis['probleme'].append('Kein TÜV-Prüfdatum vorhanden')\n        \n        if flasche.max_druck_bar < 200:\n            pruef_ergebnis['probleme'].append(f'Maximaler Druck zu niedrig ({flasche.max_druck_bar} bar)')\n        \n        # Warnungen bei bald fälliger Prüfung\n        if flasche.pruefung_faellig_in_tagen <= 30 and flasche.pruefung_faellig_in_tagen > 0:\n            pruef_ergebnis['warnungen'].append(f'TÜV-Prüfung bald fällig ({flasche.pruefung_faellig_in_tagen} Tage)')\n        \n        # Finales Urteil\n        pruef_ergebnis['kann_gefuellt_werden'] = len(pruef_ergebnis['probleme']) == 0\n        pruef_ergebnis['empfehlung'] = self._generiere_fuell_empfehlung(pruef_ergebnis)\n        \n        return pruef_ergebnis\n    \n    def _generiere_fuell_empfehlung(self, pruef_ergebnis: Dict) -> str:\n        \"\"\"Generiert eine Empfehlung basierend auf der Prüfung\"\"\"\n        \n        if pruef_ergebnis['kann_gefuellt_werden']:\n            if len(pruef_ergebnis['warnungen']) == 0:\n                return 'Flasche kann ohne Bedenken gefüllt werden'\n            else:\n                return 'Flasche kann gefüllt werden, aber Warnungen beachten'\n        else:\n            probleme = ', '.join(pruef_ergebnis['probleme'])\n            return f'Flasche NICHT füllen! Probleme: {probleme}'\n\n\n# Globale Instanz für einfache Verwendung\nflaschenpruefung = FlaschenpruefungsManager()\n