# SQLAlchemy Model für Handbefüllung-Protokolle
from datetime import datetime
from app import db

class Handbefuellung(db.Model):
    """
    Model für Handbefüllung-Protokolle
    
    Erfasst:
    - Molekular- und Kohlefilter-Befüllung
    - Mengen und Materialien
    - Etiketten-Druckdaten
    - Operator-Information
    """
    
    __tablename__ = 'handbefuellungen'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Material-Details
    material_typ = db.Column(db.String(50), nullable=False)  # Molekular, Kohle
    material_bezeichnung = db.Column(db.String(100), nullable=False)
    charge_nummer = db.Column(db.String(50), nullable=True)
    
    # Mengen
    menge_kg = db.Column(db.Float, nullable=False)
    einheit = db.Column(db.String(10), default='kg')
    
    # Befüllung Details
    behaelter_id = db.Column(db.String(50), nullable=True)
    befuellt_am = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    befuellt_von = db.Column(db.String(100), nullable=False)
    
    # Etikett Information
    etikett_gedruckt = db.Column(db.Boolean, default=False)
    etikett_nummer = db.Column(db.String(50), nullable=True)
    
    # Qualitätsdaten
    temperatur = db.Column(db.Float, nullable=True)
    luftfeuchtigkeit = db.Column(db.Float, nullable=True)
    
    # Zusätzliche Informationen
    notizen = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='aktiv')  # aktiv, verbraucht, entsorgt
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Handbefuellung {self.material_typ}: {self.menge_kg}{self.einheit}>'
    
    @property
    def alter_tage(self):
        """Berechnet Alter der Befüllung in Tagen"""
        delta = datetime.utcnow() - self.befuellt_am
        return delta.days
    
    @property
    def etikett_daten(self):
        """Gibt Etikett-Druckdaten zurück"""
        return {
            'material': self.material_bezeichnung,
            'menge': f"{self.menge_kg} {self.einheit}",
            'datum': self.befuellt_am.strftime('%d.%m.%Y'),
            'operator': self.befuellt_von,
            'charge': self.charge_nummer or 'N/A',
            'behaelter': self.behaelter_id or 'N/A'
        }
    
    def etikett_drucken(self):
        """Markiert Etikett als gedruckt"""
        self.etikett_gedruckt = True
        self.etikett_nummer = f"ETI-{self.id:06d}-{datetime.now().strftime('%Y%m%d')}"
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_statistiken():
        """Gibt Befüllungs-Statistiken zurück"""
        total_befuellungen = Handbefuellung.query.count()
        
        # Summe nach Material-Typ
        molekular_gesamt = db.session.query(
            db.func.sum(Handbefuellung.menge_kg)
        ).filter(
            Handbefuellung.material_typ == 'Molekular'
        ).scalar() or 0
        
        kohle_gesamt = db.session.query(
            db.func.sum(Handbefuellung.menge_kg)
        ).filter(
            Handbefuellung.material_typ == 'Kohle'
        ).scalar() or 0
        
        return {
            'total_befuellungen': total_befuellungen,
            'molekular_kg': round(molekular_gesamt, 2),
            'kohle_kg': round(kohle_gesamt, 2),
            'gesamt_kg': round(molekular_gesamt + kohle_gesamt, 2)
        }
    
    @staticmethod
    def get_aktuelle_befuellungen():
        """Gibt aktuelle (nicht verbrauchte) Befüllungen zurück"""
        return Handbefuellung.query.filter_by(status='aktiv').all()
    
    def to_dict(self):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        return {
            'id': self.id,
            'material_typ': self.material_typ,
            'material_bezeichnung': self.material_bezeichnung,
            'charge_nummer': self.charge_nummer,
            'menge_kg': self.menge_kg,
            'einheit': self.einheit,
            'behaelter_id': self.behaelter_id,
            'befuellt_am': self.befuellt_am.isoformat() if self.befuellt_am else None,
            'befuellt_von': self.befuellt_von,
            'etikett_gedruckt': self.etikett_gedruckt,
            'etikett_nummer': self.etikett_nummer,
            'alter_tage': self.alter_tage,
            'status': self.status,
            'notizen': self.notizen
        }
