"""
Preiskonfiguration für Gase
"""

from datetime import datetime
from app import db


class GasPreisKonfiguration(db.Model):
    """
    Konfigurierbare Preise für verschiedene Gase
    """
    __tablename__ = 'gas_preis_konfiguration'
    
    id = db.Column(db.Integer, primary_key=True)
    gas_typ = db.Column(db.String(50), unique=True, nullable=False)  # helium, sauerstoff, luft
    preis_pro_bar_liter = db.Column(db.Float, nullable=False)
    gueltig_ab = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    gueltig_bis = db.Column(db.DateTime, nullable=True)
    ist_aktiv = db.Column(db.Boolean, default=True)
    
    # Metadaten
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    erstellt_von = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<GasPreis {self.gas_typ}: {self.preis_pro_bar_liter} €/Bar·L>'
    
    @staticmethod
    def get_aktuelle_preise():
        """Gibt die aktuell gültigen Preise zurück"""
        preise = {}
        for gas_typ in ['helium', 'sauerstoff', 'luft']:
            preis_config = GasPreisKonfiguration.query.filter_by(
                gas_typ=gas_typ,
                ist_aktiv=True
            ).order_by(GasPreisKonfiguration.gueltig_ab.desc()).first()
            
            if preis_config:
                preise[gas_typ] = preis_config.preis_pro_bar_liter
            else:
                # Fallback auf Standard-Preise
                default_preise = {
                    'helium': 0.095,
                    'sauerstoff': 0.01,
                    'luft': 0.002
                }
                preise[gas_typ] = default_preise.get(gas_typ, 0.0)
        
        return preise
    
    @staticmethod
    def setze_preis(gas_typ, neuer_preis, erstellt_von=None):
        """Setzt einen neuen Preis für ein Gas"""
        # Deaktiviere alte Preise
        alte_preise = GasPreisKonfiguration.query.filter_by(
            gas_typ=gas_typ,
            ist_aktiv=True
        ).all()
        
        for alter_preis in alte_preise:
            alter_preis.ist_aktiv = False
            alter_preis.gueltig_bis = datetime.utcnow()
        
        # Erstelle neuen Preis
        neuer_preis_config = GasPreisKonfiguration(
            gas_typ=gas_typ,
            preis_pro_bar_liter=neuer_preis,
            erstellt_von=erstellt_von
        )
        
        db.session.add(neuer_preis_config)
        db.session.commit()
        
        return neuer_preis_config
    
    @staticmethod
    def initialisiere_standard_preise():
        """Initialisiert die Standard-Preise beim ersten Start"""
        standard_preise = [
            ('helium', 0.095, 'Helium'),
            ('sauerstoff', 0.01, 'Sauerstoff'),
            ('luft', 0.002, 'Luft/Stickstoff')
        ]
        
        for gas_typ, preis, _ in standard_preise:
            # Prüfe ob bereits Preise existieren
            existiert = GasPreisKonfiguration.query.filter_by(gas_typ=gas_typ).first()
            if not existiert:
                GasPreisKonfiguration.setze_preis(gas_typ, preis, 'System')
        
        return True
