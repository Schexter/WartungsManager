# SQLAlchemy Model für Bulk-Füllvorgänge
from datetime import datetime
from app import db

class BulkFuellvorgang(db.Model):
    """
    Model für Bulk-Füllvorgänge (mehrere Flaschen gleichzeitig)
    
    Erfasst:
    - Bulk-Füllungen mit mehreren Flaschen
    - Gesamt-Zeiterfassung
    - Operator-Information
    - Verknüpfung mit einzelnen Flaschen
    """
    
    __tablename__ = 'bulk_fuellvorgaenge'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Zeiterfassung
    start_zeit = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_zeit = db.Column(db.DateTime, nullable=True)
    gesamtdauer_minuten = db.Column(db.Integer, nullable=True)  # Automatisch berechnet
    
    # Operator Information
    operator = db.Column(db.String(100), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Füllvorgang-Details
    anzahl_flaschen = db.Column(db.Integer, nullable=False, default=0)
    erfolgreich_gefuellt = db.Column(db.Integer, default=0)
    fehlgeschlagen = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='vorbereitung')  
    # Status: vorbereitung, laufend, beendet, abgebrochen
    
    # Kompressor-Verknüpfung
    kompressor_betrieb_id = db.Column(db.Integer, db.ForeignKey('kompressor_betrieb.id'), nullable=True)
    
    # Zusätzliche Informationen
    notizen = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    operator_user = db.relationship('User', foreign_keys=[operator_id], backref='bulk_fuellvorgaenge')
    kompressor_betrieb = db.relationship('KompressorBetrieb', backref='bulk_fuellvorgaenge')
    flasche_fuellungen = db.relationship('FlascheFuellvorgang', backref='bulk_vorgang', lazy='dynamic')
    
    def __repr__(self):
        return f'<BulkFuellvorgang {self.id}: {self.anzahl_flaschen} Flaschen - {self.status}>'
    
    @property
    def ist_aktiv(self):
        """Prüft ob Bulk-Füllvorgang noch läuft"""
        return self.status in ['vorbereitung', 'laufend']
    
    @property
    def gesamtdauer_stunden(self):
        """Berechnet Gesamtdauer in Stunden (float)"""
        if self.gesamtdauer_minuten:
            return round(self.gesamtdauer_minuten / 60.0, 2)
        return 0.0
    
    @property
    def aktuelle_dauer(self):
        """Berechnet aktuelle Dauer für laufende Füllungen"""
        if self.ist_aktiv and self.start_zeit:
            delta = datetime.utcnow() - self.start_zeit
            return delta.total_seconds() / 60  # Minuten
        return self.gesamtdauer_minuten or 0
    
    @property
    def erfolgsquote_prozent(self):
        """Berechnet Erfolgsquote in Prozent"""
        if self.anzahl_flaschen == 0:
            return 0
        return round((self.erfolgreich_gefuellt / self.anzahl_flaschen) * 100, 1)
    
    @property
    def bearbeitete_flaschen(self):
        """Anzahl bereits bearbeiteter Flaschen"""
        return self.erfolgreich_gefuellt + self.fehlgeschlagen
    
    @property
    def offene_flaschen(self):
        """Anzahl noch nicht bearbeiteter Flaschen"""
        return self.anzahl_flaschen - self.bearbeitete_flaschen
    
    def starten(self):
        """Startet den Bulk-Füllvorgang"""
        if self.status != 'vorbereitung':
            raise ValueError("Bulk-Füllvorgang kann nur aus Status 'vorbereitung' gestartet werden")
        
        self.status = 'laufend'
        self.start_zeit = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def beenden(self, end_zeit=None):
        """Beendet den Bulk-Füllvorgang"""
        if end_zeit is None:
            end_zeit = datetime.utcnow()
        
        self.end_zeit = end_zeit
        self.status = 'beendet'
        
        # Gesamtdauer berechnen
        if self.start_zeit:
            delta = self.end_zeit - self.start_zeit
            self.gesamtdauer_minuten = int(delta.total_seconds() / 60)
        
        self.updated_at = datetime.utcnow()
    
    def abbrechen(self, grund="Manuell abgebrochen"):
        """Bricht den Bulk-Füllvorgang ab"""
        self.end_zeit = datetime.utcnow()
        self.status = 'abgebrochen'
        self.notizen = self.notizen or ""
        self.notizen += f"\nAbbruch: {grund}"
        self.updated_at = datetime.utcnow()
    
    def flasche_hinzufuegen(self, flasche, ziel_druck=300):
        """Fügt eine Flasche zum Bulk-Füllvorgang hinzu"""
        # Prüfe ob Flasche bereits hinzugefügt
        existing = self.flasche_fuellungen.filter_by(flasche_id=flasche.id).first()
        if existing:
            return existing
        
        flasche_fuellung = FlascheFuellvorgang(
            bulk_fuellvorgang_id=self.id,
            flasche_id=flasche.id,
            ziel_druck=ziel_druck
        )
        
        db.session.add(flasche_fuellung)
        self.anzahl_flaschen += 1
        self.updated_at = datetime.utcnow()
        
        return flasche_fuellung
    
    def flasche_entfernen(self, flasche):
        """Entfernt eine Flasche aus dem Bulk-Füllvorgang"""
        flasche_fuellung = self.flasche_fuellungen.filter_by(flasche_id=flasche.id).first()
        if not flasche_fuellung:
            return False
        
        # Nur entfernen wenn noch nicht gefüllt
        if flasche_fuellung.status == 'wartend':
            db.session.delete(flasche_fuellung)
            self.anzahl_flaschen -= 1
            self.updated_at = datetime.utcnow()
            return True
        
        return False
    
    def flasche_als_erfolgreich_markieren(self, flasche, erreicher_druck=None):
        """Markiert eine Flasche als erfolgreich gefüllt"""
        flasche_fuellung = self.flasche_fuellungen.filter_by(flasche_id=flasche.id).first()
        if not flasche_fuellung:
            return False
        
        flasche_fuellung.als_erfolgreich_markieren(erreicher_druck)
        self.erfolgreich_gefuellt += 1
        self.updated_at = datetime.utcnow()
        
        return True
    
    def flasche_als_fehlgeschlagen_markieren(self, flasche, grund=None):
        """Markiert eine Flasche als fehlgeschlagen"""
        flasche_fuellung = self.flasche_fuellungen.filter_by(flasche_id=flasche.id).first()
        if not flasche_fuellung:
            return False
        
        flasche_fuellung.als_fehlgeschlagen_markieren(grund)
        self.fehlgeschlagen += 1
        self.updated_at = datetime.utcnow()
        
        return True
    
    @staticmethod
    def get_aktiver_bulk_vorgang():
        """Gibt den aktuell laufenden Bulk-Füllvorgang zurück"""
        return BulkFuellvorgang.query.filter(
            BulkFuellvorgang.status.in_(['vorbereitung', 'laufend'])
        ).first()
    
    @staticmethod
    def erstelle_bulk_vorgang(operator, flaschen_ids=None):
        """Erstellt einen neuen Bulk-Füllvorgang"""
        # Prüfe ob bereits ein aktiver Vorgang läuft
        aktiver_vorgang = BulkFuellvorgang.get_aktiver_bulk_vorgang()
        if aktiver_vorgang:
            raise ValueError("Es läuft bereits ein Bulk-Füllvorgang")
        
        bulk_vorgang = BulkFuellvorgang(operator=operator)
        db.session.add(bulk_vorgang)
        db.session.flush()  # Damit wir die ID bekommen
        
        # Flaschen hinzufügen falls angegeben
        if flaschen_ids:
            from app.models.flaschen import Flasche
            flaschen = Flasche.query.filter(Flasche.id.in_(flaschen_ids)).all()
            
            for flasche in flaschen:
                bulk_vorgang.flasche_hinzufuegen(flasche)
        
        db.session.commit()
        return bulk_vorgang
    
    @staticmethod
    def get_statistiken():
        """Gibt Bulk-Füllvorgang Statistiken zurück"""
        total_vorgaenge = BulkFuellvorgang.query.filter_by(status='beendet').count()
        
        if total_vorgaenge == 0:
            return {
                'total_vorgaenge': 0,
                'total_flaschen': 0,
                'durchschnitt_flaschen': 0,
                'durchschnitt_erfolgsquote': 0,
                'gesamtzeit_stunden': 0
            }
        
        # Aggregierte Daten
        result = db.session.query(
            db.func.sum(BulkFuellvorgang.anzahl_flaschen),
            db.func.sum(BulkFuellvorgang.erfolgreich_gefuellt),
            db.func.sum(BulkFuellvorgang.gesamtdauer_minuten),
            db.func.avg(BulkFuellvorgang.anzahl_flaschen)
        ).filter_by(status='beendet').first()
        
        total_flaschen, total_erfolgreich, total_minuten, avg_flaschen = result
        
        return {
            'total_vorgaenge': total_vorgaenge,
            'total_flaschen': total_flaschen or 0,
            'total_erfolgreich': total_erfolgreich or 0,
            'durchschnitt_flaschen': round(avg_flaschen or 0, 1),
            'durchschnitt_erfolgsquote': round(((total_erfolgreich or 0) / (total_flaschen or 1)) * 100, 1),
            'gesamtzeit_stunden': round((total_minuten or 0) / 60.0, 1)
        }

    def to_dict(self, include_flaschen=False):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        data = {
            'id': self.id,
            'start_zeit': self.start_zeit.isoformat() if self.start_zeit else None,
            'end_zeit': self.end_zeit.isoformat() if self.end_zeit else None,
            'gesamtdauer_minuten': self.gesamtdauer_minuten,
            'gesamtdauer_stunden': self.gesamtdauer_stunden,
            'operator': self.operator,
            'anzahl_flaschen': self.anzahl_flaschen,
            'erfolgreich_gefuellt': self.erfolgreich_gefuellt,
            'fehlgeschlagen': self.fehlgeschlagen,
            'bearbeitete_flaschen': self.bearbeitete_flaschen,
            'offene_flaschen': self.offene_flaschen,
            'erfolgsquote_prozent': self.erfolgsquote_prozent,
            'status': self.status,
            'ist_aktiv': self.ist_aktiv,
            'notizen': self.notizen
        }
        
        if include_flaschen:
            data['flaschen'] = [ff.to_dict() for ff in self.flasche_fuellungen]
        
        return data


class FlascheFuellvorgang(db.Model):
    """
    Junction Table für Flaschen in Bulk-Füllvorgängen
    
    Erfasst:
    - Individual-Status jeder Flasche im Bulk-Vorgang
    - Ziel- und Erreichtdruck
    - Einzelne Füllergebnisse
    """
    
    __tablename__ = 'flasche_fuellvorgang'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    bulk_fuellvorgang_id = db.Column(db.Integer, db.ForeignKey('bulk_fuellvorgaenge.id'), nullable=False)
    flasche_id = db.Column(db.Integer, db.ForeignKey('flaschen.id'), nullable=False)
    
    # Füll-Details
    ziel_druck = db.Column(db.Integer, default=300)  # Bar
    erreicher_druck = db.Column(db.Integer, nullable=True)  # Bar
    
    # Status dieser Flasche
    status = db.Column(db.String(20), default='wartend')  # wartend, gefuellt, fehlgeschlagen
    
    # Zeitstempel
    gefuellt_um = db.Column(db.DateTime, nullable=True)
    
    # Füller-Information (NEU)
    fueller_name = db.Column(db.String(100), nullable=True)  # Name des Füllers
    kompressor_id = db.Column(db.String(50), nullable=True)  # Kompressor-Bezeichnung
    
    # Fehler-Information
    fehler_grund = db.Column(db.String(200), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flasche = db.relationship('Flasche', backref='flasche_fuellvorgaenge')
    
    def __repr__(self):
        return f'<FlascheFuellvorgang Flasche:{self.flasche_id} - {self.status}>'
    
    @property
    def ist_erfolgreich(self):
        """Prüft ob Füllung erfolgreich war"""
        return self.status == 'gefuellt'
    
    @property
    def ist_fehlgeschlagen(self):
        """Prüft ob Füllung fehlgeschlagen ist"""
        return self.status == 'fehlgeschlagen'
    
    @property
    def druckdifferenz(self):
        """Berechnet Druckdifferenz (erreicht - Ziel)"""
        if self.erreicher_druck and self.ziel_druck:
            return self.erreicher_druck - self.ziel_druck
        return 0
    
    def als_erfolgreich_markieren(self, erreicher_druck=None, fueller_name=None, kompressor_id=None):
        """Markiert Flasche als erfolgreich gefüllt"""
        self.status = 'gefuellt'
        self.gefuellt_um = datetime.utcnow()
        if erreicher_druck:
            self.erreicher_druck = erreicher_druck
        if fueller_name:
            self.fueller_name = fueller_name
        if kompressor_id:
            self.kompressor_id = kompressor_id
        self.updated_at = datetime.utcnow()
    
    def als_fehlgeschlagen_markieren(self, grund=None):
        """Markiert Flasche als fehlgeschlagen"""
        self.status = 'fehlgeschlagen'
        self.gefuellt_um = datetime.utcnow()
        if grund:
            self.fehler_grund = grund
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        return {
            'id': self.id,
            'flasche_id': self.flasche_id,
            'flasche_nummer': self.flasche.flaschennummer if self.flasche else None,
            'besitzer_name': self.flasche.besitzer.vollname if self.flasche and self.flasche.besitzer else None,
            'ziel_druck': self.ziel_druck,
            'erreicher_druck': self.erreicher_druck,
            'druckdifferenz': self.druckdifferenz,
            'status': self.status,
            'ist_erfolgreich': self.ist_erfolgreich,
            'ist_fehlgeschlagen': self.ist_fehlgeschlagen,
            'gefuellt_um': self.gefuellt_um.isoformat() if self.gefuellt_um else None,
            'fueller_name': self.fueller_name,
            'kompressor_id': self.kompressor_id,
            'fehler_grund': self.fehler_grund
        }
