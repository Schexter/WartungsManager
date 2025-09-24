# SQLAlchemy Model für Wartungen
from datetime import datetime, timedelta
from app import db

class Wartung(db.Model):
    """
    Model für Wartungsintervalle und -durchführungen
    
    Erfasst:
    - Wartungstyp (Filter, Öl, etc.)
    - Durchführungsdatum
    - Nächste fällige Wartung
    - Verantwortliche Person
    """
    
    __tablename__ = 'wartungen'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Wartungsdetails
    typ = db.Column(db.String(50), nullable=False)  # Filter, Öl, Inspektion
    datum = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    durchgefuehrt_von = db.Column(db.String(100), nullable=False)
    
    # Intervall Management
    naechste_faellig = db.Column(db.DateTime, nullable=True)
    intervall_tage = db.Column(db.Integer, default=30)  # Standard: 30 Tage
    
    # Zusätzliche Informationen
    notizen = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='durchgefuehrt')  # geplant, durchgefuehrt, überfällig
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Wartung {self.typ}: {self.datum}>'
    
    @property
    def ist_ueberfaellig(self):
        """Prüft ob Wartung überfällig ist"""
        if self.naechste_faellig:
            return datetime.utcnow() > self.naechste_faellig
        return False
    
    @property
    def tage_bis_faellig(self):
        """Berechnet Tage bis zur nächsten Wartung"""
        if self.naechste_faellig:
            delta = self.naechste_faellig - datetime.utcnow()
            return delta.days
        return None
    
    def naechste_wartung_setzen(self, tage=None):
        """Setzt das nächste Wartungsdatum"""
        if tage is None:
            tage = self.intervall_tage
        
        self.naechste_faellig = self.datum + timedelta(days=tage)
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_ueberfaellige_wartungen():
        """Gibt alle überfälligen Wartungen zurück"""
        now = datetime.utcnow()
        return Wartung.query.filter(
            Wartung.naechste_faellig < now,
            Wartung.status != 'durchgefuehrt'
        ).all()
    
    @staticmethod
    def get_wartungen_diese_woche():
        """Wartungen die diese Woche fällig sind"""
        now = datetime.utcnow()
        week_end = now + timedelta(days=7)
        
        return Wartung.query.filter(
            Wartung.naechste_faellig.between(now, week_end)
        ).all()
    
    def to_dict(self):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        return {
            'id': self.id,
            'typ': self.typ,
            'datum': self.datum.isoformat() if self.datum else None,
            'durchgefuehrt_von': self.durchgefuehrt_von,
            'naechste_faellig': self.naechste_faellig.isoformat() if self.naechste_faellig else None,
            'tage_bis_faellig': self.tage_bis_faellig,
            'ist_ueberfaellig': self.ist_ueberfaellig,
            'status': self.status,
            'notizen': self.notizen
        }
