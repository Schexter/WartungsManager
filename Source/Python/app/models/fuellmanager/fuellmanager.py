"""
Füllmanager Model - Verwaltung und Dokumentation von Füllvorgängen
Erweitert die Flaschen-Füllvorgänge um vollständige Dokumentation und Unterschriften
"""

from datetime import datetime
from app import db
import json
from .preiskonfiguration import GasPreisKonfiguration


class FuellManager(db.Model):
    """
    Hauptmodell für die Füllmanager-Verwaltung
    Verwaltet den gesamten Füllprozess von Annahme bis Unterschrift
    """
    __tablename__ = 'fuellmanager'
    
    # Primärschlüssel
    id = db.Column(db.Integer, primary_key=True)
    
    # Referenzen
    kunde_id = db.Column(db.Integer, db.ForeignKey('kunden.id'), nullable=False)
    flasche_id = db.Column(db.Integer, db.ForeignKey('flaschen.id'), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Auftragsdaten
    auftragsnummer = db.Column(db.String(50), unique=True, nullable=False)  # FM-2025-001
    status = db.Column(db.String(30), nullable=False, default='angenommen')  # angenommen, in_fuellung, abgeschlossen, storniert
    
    # Zeitstempel
    annahme_zeit = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fuellstart_zeit = db.Column(db.DateTime, nullable=True)
    fuellende_zeit = db.Column(db.DateTime, nullable=True)
    uebergabe_zeit = db.Column(db.DateTime, nullable=True)
    
    # Flaschenprüfung bei Annahme
    visuelle_pruefung = db.Column(db.Boolean, default=False)
    tuev_geprueft = db.Column(db.Boolean, default=False)
    ventil_zustand = db.Column(db.String(20), default='OK')  # OK, Defekt, Wartung
    annahme_notizen = db.Column(db.Text, nullable=True)
    
    # Füllungsdaten
    restdruck_bar = db.Column(db.Float, nullable=False, default=0.0)
    zieldruck_bar = db.Column(db.Float, nullable=False, default=220.0)
    tatsaechlicher_enddruck = db.Column(db.Float, nullable=True)
    
    # Gasgemisch (%)
    sauerstoff_prozent = db.Column(db.Float, nullable=False, default=21.0)
    helium_prozent = db.Column(db.Float, nullable=False, default=0.0)
    stickstoff_prozent = db.Column(db.Float, nullable=False, default=79.0)
    
    # Berechnete Werte (JSON für flexible Speicherung)
    berechnungen = db.Column(db.Text, nullable=True)  # MOD, END, Partialdrücke etc.
    
    # Preisberechnung
    preis_helium = db.Column(db.Float, nullable=False, default=0.0)
    preis_sauerstoff = db.Column(db.Float, nullable=False, default=0.0)
    preis_luft = db.Column(db.Float, nullable=False, default=0.0)
    gesamtpreis = db.Column(db.Float, nullable=False, default=0.0)
    bezahlt = db.Column(db.Boolean, default=False)
    
    # Dokumentation
    fuell_notizen = db.Column(db.Text, nullable=True)
    
    # Zeitstempel
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    aktualisiert_am = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    kunde = db.relationship('Kunde', backref='fuellmanager_auftraege')
    flasche = db.relationship('Flasche', backref='fuellmanager_auftraege')
    operator = db.relationship('User', backref='fuellmanager_auftraege')
    
    def __repr__(self):
        return f'<FuellManager {self.auftragsnummer}: {self.status}>'
    
    def generiere_auftragsnummer(self):
        """Generiert eine eindeutige Auftragsnummer"""
        jahr = datetime.now().year
        # Finde die höchste Nummer für dieses Jahr
        letzte_nummer = db.session.query(db.func.max(
            db.func.cast(db.func.substr(FuellManager.auftragsnummer, -3), db.Integer)
        )).filter(
            FuellManager.auftragsnummer.like(f'FM-{jahr}-%')
        ).scalar() or 0
        
        self.auftragsnummer = f'FM-{jahr}-{letzte_nummer + 1:03d}'
        return self.auftragsnummer
    
    def berechne_preise(self):
        """Berechnet die Preise basierend auf dem Gasgemisch"""
        # Hole aktuelle Preise aus der Konfiguration
        preise = GasPreisKonfiguration.get_aktuelle_preise()
        PREIS_HELIUM = preise['helium']
        PREIS_SAUERSTOFF = preise['sauerstoff']
        PREIS_LUFT = preise['luft']
        
        # Flaschenvolumen
        volumen = self.flasche.groesse_liter if self.flasche else 11.0
        
        # Berechnung der Füllmenge
        fuellmenge_bar = self.zieldruck_bar - self.restdruck_bar
        
        # Gasvolumen in Bar·Liter
        helium_bar_liter = (self.helium_prozent / 100) * fuellmenge_bar * volumen
        sauerstoff_bar_liter = (self.sauerstoff_prozent / 100) * fuellmenge_bar * volumen
        luft_bar_liter = (self.stickstoff_prozent / 100) * fuellmenge_bar * volumen
        
        # Preisberechnung
        self.preis_helium = round(helium_bar_liter * PREIS_HELIUM, 2)
        self.preis_sauerstoff = round(sauerstoff_bar_liter * PREIS_SAUERSTOFF, 2)
        self.preis_luft = round(luft_bar_liter * PREIS_LUFT, 2)
        self.gesamtpreis = round(self.preis_helium + self.preis_sauerstoff + self.preis_luft, 2)
        
        return {
            'helium_bar_liter': round(helium_bar_liter, 1),
            'sauerstoff_bar_liter': round(sauerstoff_bar_liter, 1),
            'luft_bar_liter': round(luft_bar_liter, 1),
            'preis_helium': self.preis_helium,
            'preis_sauerstoff': self.preis_sauerstoff,
            'preis_luft': self.preis_luft,
            'gesamtpreis': self.gesamtpreis
        }
    
    def berechne_tauchparameter(self):
        """Berechnet MOD, END und andere Tauchparameter"""
        berechnungen = {}
        
        # MOD Berechnungen für verschiedene ppO2-Werte
        if self.sauerstoff_prozent > 0:
            # MOD bei 1.2 bar ppO2
            mod_1_2 = (1.2 / (self.sauerstoff_prozent / 100)) - 1
            berechnungen['mod_1_2'] = round(max(0, mod_1_2 * 10), 1)  # Meter
            
            # MOD bei 1.4 bar ppO2
            mod_1_4 = (1.4 / (self.sauerstoff_prozent / 100)) - 1
            berechnungen['mod_1_4'] = round(max(0, mod_1_4 * 10), 1)  # Meter
            
            # MOD bei 1.6 bar ppO2
            mod_1_6 = (1.6 / (self.sauerstoff_prozent / 100)) - 1
            berechnungen['mod_1_6'] = round(max(0, mod_1_6 * 10), 1)  # Meter
        
        # END Berechnung bei 30m (4 bar absolut)
        if self.stickstoff_prozent > 0:
            end_30m = (4 * (self.stickstoff_prozent / 100)) / 0.79 - 1
            berechnungen['end_30m'] = round(max(0, end_30m * 10), 1)  # Meter
        
        # Speichere als JSON
        self.berechnungen = json.dumps(berechnungen)
        
        return berechnungen
    
    def start_fuellung(self):
        """Startet den Füllvorgang"""
        self.status = 'in_fuellung'
        self.fuellstart_zeit = datetime.utcnow()
        db.session.commit()
    
    def beende_fuellung(self, enddruck=None):
        """Beendet den Füllvorgang"""
        self.fuellende_zeit = datetime.utcnow()
        if enddruck:
            self.tatsaechlicher_enddruck = enddruck
        else:
            self.tatsaechlicher_enddruck = self.zieldruck_bar
        db.session.commit()
    
    def abschliessen(self):
        """Schließt den gesamten Vorgang ab"""
        self.status = 'abgeschlossen'
        self.uebergabe_zeit = datetime.utcnow()
        db.session.commit()
    
    def get_berechnungen(self):
        """Gibt die gespeicherten Berechnungen als Dictionary zurück"""
        if self.berechnungen:
            return json.loads(self.berechnungen)
        return {}
    
    def to_dict(self):
        """Konvertiert das Model zu einem Dictionary"""
        berechnungen = self.get_berechnungen()
        
        return {
            'id': self.id,
            'auftragsnummer': self.auftragsnummer,
            'status': self.status,
            'kunde': {
                'id': self.kunde.id,
                'vollname': self.kunde.vollname,
                'mitgliedsnummer': self.kunde.mitgliedsnummer
            } if self.kunde else None,
            'flasche': {
                'id': self.flasche.id,
                'flasche_nummer': self.flasche.flasche_nummer,
                'groesse_liter': self.flasche.groesse_liter,
                'externe_flasche_nummer': self.flasche.externe_flasche_nummer
            } if self.flasche else None,
            'operator': self.operator.username if self.operator else None,
            'zeiten': {
                'annahme': self.annahme_zeit.isoformat() if self.annahme_zeit else None,
                'fuellstart': self.fuellstart_zeit.isoformat() if self.fuellstart_zeit else None,
                'fuellende': self.fuellende_zeit.isoformat() if self.fuellende_zeit else None,
                'uebergabe': self.uebergabe_zeit.isoformat() if self.uebergabe_zeit else None
            },
            'pruefung': {
                'visuelle_pruefung': self.visuelle_pruefung,
                'tuev_geprueft': self.tuev_geprueft,
                'ventil_zustand': self.ventil_zustand,
                'annahme_notizen': self.annahme_notizen
            },
            'fuellung': {
                'restdruck_bar': self.restdruck_bar,
                'zieldruck_bar': self.zieldruck_bar,
                'tatsaechlicher_enddruck': self.tatsaechlicher_enddruck,
                'gasgemisch': {
                    'sauerstoff': self.sauerstoff_prozent,
                    'helium': self.helium_prozent,
                    'stickstoff': self.stickstoff_prozent
                },
                'notizen': self.fuell_notizen
            },
            'berechnungen': berechnungen,
            'preise': {
                'helium': self.preis_helium,
                'sauerstoff': self.preis_sauerstoff,
                'luft': self.preis_luft,
                'gesamt': self.gesamtpreis,
                'bezahlt': self.bezahlt
            }
        }


class FuellVorgangErweitert(db.Model):
    """
    Erweiterte Füllvorgänge mit detaillierter Protokollierung
    """
    __tablename__ = 'fuellvorgang_erweitert'
    
    id = db.Column(db.Integer, primary_key=True)
    fuellmanager_id = db.Column(db.Integer, db.ForeignKey('fuellmanager.id'), nullable=False)
    
    # Ereignistyp
    ereignis_typ = db.Column(db.String(50), nullable=False)  # annahme, pruefung, fuellstart, fuellende, uebergabe
    ereignis_zeit = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Details als JSON
    details = db.Column(db.Text, nullable=True)
    
    # Operator
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    fuellmanager = db.relationship('FuellManager', backref='ereignisse')
    operator = db.relationship('User')
    
    def __repr__(self):
        return f'<FuellVorgangErweitert {self.ereignis_typ} @ {self.ereignis_zeit}>'


class FuellManagerSignatur(db.Model):
    """
    Digitale Unterschriften für Füllvorgänge
    """
    __tablename__ = 'fuellmanager_signaturen'
    
    id = db.Column(db.Integer, primary_key=True)
    fuellmanager_id = db.Column(db.Integer, db.ForeignKey('fuellmanager.id'), nullable=False)
    
    # Unterschriftstyp
    signatur_typ = db.Column(db.String(20), nullable=False)  # kunde, mitarbeiter
    
    # Signatur-Daten (Base64)
    signatur_daten = db.Column(db.Text, nullable=False)
    
    # Metadaten
    unterschrieben_am = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    unterschrieben_von = db.Column(db.String(100), nullable=False)
    
    # Device-Info
    device_info = db.Column(db.String(500), nullable=True)
    ip_adresse = db.Column(db.String(50), nullable=True)
    
    # Relationships
    fuellmanager = db.relationship('FuellManager', backref='signaturen')
    
    def __repr__(self):
        return f'<FuellManagerSignatur {self.signatur_typ} für {self.fuellmanager_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fuellmanager_id': self.fuellmanager_id,
            'signatur_typ': self.signatur_typ,
            'unterschrieben_am': self.unterschrieben_am.isoformat() if self.unterschrieben_am else None,
            'unterschrieben_von': self.unterschrieben_von,
            'device_info': self.device_info,
            'ip_adresse': self.ip_adresse
        }
