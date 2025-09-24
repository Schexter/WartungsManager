# SQLAlchemy Models für Füllvorgänge
from datetime import datetime, timedelta
from app import db

class Fuellvorgang(db.Model):
    """
    Model für Füllvorgänge mit Touch-UI optimierter Zeiterfassung
    
    Erfasst:
    - Start/Stop Zeiten
    - Automatische Dauer-Berechnung  
    - Operator-Information
    - Betriebsstunden-Tracking
    """
    
    __tablename__ = 'fuellvorgaenge'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Zeiterfassung
    start_zeit = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_zeit = db.Column(db.DateTime, nullable=True)
    dauer_minuten = db.Column(db.Integer, nullable=True)  # Automatisch berechnet
    
    # Operator Information  
    operator = db.Column(db.String(100), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='laufend')  # laufend, beendet, abgebrochen
    
    # Zusätzliche Informationen
    notizen = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Fuellvorgang {self.id}: {self.start_zeit} - {self.status}>'
    
    @property
    def ist_aktiv(self):
        """Prüft ob Füllvorgang noch läuft"""
        return self.status == 'laufend' and self.end_zeit is None
    
    @property
    def dauer_stunden(self):
        """Berechnet Dauer in Stunden (float)"""
        if self.dauer_minuten:
            return round(self.dauer_minuten / 60.0, 2)
        return 0.0
    
    @property
    def aktuelle_dauer(self):
        """Berechnet aktuelle Dauer für laufende Füllungen"""
        if self.ist_aktiv:
            delta = datetime.utcnow() - self.start_zeit
            return delta.total_seconds() / 60  # Minuten
        return self.dauer_minuten or 0
    
    def beenden(self, end_zeit=None):
        """Beendet den Füllvorgang"""
        if end_zeit is None:
            end_zeit = datetime.utcnow()
        
        self.end_zeit = end_zeit
        self.status = 'beendet'
        
        # Dauer berechnen
        delta = self.end_zeit - self.start_zeit
        self.dauer_minuten = int(delta.total_seconds() / 60)
        
        self.updated_at = datetime.utcnow()
    
    def abbrechen(self, grund="Manuell abgebrochen"):
        """Bricht den Füllvorgang ab"""
        self.end_zeit = datetime.utcnow()
        self.status = 'abgebrochen'
        self.notizen = self.notizen or ""
        self.notizen += f"\nAbbruch: {grund}"
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_aktiver_fuellvorgang():
        """Gibt den aktuell laufenden Füllvorgang zurück"""
        return Fuellvorgang.query.filter_by(status='laufend').first()
    
    @staticmethod
    def get_gesamt_betriebsstunden():
        """Berechnet Gesamt-Betriebsstunden aller Füllvorgänge"""
        result = db.session.query(
            db.func.sum(Fuellvorgang.dauer_minuten)
        ).filter(
            Fuellvorgang.status == 'beendet'
        ).scalar()
        
        return round((result or 0) / 60.0, 1)  # Stunden mit 1 Dezimalstelle
    
    @staticmethod
    def get_betriebsstunden_seit(datum):
        """Betriebsstunden seit bestimmtem Datum"""
        result = db.session.query(
            db.func.sum(Fuellvorgang.dauer_minuten)
        ).filter(
            Fuellvorgang.status == 'beendet',
            Fuellvorgang.start_zeit >= datum
        ).scalar()
        
        return round((result or 0) / 60.0, 1)
    
    @staticmethod
    def get_statistiken():
        """Gibt umfassende Statistiken zurück"""
        total_count = Fuellvorgang.query.filter_by(status='beendet').count()
        total_hours = Fuellvorgang.get_gesamt_betriebsstunden()
        
        # Durchschnittliche Füllzeit
        avg_duration = db.session.query(
            db.func.avg(Fuellvorgang.dauer_minuten)
        ).filter(
            Fuellvorgang.status == 'beendet'
        ).scalar()
        
        avg_hours = round((avg_duration or 0) / 60.0, 2)
        
        return {
            'total_fuellungen': total_count,
            'total_betriebsstunden': total_hours,
            'durchschnitt_stunden': avg_hours,
            'aktiver_vorgang': Fuellvorgang.get_aktiver_fuellvorgang() is not None
        }

    def to_dict(self):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        return {
            'id': self.id,
            'start_zeit': self.start_zeit.isoformat() if self.start_zeit else None,
            'end_zeit': self.end_zeit.isoformat() if self.end_zeit else None,
            'dauer_minuten': self.dauer_minuten,
            'dauer_stunden': self.dauer_stunden,
            'operator': self.operator,
            'status': self.status,
            'ist_aktiv': self.ist_aktiv,
            'notizen': self.notizen
        }
