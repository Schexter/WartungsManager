# Patronenwechsel Model für WartungsManager
from datetime import datetime, timedelta
from app import db

class PatronenwechselKonfiguration(db.Model):
    """
    Model für Patronenwechsel-Konfiguration
    
    Bestimmt wann Patronen gewechselt werden müssen
    """
    
    __tablename__ = 'patronenwechsel_konfiguration'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Konfiguration
    patronenwechsel_intervall_stunden = db.Column(db.Float, nullable=False, default=12.0)  # Standard: 12h
    warnung_vor_stunden = db.Column(db.Float, nullable=False, default=2.0)  # Warnung 2h vorher
    
    # System-Info
    ist_aktiv = db.Column(db.Boolean, nullable=False, default=True)
    erstellt_von = db.Column(db.String(100), nullable=True)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_aktuelle_konfiguration():
        """Gibt die aktuelle Patronenwechsel-Konfiguration zurück"""
        config = PatronenwechselKonfiguration.query.filter_by(ist_aktiv=True).first()
        if not config:
            # Standard-Konfiguration erstellen
            config = PatronenwechselKonfiguration(
                patronenwechsel_intervall_stunden=12.0,
                warnung_vor_stunden=2.0,
                erstellt_von="SYSTEM_DEFAULT",
                ist_aktiv=True
            )
            db.session.add(config)
            db.session.commit()
        return config

class Patronenwechsel(db.Model):
    """
    Model für durchgeführte Patronenwechsel
    
    Dokumentiert jeden Patronenwechsel mit allen Details
    """
    
    __tablename__ = 'patronenwechsel'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Wechsel-Information
    wechsel_datum = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    durchgefuehrt_von = db.Column(db.String(100), nullable=False)
    
    # Betriebsstunden-Information
    betriebsstunden_bei_wechsel = db.Column(db.Float, nullable=False)  # Gesamt-Betriebsstunden beim Wechsel
    betriebsstunden_seit_letztem_wechsel = db.Column(db.Float, nullable=False)  # Stunden seit letztem Wechsel
    
    # Patronen-Details
    molekularsieb_patrone_1_gewechselt = db.Column(db.Boolean, nullable=False, default=True)
    molekularsieb_patrone_2_gewechselt = db.Column(db.Boolean, nullable=False, default=True)
    kohle_filter_gewechselt = db.Column(db.Boolean, nullable=False, default=True)
    
    # Seriennummern/Chargennummern (optional)
    molekularsieb_1_charge = db.Column(db.String(50), nullable=True)
    molekularsieb_2_charge = db.Column(db.String(50), nullable=True)
    kohle_filter_charge = db.Column(db.String(50), nullable=True)
    
    # Alte Patronen (entfernte)
    alte_molekularsieb_1_charge = db.Column(db.String(50), nullable=True)
    alte_molekularsieb_2_charge = db.Column(db.String(50), nullable=True)
    alte_kohle_filter_charge = db.Column(db.String(50), nullable=True)
    
    # Status und Notizen
    notizen = db.Column(db.Text, nullable=True)
    naechster_wechsel_faellig_bei = db.Column(db.Float, nullable=True)  # Berechnet basierend auf Konfiguration
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Patronenwechsel {self.id}: {self.wechsel_datum} - {self.durchgefuehrt_von}>'
    
    @staticmethod
    def get_letzter_patronenwechsel():
        """Gibt den letzten Patronenwechsel zurück"""
        return Patronenwechsel.query.order_by(Patronenwechsel.wechsel_datum.desc()).first()
    
    @staticmethod
    def get_patronenwechsel_status():
        """Gibt aktuellen Patronenwechsel-Status zurück"""
        from app.models.kompressor import KompressorBetrieb
        
        config = PatronenwechselKonfiguration.get_aktuelle_konfiguration()
        letzter_wechsel = Patronenwechsel.get_letzter_patronenwechsel()
        aktuelle_betriebsstunden = KompressorBetrieb.get_gesamt_betriebsstunden()
        
        if not letzter_wechsel:
            # Noch nie Patronen gewechselt
            return {
                'hat_patronenwechsel': False,
                'stunden_seit_letztem_wechsel': aktuelle_betriebsstunden,
                'naechster_wechsel_bei': config.patronenwechsel_intervall_stunden,
                'stunden_bis_wechsel': max(0.0, config.patronenwechsel_intervall_stunden - aktuelle_betriebsstunden),
                'wechsel_faellig': aktuelle_betriebsstunden >= config.patronenwechsel_intervall_stunden,
                'warnung_aktiv': aktuelle_betriebsstunden >= (config.patronenwechsel_intervall_stunden - config.warnung_vor_stunden),
                'konfiguration': {
                    'intervall_stunden': config.patronenwechsel_intervall_stunden,
                    'warnung_vor_stunden': config.warnung_vor_stunden
                }
            }
        else:
            # Patronen wurden schon gewechselt
            stunden_seit_letztem = aktuelle_betriebsstunden - letzter_wechsel.betriebsstunden_bei_wechsel
            naechster_wechsel_bei = letzter_wechsel.betriebsstunden_bei_wechsel + config.patronenwechsel_intervall_stunden
            stunden_bis_wechsel = max(0.0, naechster_wechsel_bei - aktuelle_betriebsstunden)
            
            return {
                'hat_patronenwechsel': True,
                'letzter_wechsel': letzter_wechsel.to_dict(),
                'stunden_seit_letztem_wechsel': stunden_seit_letztem,
                'naechster_wechsel_bei': naechster_wechsel_bei,
                'stunden_bis_wechsel': stunden_bis_wechsel,
                'wechsel_faellig': stunden_bis_wechsel <= 0,
                'warnung_aktiv': stunden_bis_wechsel <= config.warnung_vor_stunden,
                'konfiguration': {
                    'intervall_stunden': config.patronenwechsel_intervall_stunden,
                    'warnung_vor_stunden': config.warnung_vor_stunden
                }
            }
    
    @staticmethod
    def neuer_patronenwechsel(durchgefuehrt_von, wechsel_datum=None, 
                             molekularsieb_1=True, molekularsieb_2=True, kohle_filter=True,
                             mol_1_charge=None, mol_2_charge=None, kohle_charge=None,
                             alte_mol_1=None, alte_mol_2=None, alte_kohle=None, notizen=None):
        """Erstellt einen neuen Patronenwechsel-Eintrag"""
        from app.models.kompressor import KompressorBetrieb
        
        if wechsel_datum is None:
            wechsel_datum = datetime.utcnow()
        
        config = PatronenwechselKonfiguration.get_aktuelle_konfiguration()
        letzter_wechsel = Patronenwechsel.get_letzter_patronenwechsel()
        aktuelle_betriebsstunden = KompressorBetrieb.get_gesamt_betriebsstunden()
        
        # Stunden seit letztem Wechsel berechnen
        if letzter_wechsel:
            stunden_seit_letztem = aktuelle_betriebsstunden - letzter_wechsel.betriebsstunden_bei_wechsel
        else:
            stunden_seit_letztem = aktuelle_betriebsstunden
        
        # Neuen Wechsel erstellen
        neuer_wechsel = Patronenwechsel(
            wechsel_datum=wechsel_datum,
            durchgefuehrt_von=durchgefuehrt_von,
            betriebsstunden_bei_wechsel=aktuelle_betriebsstunden,
            betriebsstunden_seit_letztem_wechsel=stunden_seit_letztem,
            molekularsieb_patrone_1_gewechselt=molekularsieb_1,
            molekularsieb_patrone_2_gewechselt=molekularsieb_2,
            kohle_filter_gewechselt=kohle_filter,
            molekularsieb_1_charge=mol_1_charge,
            molekularsieb_2_charge=mol_2_charge,
            kohle_filter_charge=kohle_charge,
            alte_molekularsieb_1_charge=alte_mol_1,
            alte_molekularsieb_2_charge=alte_mol_2,
            alte_kohle_filter_charge=alte_kohle,
            notizen=notizen,
            naechster_wechsel_faellig_bei=aktuelle_betriebsstunden + config.patronenwechsel_intervall_stunden
        )
        
        db.session.add(neuer_wechsel)
        db.session.commit()
        
        return neuer_wechsel
    
    def to_dict(self):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        return {
            'id': self.id,
            'wechsel_datum': self.wechsel_datum.isoformat(),
            'durchgefuehrt_von': self.durchgefuehrt_von,
            'betriebsstunden_bei_wechsel': self.betriebsstunden_bei_wechsel,
            'betriebsstunden_seit_letztem_wechsel': self.betriebsstunden_seit_letztem_wechsel,
            'molekularsieb_patrone_1_gewechselt': self.molekularsieb_patrone_1_gewechselt,
            'molekularsieb_patrone_2_gewechselt': self.molekularsieb_patrone_2_gewechselt,
            'kohle_filter_gewechselt': self.kohle_filter_gewechselt,
            'molekularsieb_1_charge': self.molekularsieb_1_charge,
            'molekularsieb_2_charge': self.molekularsieb_2_charge,
            'kohle_filter_charge': self.kohle_filter_charge,
            'alte_molekularsieb_1_charge': self.alte_molekularsieb_1_charge,
            'alte_molekularsieb_2_charge': self.alte_molekularsieb_2_charge,
            'alte_kohle_filter_charge': self.alte_kohle_filter_charge,
            'notizen': self.notizen,
            'naechster_wechsel_faellig_bei': self.naechster_wechsel_faellig_bei
        }
