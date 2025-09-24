# SQLAlchemy Model für Kunden/Mitglieder-Verwaltung
from datetime import datetime
from app import db

class Kunde(db.Model):
    """
    Model für Kunden/Mitglieder-Verwaltung
    
    Erfasst:
    - Mitgliederdaten
    - Mitgliedsnummern
    - Kontaktinformationen
    - Flaschen-Beziehungen
    """
    
    __tablename__ = 'kunden'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Mitgliedsnummer (eindeutig)
    mitgliedsnummer = db.Column(db.String(20), unique=True, nullable=False)
    
    # Externe Kundennummern (für andere Systeme/Vereine)
    externe_kundennummer = db.Column(db.String(50), nullable=True)  # Verein, andere Systeme
    externe_system = db.Column(db.String(100), nullable=True)  # Woher kommt die externe Nummer
    
    # Persönliche Daten
    vorname = db.Column(db.String(50), nullable=False)
    nachname = db.Column(db.String(100), nullable=False)
    firma = db.Column(db.String(200), nullable=True)
    
    # Kontaktdaten
    email = db.Column(db.String(120), nullable=True)
    telefon = db.Column(db.String(30), nullable=True)
    
    # Adresse
    strasse = db.Column(db.String(200), nullable=True)
    plz = db.Column(db.String(10), nullable=True)
    ort = db.Column(db.String(100), nullable=True)
    adresse = db.Column(db.Text, nullable=True)  # Zusätzliches Adressfeld
    
    # Mitgliedschaft
    mitglied_seit = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    mitgliedschaft_typ = db.Column(db.String(30), default='Standard')  # Standard, Premium, etc.
    ist_aktiv = db.Column(db.Boolean, default=True)
    
    # Zusätzliche Informationen
    notizen = db.Column(db.Text, nullable=True)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flaschen = db.relationship('Flasche', backref='besitzer', lazy='dynamic')
    
    def __repr__(self):
        return f'<Kunde {self.mitgliedsnummer}: {self.vollname}>'
    
    @property
    def vollname(self):
        """Gibt den vollständigen Namen zurück"""
        if self.firma:
            return f"{self.vorname} {self.nachname} ({self.firma})"
        return f"{self.vorname} {self.nachname}"
    
    @property
    def anzahl_flaschen(self):
        """Anzahl der Flaschen des Kunden"""
        return self.flaschen.count()
    
    @property
    def aktive_flaschen(self):
        """Nur aktive Flaschen des Kunden"""
        return self.flaschen.filter_by(ist_aktiv=True)
    
    @property
    def vollstaendige_adresse(self):
        """Formatierte Adresse"""
        if not (self.strasse and self.plz and self.ort):
            return "Adresse unvollständig"
        return f"{self.strasse}, {self.plz} {self.ort}"
    
    @property
    def mitgliedschaft_dauer_jahre(self):
        """Mitgliedschaftsdauer in Jahren"""
        heute = datetime.utcnow().date()
        delta = heute - self.mitglied_seit
        return round(delta.days / 365.25, 1)
    
    def deaktivieren(self, grund=None):
        """Deaktiviert den Kunden"""
        self.ist_aktiv = False
        if grund:
            self.notizen = self.notizen or ""
            self.notizen += f"\nDeaktiviert: {grund} ({datetime.utcnow().strftime('%d.%m.%Y')})"
        self.updated_at = datetime.utcnow()
    
    def reaktivieren(self, grund=None):
        """Reaktiviert den Kunden"""
        self.ist_aktiv = True
        if grund:
            self.notizen = self.notizen or ""
            self.notizen += f"\nReaktiviert: {grund} ({datetime.utcnow().strftime('%d.%m.%Y')})"
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_naechste_mitgliedsnummer():
        """Generiert die nächste verfügbare Mitgliedsnummer"""
        # Findet die höchste numerische Mitgliedsnummer
        letzter_kunde = Kunde.query.order_by(Kunde.id.desc()).first()
        
        if not letzter_kunde:
            return "M-001"
        
        try:
            # Versuche numerischen Teil zu extrahieren
            letzte_nummer = int(letzter_kunde.mitgliedsnummer.split('-')[1])
            neue_nummer = letzte_nummer + 1
            return f"M-{neue_nummer:03d}"
        except (ValueError, IndexError):
            # Fallback: Zähle alle Kunden + 1
            anzahl = Kunde.query.count()
            return f"M-{anzahl + 1:03d}"
    
    @staticmethod
    def suche_kunde(suchbegriff):
        """Sucht Kunden nach verschiedenen Kriterien inklusive externe Nummern"""
        suchbegriff = f"%{suchbegriff}%"
        
        return Kunde.query.filter(
            db.or_(
                Kunde.mitgliedsnummer.like(suchbegriff),
                Kunde.externe_kundennummer.like(suchbegriff),
                Kunde.vorname.like(suchbegriff),
                Kunde.nachname.like(suchbegriff),
                Kunde.firma.like(suchbegriff),
                Kunde.email.like(suchbegriff),
                # Kombinierte Suche für "Vorname Nachname" (SQLite-Syntax)
                (Kunde.vorname + ' ' + Kunde.nachname).like(suchbegriff)
            )
        ).all()
    
    @staticmethod
    def pruefen_kunde_existiert(vorname=None, nachname=None, email=None, mitgliedsnummer=None):
        """Prüft ob Kunde bereits existiert"""
        query = Kunde.query
        
        if mitgliedsnummer:
            return query.filter_by(mitgliedsnummer=mitgliedsnummer).first()
        
        if email:
            kunde = query.filter_by(email=email).first()
            if kunde:
                return kunde
        
        if vorname and nachname:
            return query.filter_by(vorname=vorname, nachname=nachname).first()
        
        return None
    
    @staticmethod
    def get_kunden_statistiken():
        """Gibt Kunden-Statistiken zurück"""
        try:
            from datetime import timedelta
            from sqlalchemy import func
            
            total_kunden = Kunde.query.count()
            aktive_kunden = Kunde.query.filter_by(ist_aktiv=True).count()
            
            # Mitgliedschaftstypen - vereinfacht
            try:
                typen_result = db.session.query(
                    Kunde.mitgliedschaft_typ,
                    func.count(Kunde.id)
                ).group_by(Kunde.mitgliedschaft_typ).all()
                typen = dict(typen_result)
            except Exception as e:
                print(f"Fehler bei Mitgliedschaftstypen: {e}")
                typen = {}
            
            # Neue Mitglieder letzte 30 Tage
            try:
                vor_30_tagen = datetime.utcnow().date() - timedelta(days=30)
                neue_mitglieder = Kunde.query.filter(
                    Kunde.mitglied_seit >= vor_30_tagen
                ).count()
            except Exception as e:
                print(f"Fehler bei neuen Mitgliedern: {e}")
                neue_mitglieder = 0
            
            return {
                'total_kunden': total_kunden,
                'aktive_kunden': aktive_kunden,
                'inaktive_kunden': total_kunden - aktive_kunden,
                'mitgliedschaftstypen': typen,
                'neue_mitglieder_30_tage': neue_mitglieder
            }
            
        except Exception as e:
            print(f"Fehler bei Kunden-Statistiken: {str(e)}")
            return {
                'total_kunden': 0,
                'aktive_kunden': 0,
                'inaktive_kunden': 0,
                'mitgliedschaftstypen': {},
                'neue_mitglieder_30_tage': 0
            }
    
    @staticmethod
    def erstelle_oder_finde_kunde(daten):
        """Erstellt neuen Kunden oder findet existierenden"""
        # Prüfe ob Kunde bereits existiert
        existierender_kunde = Kunde.pruefen_kunde_existiert(
            vorname=daten.get('vorname'),
            nachname=daten.get('nachname'),
            email=daten.get('email'),
            mitgliedsnummer=daten.get('mitgliedsnummer')
        )
        
        if existierender_kunde:
            return {
                'kunde': existierender_kunde,
                'neu_erstellt': False,
                'message': f'Kunde bereits vorhanden: {existierender_kunde.vollname}'
            }
        
        # Erstelle neuen Kunden
        neue_mitgliedsnummer = daten.get('mitgliedsnummer') or Kunde.get_naechste_mitgliedsnummer()
        
        neuer_kunde = Kunde(
            mitgliedsnummer=neue_mitgliedsnummer,
            vorname=daten['vorname'],
            nachname=daten['nachname'],
            firma=daten.get('firma'),
            email=daten.get('email'),
            telefon=daten.get('telefon'),
            strasse=daten.get('strasse'),
            plz=daten.get('plz'),
            ort=daten.get('ort'),
            mitgliedschaft_typ=daten.get('mitgliedschaft_typ', 'Standard'),
            notizen=daten.get('notizen')
        )
        
        db.session.add(neuer_kunde)
        db.session.commit()
        
        return {
            'kunde': neuer_kunde,
            'neu_erstellt': True,
            'message': f'Neuer Kunde erstellt: {neuer_kunde.vollname} ({neue_mitgliedsnummer})'
        }

    def to_dict(self, include_flaschen=False):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        data = {
            'id': self.id,
            'mitgliedsnummer': self.mitgliedsnummer,
            'vorname': self.vorname,
            'nachname': self.nachname,
            'vollname': self.vollname,
            'firma': self.firma,
            'email': self.email,
            'telefon': self.telefon,
            'strasse': self.strasse,
            'plz': self.plz,
            'ort': self.ort,
            'vollstaendige_adresse': self.vollstaendige_adresse,
            'mitglied_seit': self.mitglied_seit.isoformat() if self.mitglied_seit else None,
            'mitgliedschaft_typ': self.mitgliedschaft_typ,
            'mitgliedschaft_dauer_jahre': self.mitgliedschaft_dauer_jahre,
            'ist_aktiv': self.ist_aktiv,
            'anzahl_flaschen': self.anzahl_flaschen,
            'notizen': self.notizen,
            'erstellt_am': self.erstellt_am.isoformat() if self.erstellt_am else None
        }
        
        if include_flaschen:
            data['flaschen'] = [flasche.to_dict() for flasche in self.aktive_flaschen]
        
        return data

# Import für Beziehungen
from datetime import timedelta
