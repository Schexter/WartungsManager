# Erweiterte Patronenverwaltung Models für WartungsManager
# Neue Struktur für Vorbereitung, Einkauf und Wechsel

from datetime import datetime
from app import db

class PatroneVorbereitung(db.Model):
    """
    Model für vorbereitete Patronen
    
    Dokumentiert wer welche Patrone wann vorbereitet/gefüllt hat
    """
    
    __tablename__ = 'patrone_vorbereitung'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Vorbereitung-Info
    vorbereitet_von = db.Column(db.String(100), nullable=False)
    vorbereitet_am = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Patronen-Details
    patrone_typ = db.Column(db.String(50), nullable=False)  # 'Molekularsieb', 'Kohle'
    patrone_nummer = db.Column(db.String(20), nullable=True)  # z.B. '1', '2' für Molekularsieb
    charge_nummer = db.Column(db.String(50), nullable=False)
    
    # Gewicht und Qualität
    gewicht_vor_fuellen = db.Column(db.Float, nullable=True)  # kg
    gewicht_nach_fuellen = db.Column(db.Float, nullable=True)  # kg
    material_verwendet = db.Column(db.String(200), nullable=True)  # Was wurde eingefüllt
    
    # Status
    ist_bereit = db.Column(db.Boolean, nullable=False, default=True)
    ist_verwendet = db.Column(db.Boolean, nullable=False, default=False)
    verwendung_datum = db.Column(db.DateTime, nullable=True)
    
    # Etikettendruck
    etikett_gedruckt = db.Column(db.Boolean, nullable=False, default=False)
    etikett_gedruckt_am = db.Column(db.DateTime, nullable=True)
    
    # Notizen
    notizen = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PatroneVorbereitung {self.id}: {self.patrone_typ} - {self.charge_nummer}>'
    
    def to_dict(self):
        """Konvertiert zu Dictionary für JSON API"""
        return {
            'id': self.id,
            'vorbereitet_von': self.vorbereitet_von,
            'vorbereitet_am': self.vorbereitet_am.isoformat() if self.vorbereitet_am else None,
            'patrone_typ': self.patrone_typ,
            'patrone_nummer': self.patrone_nummer,
            'charge_nummer': self.charge_nummer,
            'gewicht_vor_fuellen': self.gewicht_vor_fuellen,
            'gewicht_nach_fuellen': self.gewicht_nach_fuellen,
            'material_verwendet': self.material_verwendet,
            'ist_bereit': self.ist_bereit,
            'ist_verwendet': self.ist_verwendet,
            'verwendung_datum': self.verwendung_datum.isoformat() if self.verwendung_datum else None,
            'etikett_gedruckt': self.etikett_gedruckt,
            'etikett_gedruckt_am': self.etikett_gedruckt_am.isoformat() if self.etikett_gedruckt_am else None,
            'notizen': self.notizen
        }
    
    @staticmethod
    def get_verfuegbare_patronen(patrone_typ=None):
        """Gibt verfügbare (nicht verwendete) Patronen zurück"""
        query = PatroneVorbereitung.query.filter_by(
            ist_bereit=True, 
            ist_verwendet=False
        )
        
        if patrone_typ:
            query = query.filter_by(patrone_typ=patrone_typ)
            
        return query.order_by(PatroneVorbereitung.vorbereitet_am.asc()).all()


class PatroneEinkauf(db.Model):
    """
    Model für gekaufte Patronen
    
    Dokumentiert Einkäufe von Patronenmaterial und Lieferanten
    """
    
    __tablename__ = 'patrone_einkauf'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Einkauf-Info
    eingekauft_von = db.Column(db.String(100), nullable=False)
    einkauf_datum = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    lieferant = db.Column(db.String(200), nullable=False)
    
    # Produkt-Details
    produkt_name = db.Column(db.String(200), nullable=False)
    produkt_typ = db.Column(db.String(50), nullable=False)  # 'Molekularsieb', 'Kohle', etc.
    menge = db.Column(db.Float, nullable=False)  # Anzahl/Gewicht
    einheit = db.Column(db.String(20), nullable=False)  # 'kg', 'Stück', etc.
    
    # Preise
    einzelpreis = db.Column(db.Float, nullable=True)
    gesamtpreis = db.Column(db.Float, nullable=True)
    waehrung = db.Column(db.String(10), nullable=False, default='EUR')
    
    # Lieferung
    lieferdatum = db.Column(db.DateTime, nullable=True)
    ist_geliefert = db.Column(db.Boolean, nullable=False, default=False)
    
    # Qualität
    charge_nummer_lieferant = db.Column(db.String(100), nullable=True)
    haltbarkeitsdatum = db.Column(db.DateTime, nullable=True)
    qualitaets_zertifikat = db.Column(db.String(200), nullable=True)  # Dateipfad
    
    # Etikettendruck
    kleber_gedruckt = db.Column(db.Boolean, nullable=False, default=False)
    kleber_gedruckt_am = db.Column(db.DateTime, nullable=True)
    
    # Lagerung
    lagerort = db.Column(db.String(100), nullable=True)
    verbraucht_menge = db.Column(db.Float, nullable=False, default=0.0)
    verbleibende_menge = db.Column(db.Float, nullable=True)
    
    # Status
    ist_aktiv = db.Column(db.Boolean, nullable=False, default=True)
    notizen = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PatroneEinkauf {self.id}: {self.produkt_name} - {self.lieferant}>'
    
    def to_dict(self):
        """Konvertiert zu Dictionary für JSON API"""
        return {
            'id': self.id,
            'eingekauft_von': self.eingekauft_von,
            'einkauf_datum': self.einkauf_datum.isoformat() if self.einkauf_datum else None,
            'lieferant': self.lieferant,
            'produkt_name': self.produkt_name,
            'produkt_typ': self.produkt_typ,
            'menge': self.menge,
            'einheit': self.einheit,
            'einzelpreis': self.einzelpreis,
            'gesamtpreis': self.gesamtpreis,
            'waehrung': self.waehrung,
            'lieferdatum': self.lieferdatum.isoformat() if self.lieferdatum else None,
            'ist_geliefert': self.ist_geliefert,
            'charge_nummer_lieferant': self.charge_nummer_lieferant,
            'haltbarkeitsdatum': self.haltbarkeitsdatum.isoformat() if self.haltbarkeitsdatum else None,
            'qualitaets_zertifikat': self.qualitaets_zertifikat,
            'kleber_gedruckt': self.kleber_gedruckt,
            'kleber_gedruckt_am': self.kleber_gedruckt_am.isoformat() if self.kleber_gedruckt_am else None,
            'lagerort': self.lagerort,
            'verbraucht_menge': self.verbraucht_menge,
            'verbleibende_menge': self.verbleibende_menge,
            'ist_aktiv': self.ist_aktiv,
            'notizen': self.notizen
        }
    
    @property
    def verbleibende_menge_berechnet(self):
        """Berechnet verbleibende Menge"""
        if self.verbleibende_menge is not None:
            return self.verbleibende_menge
        return self.menge - self.verbraucht_menge


class PatroneWechselProtokoll(db.Model):
    """
    Erweiterte Dokumentation von Patronenwechseln
    
    Verbindet vorbereitete und gekaufte Patronen mit Wechselprotokoll
    """
    
    __tablename__ = 'patrone_wechsel_protokoll'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Referenz zum ursprünglichen Patronenwechsel
    patronenwechsel_id = db.Column(db.Integer, db.ForeignKey('patronenwechsel.id'), nullable=False)
    
    # Wechsel-Details
    gewechselt_von = db.Column(db.String(100), nullable=False)
    wechsel_datum = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Verwendete vorbereitete Patrone
    vorbereitung_id = db.Column(db.Integer, db.ForeignKey('patrone_vorbereitung.id'), nullable=True)
    
    # Gewichte beim Wechsel
    alte_patrone_gewicht = db.Column(db.Float, nullable=True)  # kg
    neue_patrone_gewicht = db.Column(db.Float, nullable=True)  # kg
    
    # Position/Art der Patrone
    position = db.Column(db.String(50), nullable=False)  # 'Molekularsieb_1', 'Molekularsieb_2', 'Kohle'
    
    # Zustand
    alte_patrone_zustand = db.Column(db.String(200), nullable=True)  # Sichtbare Probleme
    wechsel_grund = db.Column(db.String(200), nullable=True)  # Planmäßig, Defekt, etc.
    
    # Betriebsstunden
    betriebsstunden_alte_patrone = db.Column(db.Float, nullable=True)
    
    # Entsorgung
    alte_patrone_entsorgt = db.Column(db.Boolean, nullable=False, default=False)
    entsorgung_datum = db.Column(db.DateTime, nullable=True)
    entsorgung_art = db.Column(db.String(100), nullable=True)
    
    # Notizen
    notizen = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patronenwechsel = db.relationship('Patronenwechsel', backref='wechsel_protokolle')
    vorbereitung = db.relationship('PatroneVorbereitung', backref='verwendungen')
    
    def __repr__(self):
        return f'<PatroneWechselProtokoll {self.id}: {self.position} - {self.gewechselt_von}>'
    
    def to_dict(self):
        """Konvertiert zu Dictionary für JSON API"""
        return {
            'id': self.id,
            'patronenwechsel_id': self.patronenwechsel_id,
            'gewechselt_von': self.gewechselt_von,
            'wechsel_datum': self.wechsel_datum.isoformat() if self.wechsel_datum else None,
            'vorbereitung_id': self.vorbereitung_id,
            'alte_patrone_gewicht': self.alte_patrone_gewicht,
            'neue_patrone_gewicht': self.neue_patrone_gewicht,
            'position': self.position,
            'alte_patrone_zustand': self.alte_patrone_zustand,
            'wechsel_grund': self.wechsel_grund,
            'betriebsstunden_alte_patrone': self.betriebsstunden_alte_patrone,
            'alte_patrone_entsorgt': self.alte_patrone_entsorgt,
            'entsorgung_datum': self.entsorgung_datum.isoformat() if self.entsorgung_datum else None,
            'entsorgung_art': self.entsorgung_art,
            'notizen': self.notizen,
            'vorbereitung': self.vorbereitung.to_dict() if self.vorbereitung else None
        }
