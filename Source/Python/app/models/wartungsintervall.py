# Wartungsintervall Model für WartungsManager
from datetime import datetime
from app import db

class Wartungsintervall(db.Model):
    """
    Model für Wartungsintervall-Tracking
    
    Trennt zwischen:
    - Gesamt-Betriebszeit (niemals zurücksetzen)
    - Wartungsintervall (nach Patronenwechsel zurücksetzen)
    """
    
    __tablename__ = 'wartungsintervall'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Intervall-Information
    name = db.Column(db.String(100), nullable=False)  # z.B. "Patronenwechsel", "Hauptwartung"
    start_datum = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reset_grund = db.Column(db.String(200), nullable=True)  # Grund für Reset
    
    # Betriebsstunden-Zähler
    startstand_stunden = db.Column(db.Float, nullable=False, default=0.0)  # Stand bei Intervall-Start
    
    # Wartungsparameter
    wartungsintervall_stunden = db.Column(db.Float, nullable=False, default=100.0)  # Nach x Stunden Wartung
    naechste_wartung_bei = db.Column(db.Float, nullable=True)  # Automatisch berechnet
    
    # Status und Dokumentation
    ist_aktiv = db.Column(db.Boolean, nullable=False, default=True)
    durchgefuehrt_von = db.Column(db.String(100), nullable=True)
    notizen = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Wartungsintervall {self.id}: {self.name} - {self.start_datum}>'
    
    @property
    def intervall_betriebsstunden(self):
        """Betriebsstunden seit Start dieses Intervalls"""
        from app.models.kompressor import KompressorBetrieb
        
        # Alle Betriebsstunden seit Intervall-Start
        gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
        return max(0.0, gesamt_stunden - self.startstand_stunden)
    
    @property
    def wartung_faellig_in(self):
        """Stunden bis zur nächsten Wartung"""
        return max(0.0, self.wartungsintervall_stunden - self.intervall_betriebsstunden)
    
    @property
    def ist_wartung_faellig(self):
        """Prüft ob Wartung fällig ist"""
        return self.wartung_faellig_in <= 0
    
    @staticmethod
    def get_aktuelles_intervall():
        """Gibt das aktuelle (aktive) Wartungsintervall zurück"""
        return Wartungsintervall.query.filter_by(ist_aktiv=True).first()
    
    @staticmethod
    def neues_intervall_starten(name, grund, wartungsintervall_stunden=100.0, durchgefuehrt_von=None):
        """Startet ein neues Wartungsintervall (nach Patronenwechsel)"""
        from app.models.kompressor import KompressorBetrieb
        
        # Altes Intervall deaktivieren
        altes_intervall = Wartungsintervall.get_aktuelles_intervall()
        if altes_intervall:
            altes_intervall.ist_aktiv = False
            altes_intervall.updated_at = datetime.utcnow()
        
        # Aktueller Gesamt-Stand
        gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
        
        # Neues Intervall erstellen
        neues_intervall = Wartungsintervall(
            name=name,
            reset_grund=grund,
            startstand_stunden=gesamt_stunden,
            wartungsintervall_stunden=wartungsintervall_stunden,
            naechste_wartung_bei=gesamt_stunden + wartungsintervall_stunden,
            durchgefuehrt_von=durchgefuehrt_von,
            ist_aktiv=True
        )
        
        db.session.add(neues_intervall)
        db.session.commit()
        
        return neues_intervall
    
    @staticmethod
    def get_wartungsstatistiken():
        """Gibt Wartungsstatistiken zurück"""
        aktuelles = Wartungsintervall.get_aktuelles_intervall()
        
        if not aktuelles:
            return {
                'hat_intervall': False,
                'intervall_stunden': 0.0,
                'wartung_faellig_in': 0.0,
                'ist_faellig': True,
                'message': 'Kein Wartungsintervall definiert'
            }
        
        return {
            'hat_intervall': True,
            'intervall_name': aktuelles.name,
            'start_datum': aktuelles.start_datum.isoformat(),
            'intervall_stunden': aktuelles.intervall_betriebsstunden,
            'wartungsintervall': aktuelles.wartungsintervall_stunden,
            'wartung_faellig_in': aktuelles.wartung_faellig_in,
            'ist_faellig': aktuelles.ist_wartung_faellig,
            'naechste_wartung_bei': aktuelles.naechste_wartung_bei
        }
    
    def to_dict(self):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        return {
            'id': self.id,
            'name': self.name,
            'start_datum': self.start_datum.isoformat(),
            'reset_grund': self.reset_grund,
            'startstand_stunden': self.startstand_stunden,
            'wartungsintervall_stunden': self.wartungsintervall_stunden,
            'intervall_betriebsstunden': self.intervall_betriebsstunden,
            'wartung_faellig_in': self.wartung_faellig_in,
            'ist_wartung_faellig': self.ist_wartung_faellig,
            'ist_aktiv': self.ist_aktiv,
            'durchgefuehrt_von': self.durchgefuehrt_von,
            'notizen': self.notizen
        }
