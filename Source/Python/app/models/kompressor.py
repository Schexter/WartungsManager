# SQLAlchemy Model für Kompressor-Betrieb
from datetime import datetime, timedelta
from app import db

class KompressorBetrieb(db.Model):
    """
    Model für Kompressor-Betriebsstunden-Tracking
    
    Erfasst:
    - Betriebszeiten (Start/Stop)
    - Öl-Tests bei Inbetriebnahme
    - Verantwortliche Personen
    - Automatische Betriebsstunden-Berechnung
    """
    
    __tablename__ = 'kompressor_betrieb'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Betriebszeiten
    start_zeit = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_zeit = db.Column(db.DateTime, nullable=True)
    betriebsdauer_minuten = db.Column(db.Integer, nullable=True)  # Automatisch berechnet
    
    # Öl-Test Information (bei Start)
    oel_getestet = db.Column(db.Boolean, nullable=False, default=False)
    oel_test_ergebnis = db.Column(db.String(10), nullable=True)  # 'OK', 'NOK'
    oel_tester = db.Column(db.String(100), nullable=True)  # Wer hat getestet
    oel_tester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Verantwortlicher (Füller)
    fueller = db.Column(db.String(100), nullable=False)
    fueller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='laufend')  # laufend, beendet, notaus
    
    # Zusätzliche Informationen
    notizen = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tester_user = db.relationship('User', foreign_keys=[oel_tester_id], backref='oel_tests')
    fueller_user = db.relationship('User', foreign_keys=[fueller_id], backref='kompressor_bedienungen')
    
    def __repr__(self):
        return f'<KompressorBetrieb {self.id}: {self.start_zeit} - {self.status}>'
    
    @property
    def ist_aktiv(self):
        """Prüft ob Kompressor aktuell läuft"""
        return self.status == 'laufend' and self.end_zeit is None
    
    @property
    def betriebsdauer_stunden(self):
        """Berechnet Betriebsdauer in Stunden (float)"""
        if self.betriebsdauer_minuten:
            return round(self.betriebsdauer_minuten / 60.0, 2)
        return 0.0
    
    @property
    def aktuelle_betriebsdauer(self):
        """Berechnet aktuelle Betriebsdauer für laufende Kompressoren"""
        if self.ist_aktiv:
            delta = datetime.utcnow() - self.start_zeit
            return delta.total_seconds() / 60  # Minuten
        return self.betriebsdauer_minuten or 0
    
    @property
    def oel_status_text(self):
        """Gibt lesbaren Öl-Status zurück"""
        if not self.oel_getestet:
            return "Nicht getestet"
        return f"{self.oel_test_ergebnis} (von {self.oel_tester})"
    
    def kompressor_ausschalten(self, end_zeit=None, notizen=None):
        """Schaltet Kompressor aus und berechnet Betriebszeit"""
        if end_zeit is None:
            end_zeit = datetime.utcnow()
        
        self.end_zeit = end_zeit
        self.status = 'beendet'
        
        # Betriebsdauer berechnen
        delta = self.end_zeit - self.start_zeit
        self.betriebsdauer_minuten = int(delta.total_seconds() / 60)
        
        if notizen:
            self.notizen = self.notizen or ""
            self.notizen += f"\n{notizen}"
        
        self.updated_at = datetime.utcnow()
    
    def notaus(self, grund="Notaus ausgelöst"):
        """Not-Aus des Kompressors"""
        self.end_zeit = datetime.utcnow()
        self.status = 'notaus'
        self.notizen = self.notizen or ""
        self.notizen += f"\nNOTAUS: {grund}"
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_aktiver_kompressor():
        """Gibt den aktuell laufenden Kompressor zurück"""
        return KompressorBetrieb.query.filter_by(status='laufend').first()
    
    @staticmethod
    def ist_kompressor_an():
        """Prüft ob Kompressor aktuell läuft"""
        return KompressorBetrieb.get_aktiver_kompressor() is not None
    
    @staticmethod
    def get_gesamt_betriebsstunden():
        """Berechnet Gesamt-Betriebsstunden aller Zyklen"""
        result = db.session.query(
            db.func.sum(KompressorBetrieb.betriebsdauer_minuten)
        ).filter(
            KompressorBetrieb.status.in_(['beendet', 'notaus'])
        ).scalar()
        
        return round((result or 0) / 60.0, 1)  # Stunden mit 1 Dezimalstelle
    
    @staticmethod
    def get_betriebsstunden_seit(datum):
        """Betriebsstunden seit bestimmtem Datum"""
        result = db.session.query(
            db.func.sum(KompressorBetrieb.betriebsdauer_minuten)
        ).filter(
            KompressorBetrieb.status.in_(['beendet', 'notaus']),
            KompressorBetrieb.start_zeit >= datum
        ).scalar()
        
        return round((result or 0) / 60.0, 1)
    
    @staticmethod
    def get_oel_test_statistiken():
        """Gibt Öl-Test Statistiken zurück"""
        total = KompressorBetrieb.query.count()
        getestet = KompressorBetrieb.query.filter_by(oel_getestet=True).count()
        ok_tests = KompressorBetrieb.query.filter_by(oel_test_ergebnis='OK').count()
        nok_tests = KompressorBetrieb.query.filter_by(oel_test_ergebnis='NOK').count()
        
        return {
            'total_starts': total,
            'oel_getestet': getestet,
            'oel_ok': ok_tests,
            'oel_nok': nok_tests,
            'test_quote': round((getestet / total * 100) if total > 0 else 0, 1)
        }
    
    @staticmethod
    def get_kompressor_statistiken():
        """Gibt umfassende Kompressor-Statistiken zurück"""
        total_zyklen = KompressorBetrieb.query.filter(
            KompressorBetrieb.status.in_(['beendet', 'notaus'])
        ).count()
        
        gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
        
        # Durchschnittliche Laufzeit
        avg_duration = db.session.query(
            db.func.avg(KompressorBetrieb.betriebsdauer_minuten)
        ).filter(
            KompressorBetrieb.status.in_(['beendet', 'notaus'])
        ).scalar()
        
        avg_stunden = round((avg_duration or 0) / 60.0, 2)
        
        # Öl-Statistiken
        oel_stats = KompressorBetrieb.get_oel_test_statistiken()
        
        return {
            'total_zyklen': total_zyklen,
            'gesamt_betriebsstunden': gesamt_stunden,
            'durchschnitt_laufzeit': avg_stunden,
            'aktuell_an': KompressorBetrieb.ist_kompressor_an(),
            'oel_statistiken': oel_stats
        }

    def to_dict(self):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        return {
            'id': self.id,
            'start_zeit': self.start_zeit.isoformat() if self.start_zeit else None,
            'end_zeit': self.end_zeit.isoformat() if self.end_zeit else None,
            'betriebsdauer_minuten': self.betriebsdauer_minuten,
            'betriebsdauer_stunden': self.betriebsdauer_stunden,
            'oel_getestet': self.oel_getestet,
            'oel_test_ergebnis': self.oel_test_ergebnis,
            'oel_tester': self.oel_tester,
            'oel_status_text': self.oel_status_text,
            'fueller': self.fueller,
            'status': self.status,
            'ist_aktiv': self.ist_aktiv,
            'notizen': self.notizen
        }
