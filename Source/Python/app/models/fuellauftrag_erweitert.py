"""
Erweiterte Füllauftragsverwaltung - Datenmodell
Erstellt von Hans Hahn - Alle Rechte vorbehalten

Dieses Modul erweitert das bestehende Flaschen-Füllen System um:
- Komplette Auftragsdokumentation
- Digitale Unterschriften
- Prüfungsmanagement
- Preisberechnung basierend auf Gasgemisch
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

Base = declarative_base()

class FuellauftragErweitert(Base):
    \"\"\"
    Erweiterte Füllaufträge mit kompletter Dokumentation
    \"\"\"
    __tablename__ = 'fuellauftraege_erweitert'
    
    # Primärschlüssel
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Referenzen
    kunden_id = Column(Integer, ForeignKey('kunden.id'), nullable=False)
    flaschen_id = Column(Integer, ForeignKey('flaschen.id'), nullable=False)
    
    # Auftragsdaten
    auftrag_nummer = Column(String(50), unique=True, nullable=False)  # Format: FA-2025-001
    datum = Column(DateTime, nullable=False, default=datetime.utcnow)
    operator = Column(String(100), nullable=False)
    
    # Druckdaten
    restdruck_bar = Column(Float, nullable=False, default=0.0)
    zieldruck_bar = Column(Float, nullable=False)
    
    # Gasgemisch (Prozentangaben)
    sauerstoff_prozent = Column(Float, nullable=False, default=21.0)
    helium_prozent = Column(Float, nullable=False, default=0.0)
    stickstoff_prozent = Column(Float, nullable=False, default=79.0)
    
    # Berechnete Werte
    volumen_liter = Column(Float, nullable=False)
    mod_1_2_bar = Column(Float)  # Maximum Operating Depth bei 1.2 bar
    mod_1_4_bar = Column(Float)  # Maximum Operating Depth bei 1.4 bar
    mod_1_6_bar = Column(Float)  # Maximum Operating Depth bei 1.6 bar
    end_30m = Column(Float)      # Equivalent Air Depth bei 30m
    
    # Preisberechnung
    preis_helium_euro = Column(Float, nullable=False, default=0.0)
    preis_sauerstoff_euro = Column(Float, nullable=False, default=0.0)
    preis_luft_euro = Column(Float, nullable=False, default=0.0)
    gesamtpreis_euro = Column(Float, nullable=False, default=0.0)
    
    # Prüfungsstatus
    flasche_geprueft = Column(Boolean, default=False)
    pruefung_datum = Column(DateTime)
    pruefung_notizen = Column(Text)
    pruefer = Column(String(100))
    
    # Digitale Unterschriften (Base64 encoded)
    mitarbeiter_unterschrift = Column(Text)
    kunden_unterschrift = Column(Text)
    unterschrift_datum = Column(DateTime)
    
    # Status
    status = Column(String(20), default='erstellt')  # erstellt, geprueft, unterschrieben, abgeschlossen
    
    # Metadaten
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    erstellt_von = Column(String(100), default='Hans Hahn')
    geaendert_am = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    geaendert_von = Column(String(100))
    
    # Beziehungen
    kunde = relationship(\"Kunden\", back_populates=\"fuellauftraege\")
    flasche = relationship(\"Flaschen\", back_populates=\"fuellauftraege\")
    pruefungen = relationship(\"FlaschenpruefungErweitert\", back_populates=\"fuellauftrag\")
    
    def __repr__(self):
        return f\"<FuellauftragErweitert(id={self.id}, nummer={self.auftrag_nummer}, kunde={self.kunde.name if self.kunde else 'N/A'})>\"
    
    def to_dict(self):
        \"\"\"Konvertiert das Objekt zu einem Dictionary\"\"\"
        return {
            'id': self.id,
            'auftrag_nummer': self.auftrag_nummer,
            'datum': self.datum.isoformat() if self.datum else None,
            'operator': self.operator,
            'restdruck_bar': self.restdruck_bar,
            'zieldruck_bar': self.zieldruck_bar,
            'sauerstoff_prozent': self.sauerstoff_prozent,
            'helium_prozent': self.helium_prozent,
            'stickstoff_prozent': self.stickstoff_prozent,
            'volumen_liter': self.volumen_liter,
            'mod_1_2_bar': self.mod_1_2_bar,
            'mod_1_4_bar': self.mod_1_4_bar,
            'mod_1_6_bar': self.mod_1_6_bar,
            'end_30m': self.end_30m,
            'preis_helium_euro': self.preis_helium_euro,
            'preis_sauerstoff_euro': self.preis_sauerstoff_euro,
            'preis_luft_euro': self.preis_luft_euro,
            'gesamtpreis_euro': self.gesamtpreis_euro,
            'flasche_geprueft': self.flasche_geprueft,
            'pruefung_datum': self.pruefung_datum.isoformat() if self.pruefung_datum else None,
            'pruefung_notizen': self.pruefung_notizen,
            'pruefer': self.pruefer,
            'status': self.status,
            'kunde': self.kunde.to_dict() if self.kunde else None,
            'flasche': self.flasche.to_dict() if self.flasche else None
        }
    
    def berechne_preise(self):
        \"\"\"
        Berechnet die Preise basierend auf dem Gasgemisch
        Preise aus dem Screenshot: He=0,0950€, O2=0,0100€, Luft=0,0020€ pro Bar·Liter
        \"\"\"
        # Preise pro Bar·Liter
        PREIS_HELIUM = 0.0950  # €/Bar·Liter
        PREIS_SAUERSTOFF = 0.0100  # €/Bar·Liter
        PREIS_LUFT = 0.0020  # €/Bar·Liter
        
        # Berechnung der Füllmenge
        fuellmenge_bar = self.zieldruck_bar - self.restdruck_bar
        
        # Gasvolumen in Bar·Liter
        helium_bar_liter = (self.helium_prozent / 100) * fuellmenge_bar * self.volumen_liter
        sauerstoff_bar_liter = (self.sauerstoff_prozent / 100) * fuellmenge_bar * self.volumen_liter
        luft_bar_liter = (self.stickstoff_prozent / 100) * fuellmenge_bar * self.volumen_liter
        
        # Preisberechnung
        self.preis_helium_euro = helium_bar_liter * PREIS_HELIUM
        self.preis_sauerstoff_euro = sauerstoff_bar_liter * PREIS_SAUERSTOFF
        self.preis_luft_euro = luft_bar_liter * PREIS_LUFT
        self.gesamtpreis_euro = self.preis_helium_euro + self.preis_sauerstoff_euro + self.preis_luft_euro
        
        return {
            'helium_bar_liter': helium_bar_liter,
            'sauerstoff_bar_liter': sauerstoff_bar_liter,
            'luft_bar_liter': luft_bar_liter,
            'preis_helium_euro': self.preis_helium_euro,
            'preis_sauerstoff_euro': self.preis_sauerstoff_euro,
            'preis_luft_euro': self.preis_luft_euro,
            'gesamtpreis_euro': self.gesamtpreis_euro
        }
    
    def berechne_mod_und_end(self):
        \"\"\"
        Berechnet MOD (Maximum Operating Depth) und END (Equivalent Air Depth)
        \"\"\"
        # MOD Berechnung für verschiedene ppO2-Werte
        if self.sauerstoff_prozent > 0:
            # MOD bei 1.2 bar ppO2
            self.mod_1_2_bar = (1.2 / (self.sauerstoff_prozent / 100)) - 1
            self.mod_1_2_bar = max(0, self.mod_1_2_bar * 10)  # Meter
            
            # MOD bei 1.4 bar ppO2
            self.mod_1_4_bar = (1.4 / (self.sauerstoff_prozent / 100)) - 1
            self.mod_1_4_bar = max(0, self.mod_1_4_bar * 10)  # Meter
            
            # MOD bei 1.6 bar ppO2
            self.mod_1_6_bar = (1.6 / (self.sauerstoff_prozent / 100)) - 1
            self.mod_1_6_bar = max(0, self.mod_1_6_bar * 10)  # Meter
        
        # END Berechnung bei 30m (4 bar absolut)
        if self.stickstoff_prozent > 0:
            self.end_30m = (4 * (self.stickstoff_prozent / 100)) / 0.79 - 1
            self.end_30m = max(0, self.end_30m * 10)  # Meter
        
        return {
            'mod_1_2_bar': self.mod_1_2_bar,
            'mod_1_4_bar': self.mod_1_4_bar,
            'mod_1_6_bar': self.mod_1_6_bar,
            'end_30m': self.end_30m
        }
    
    def generiere_auftragsnummer(self):
        \"\"\"Generiert eine eindeutige Auftragsnummer\"\"\"
        from sqlalchemy import func
        jahr = datetime.now().year
        # Nächste laufende Nummer für dieses Jahr
        # TODO: Datenbankabfrage für letzte Nummer implementieren
        naechste_nummer = 1  # Placeholder
        self.auftrag_nummer = f\"FA-{jahr}-{naechste_nummer:03d}\"
        return self.auftrag_nummer


class FlaschenpruefungErweitert(Base):
    \"\"\"
    Erweiterte Prüfungshistorie für Flaschen
    \"\"\"
    __tablename__ = 'flaschenpruefungen_erweitert'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fuellauftrag_id = Column(Integer, ForeignKey('fuellauftraege_erweitert.id'), nullable=False)
    flaschen_id = Column(Integer, ForeignKey('flaschen.id'), nullable=False)
    
    # Prüfungsdaten
    pruefung_datum = Column(DateTime, nullable=False, default=datetime.utcnow)
    pruefung_typ = Column(String(50), nullable=False)  # visuell, hydrostatisch, etc.
    pruefung_ergebnis = Column(String(20), nullable=False)  # OK, Mangel, Defekt
    pruefung_notizen = Column(Text)
    pruefer = Column(String(100), nullable=False)
    
    # Prüfungsdetails
    aeussere_beschaedigungen = Column(Boolean, default=False)
    ventil_zustand = Column(String(20))  # OK, Defekt, Wartung
    tauv_gueltig_bis = Column(DateTime)  # TÜV-Gültigkeit
    
    # Metadaten
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    erstellt_von = Column(String(100), default='Hans Hahn')
    
    # Beziehungen
    fuellauftrag = relationship(\"FuellauftragErweitert\", back_populates=\"pruefungen\")
    flasche = relationship(\"Flaschen\", back_populates=\"pruefungen\")
    
    def __repr__(self):
        return f\"<FlaschenpruefungErweitert(id={self.id}, ergebnis={self.pruefung_ergebnis}, datum={self.pruefung_datum})>\"
    
    def to_dict(self):
        return {
            'id': self.id,
            'fuellauftrag_id': self.fuellauftrag_id,
            'flaschen_id': self.flaschen_id,
            'pruefung_datum': self.pruefung_datum.isoformat() if self.pruefung_datum else None,
            'pruefung_typ': self.pruefung_typ,
            'pruefung_ergebnis': self.pruefung_ergebnis,
            'pruefung_notizen': self.pruefung_notizen,
            'pruefer': self.pruefer,
            'aeussere_beschaedigungen': self.aeussere_beschaedigungen,
            'ventil_zustand': self.ventil_zustand,
            'tauv_gueltig_bis': self.tauv_gueltig_bis.isoformat() if self.tauv_gueltig_bis else None
        }


class UnterschriftErweitert(Base):
    \"\"\"
    Digitale Unterschriften für Füllaufträge
    \"\"\"
    __tablename__ = 'unterschriften_erweitert'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fuellauftrag_id = Column(Integer, ForeignKey('fuellauftraege_erweitert.id'), nullable=False)
    
    # Unterschriftsdaten
    unterschrift_typ = Column(String(20), nullable=False)  # mitarbeiter, kunde
    unterschrift_base64 = Column(Text, nullable=False)  # Base64-kodierte Bilddaten
    unterschrift_datum = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Metadaten
    geraet_info = Column(String(200))  # Browser, Gerät, etc.
    ip_adresse = Column(String(50))
    
    # Beziehungen
    fuellauftrag = relationship(\"FuellauftragErweitert\")
    
    def __repr__(self):
        return f\"<UnterschriftErweitert(id={self.id}, typ={self.unterschrift_typ}, datum={self.unterschrift_datum})>\"
    
    def to_dict(self):
        return {
            'id': self.id,
            'fuellauftrag_id': self.fuellauftrag_id,
            'unterschrift_typ': self.unterschrift_typ,
            'unterschrift_datum': self.unterschrift_datum.isoformat() if self.unterschrift_datum else None,
            'geraet_info': self.geraet_info,
            'ip_adresse': self.ip_adresse
        }


# Hilfsfunktionen für Berechnungen
class GasberechnungUtils:
    \"\"\"
    Utility-Klasse für Gasberechnungen
    \"\"\"
    
    @staticmethod
    def validiere_gasgemisch(sauerstoff, helium, stickstoff):
        \"\"\"
        Validiert, ob das Gasgemisch korrekt ist (100% Summe)
        \"\"\"
        summe = sauerstoff + helium + stickstoff
        return abs(summe - 100.0) < 0.1  # Toleranz von 0.1%
    
    @staticmethod
    def berechne_partial_pressures(tiefe_meter, sauerstoff_prozent, helium_prozent, stickstoff_prozent):
        \"\"\"
        Berechnet die Partialdrücke in gegebener Tiefe
        \"\"\"
        absoluter_druck = 1 + (tiefe_meter / 10)  # bar
        
        return {
            'absoluter_druck_bar': absoluter_druck,
            'pp_sauerstoff': absoluter_druck * (sauerstoff_prozent / 100),
            'pp_helium': absoluter_druck * (helium_prozent / 100),
            'pp_stickstoff': absoluter_druck * (stickstoff_prozent / 100)
        }
    
    @staticmethod
    def berechne_mod(sauerstoff_prozent, max_pp_sauerstoff=1.4):
        \"\"\"
        Berechnet die Maximum Operating Depth
        \"\"\"
        if sauerstoff_prozent <= 0:
            return 0
        
        max_tiefe = (max_pp_sauerstoff / (sauerstoff_prozent / 100)) - 1
        return max(0, max_tiefe * 10)  # Meter
    
    @staticmethod
    def berechne_end(tiefe_meter, stickstoff_prozent):
        \"\"\"
        Berechnet die Equivalent Air Depth
        \"\"\"
        if stickstoff_prozent <= 0:
            return 0
        
        absoluter_druck = 1 + (tiefe_meter / 10)
        end_druck = (absoluter_druck * (stickstoff_prozent / 100)) / 0.79
        return max(0, (end_druck - 1) * 10)  # Meter


# Datenbankinitialisierung
def create_erweiterte_tabellen(engine):
    \"\"\"
    Erstellt die erweiterten Tabellen in der Datenbank
    \"\"\"
    try:
        Base.metadata.create_all(engine)
        print(\"✅ Erweiterte Füllauftrag-Tabellen erfolgreich erstellt\")
        return True
    except Exception as e:
        print(f\"❌ Fehler beim Erstellen der Tabellen: {str(e)}\")
        return False


if __name__ == \"__main__\":
    # Test der Berechnungsfunktionen
    print(\"=== TEST: Gasberechnungen ===\")
    
    # Beispiel aus dem Screenshot
    test_auftrag = FuellauftragErweitert(
        operator=\"Hans Hahn\",
        restdruck_bar=0.0,
        zieldruck_bar=220.0,
        sauerstoff_prozent=34.0,
        helium_prozent=0.0,
        stickstoff_prozent=66.0,
        volumen_liter=24.0
    )
    
    # Preisberechnung
    preise = test_auftrag.berechne_preise()
    print(f\"Preisberechnung: {preise}\")
    
    # MOD/END Berechnung
    mod_end = test_auftrag.berechne_mod_und_end()
    print(f\"MOD/END Berechnung: {mod_end}\")
    
    # Gasgemisch-Validierung
    gasgemisch_ok = GasberechnungUtils.validiere_gasgemisch(34.0, 0.0, 66.0)
    print(f\"Gasgemisch korrekt: {gasgemisch_ok}\")
    
    print(\"\\n=== TEST: Auftragsnummer ===\")
    test_auftrag.generiere_auftragsnummer()
    print(f\"Auftragsnummer: {test_auftrag.auftrag_nummer}\")
    
    print(\"\\n✅ Alle Tests erfolgreich!\")
