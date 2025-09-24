# SQLAlchemy Model für Warteliste-Verwaltung  
from datetime import datetime, date
from app import db

class WartelisteEintrag(db.Model):
    """
    Model für Warteliste-Verwaltung
    
    2-stufiger Workflow:
    1. FLASCHEN ANNEHMEN → Warteliste (Kompressor AUS/AN egal)
    2. FLASCHEN FÜLLEN → Aus Warteliste (Kompressor muss AN)
    """
    
    __tablename__ = 'warteliste_eintraege'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Beziehungen
    flasche_id = db.Column(db.Integer, db.ForeignKey('flaschen.id'), nullable=False)
    
    # Annahme-Daten
    annahme_datum = db.Column(db.Date, nullable=False, default=date.today)
    gewuenschter_druck = db.Column(db.Integer, nullable=False)  # bar
    besonderheiten = db.Column(db.Text, nullable=True)  # z.B. O2-Clean, Sichtprüfung
    prioritaet = db.Column(db.String(20), default='normal')  # hoch, normal, niedrig
    
    # Status-Tracking
    status = db.Column(db.String(30), default='wartend')  # wartend, wird_gefuellt, gefuellt, abgebrochen
    
    # Füll-Prozess (wird beim Füllen ergänzt)
    fueller = db.Column(db.String(100), nullable=True)  # Wer füllt
    luftgemisch = db.Column(db.String(50), nullable=True)  # Luft, Nitrox 32%, etc.
    fuell_start = db.Column(db.DateTime, nullable=True)
    fuell_ende = db.Column(db.DateTime, nullable=True)
    erreichter_druck = db.Column(db.Integer, nullable=True)  # bar
    
    # Zusätzliche Daten
    notizen = db.Column(db.Text, nullable=True)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    aktualisiert_am = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flasche = db.relationship('Flasche', backref='warteliste_eintraege')
    
    def __repr__(self):
        return f'<WartelisteEintrag {self.id}: {self.flasche.flaschennummer if self.flasche else "Unbekannt"} ({self.status})>'
    
    @property
    def kunde_name(self):
        """Name des Kunden über Flasche"""
        if self.flasche and self.flasche.besitzer:
            return self.flasche.besitzer.vollname
        return "Unbekannt"
    
    @property
    def wartezeit_tage(self):
        """Wartezeit in Tagen"""
        heute = date.today()
        return (heute - self.annahme_datum).days
    
    @property
    def ist_express(self):
        """Ist Express-Auftrag (hohe Priorität)"""
        return self.prioritaet == 'hoch'
    
    @property
    def fuell_dauer_minuten(self):
        """Dauer des Füllvorgangs in Minuten"""
        if self.fuell_start and self.fuell_ende:
            delta = self.fuell_ende - self.fuell_start
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def kann_gefuellt_werden(self):
        """Prüft ob Flasche gefüllt werden kann"""
        return (
            self.status == 'wartend' and
            self.flasche and
            self.flasche.ist_fuellbereit
        )
    
    def fuellvorgang_starten(self, fueller, luftgemisch='Luft'):
        """Startet den Füllvorgang"""
        if self.status != 'wartend':
            raise ValueError(f"Kann Füllvorgang nicht starten. Status: {self.status}")
        
        self.status = 'wird_gefuellt'
        self.fueller = fueller
        self.luftgemisch = luftgemisch
        self.fuell_start = datetime.utcnow()
        self.aktualisiert_am = datetime.utcnow()
    
    def fuellvorgang_abschliessen(self, erreichter_druck, notizen=None):
        """Schließt den Füllvorgang ab"""
        if self.status != 'wird_gefuellt':
            raise ValueError(f"Kann Füllvorgang nicht abschließen. Status: {self.status}")
        
        self.status = 'gefuellt'
        self.erreichter_druck = erreichter_druck
        self.fuell_ende = datetime.utcnow()
        
        if notizen:
            if self.notizen:
                self.notizen += f"\n{notizen}"
            else:
                self.notizen = notizen
        
        # Flasche aktualisieren
        if self.flasche:
            self.flasche.letzter_fuellstand = erreichter_druck
            self.flasche.ist_zum_fuellen_vorgemerkt = False
        
        self.aktualisiert_am = datetime.utcnow()
    
    def fuellvorgang_abbrechen(self, grund):
        """Bricht den Füllvorgang ab"""
        self.status = 'abgebrochen'
        self.fuell_ende = datetime.utcnow()
        
        if self.notizen:
            self.notizen += f"\nAbgebrochen: {grund}"
        else:
            self.notizen = f"Abgebrochen: {grund}"
        
        self.aktualisiert_am = datetime.utcnow()
    
    @staticmethod
    def get_aktuelle_warteliste():
        """Gibt aktuelle Warteliste zurück (sortiert nach Priorität)"""
        prioritaet_order = {'hoch': 1, 'normal': 2, 'niedrig': 3}
        
        eintraege = WartelisteEintrag.query.filter_by(status='wartend').join(
            'flasche'
        ).join(
            'flasche.besitzer'
        ).order_by(
            WartelisteEintrag.annahme_datum.asc()
        ).all()
        
        # Nach Priorität sortieren
        return sorted(eintraege, key=lambda x: prioritaet_order.get(x.prioritaet, 2))
    
    @staticmethod
    def get_fuellbare_flaschen():
        """Gibt Flaschen zurück die gefüllt werden können"""
        return WartelisteEintrag.query.filter_by(status='wartend').join(
            'flasche'
        ).filter(
            'flasche.ist_aktiv == True',
            'flasche.pruefung_faellig == False'
        ).order_by(
            WartelisteEintrag.annahme_datum.asc()
        ).all()
    
    @staticmethod
    def get_in_bearbeitung():
        """Gibt Flaschen zurück die gerade gefüllt werden"""
        return WartelisteEintrag.query.filter_by(status='wird_gefuellt').order_by(
            WartelisteEintrag.fuell_start.asc()
        ).all()
    
    @staticmethod
    def get_warteliste_statistiken():
        """Gibt Warteliste-Statistiken zurück"""
        heute = date.today()
        
        # Grundzahlen
        wartend = WartelisteEintrag.query.filter_by(status='wartend').count()
        in_bearbeitung = WartelisteEintrag.query.filter_by(status='wird_gefuellt').count()
        
        # Heute angenommen
        heute_angenommen = WartelisteEintrag.query.filter(
            WartelisteEintrag.annahme_datum == heute
        ).count()
        
        # Heute gefüllt
        heute_gefuellt = WartelisteEintrag.query.filter(
            WartelisteEintrag.status == 'gefuellt',
            db.func.date(WartelisteEintrag.fuell_ende) == heute
        ).count()
        
        # Prioritäten in Warteliste
        prioritaeten = db.session.query(
            WartelisteEintrag.prioritaet,
            db.func.count(WartelisteEintrag.id)
        ).filter_by(status='wartend').group_by(WartelisteEintrag.prioritaet).all()
        
        # Ältester Eintrag
        aeltester = WartelisteEintrag.query.filter_by(status='wartend').order_by(
            WartelisteEintrag.annahme_datum.asc()
        ).first()
        
        # Durchschnittliche Wartezeit (letzte 30 Tage)
        vor_30_tagen = heute - timedelta(days=30)
        
        avg_wartezeit = db.session.query(
            db.func.avg(
                db.func.julianday(WartelisteEintrag.fuell_start) - 
                db.func.julianday(WartelisteEintrag.annahme_datum)
            )
        ).filter(
            WartelisteEintrag.status == 'gefuellt',
            WartelisteEintrag.fuell_ende >= vor_30_tagen
        ).scalar()
        
        # Wartende Kunden (unique)
        wartende_kunden = db.session.query(
            'Kunde.id'
        ).select_from(
            WartelisteEintrag
        ).join(
            'flasche'
        ).join(
            'flasche.besitzer'
        ).filter(
            WartelisteEintrag.status == 'wartend'
        ).distinct().count()
        
        return {
            'wartend': wartend,
            'in_bearbeitung': in_bearbeitung,
            'heute_angenommen': heute_angenommen,
            'heute_gefuellt': heute_gefuellt,
            'wartende_kunden': wartende_kunden,
            'prioritaeten': dict(prioritaeten),
            'aeltester_eintrag': {
                'datum': aeltester.annahme_datum.isoformat() if aeltester else None,
                'tage': aeltester.wartezeit_tage if aeltester else 0,
                'kunde': aeltester.kunde_name if aeltester else None
            },
            'durchschnittliche_wartezeit_tage': round(avg_wartezeit or 0, 1)
        }
    
    @staticmethod
    def get_archiv(tage=30):
        """Gibt Archiv der gefüllten Flaschen zurück"""
        seit_datum = date.today() - timedelta(days=tage)
        
        return WartelisteEintrag.query.filter(
            WartelisteEintrag.status.in_(['gefuellt', 'abgebrochen']),
            WartelisteEintrag.fuell_ende >= seit_datum
        ).order_by(
            WartelisteEintrag.fuell_ende.desc()
        ).all()
    
    @staticmethod
    def bulk_prioritaet_setzen(eintrag_ids, neue_prioritaet):
        """Setzt Priorität für mehrere Einträge"""
        eintraege = WartelisteEintrag.query.filter(
            WartelisteEintrag.id.in_(eintrag_ids),
            WartelisteEintrag.status == 'wartend'
        ).all()
        
        for eintrag in eintraege:
            eintrag.prioritaet = neue_prioritaet
            eintrag.aktualisiert_am = datetime.utcnow()
        
        db.session.commit()
        return len(eintraege)
    
    def to_dict(self, include_flasche=True, include_kunde=True):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        data = {
            'id': self.id,
            'flasche_id': self.flasche_id,
            'annahme_datum': self.annahme_datum.isoformat(),
            'gewuenschter_druck': self.gewuenschter_druck,
            'besonderheiten': self.besonderheiten,
            'prioritaet': self.prioritaet,
            'ist_express': self.ist_express,
            'status': self.status,
            'fueller': self.fueller,
            'luftgemisch': self.luftgemisch,
            'fuell_start': self.fuell_start.isoformat() if self.fuell_start else None,
            'fuell_ende': self.fuell_ende.isoformat() if self.fuell_ende else None,
            'erreichter_druck': self.erreichter_druck,
            'fuell_dauer_minuten': self.fuell_dauer_minuten,
            'wartezeit_tage': self.wartezeit_tage,
            'kann_gefuellt_werden': self.kann_gefuellt_werden,
            'notizen': self.notizen,
            'erstellt_am': self.erstellt_am.isoformat(),
            'aktualisiert_am': self.aktualisiert_am.isoformat()
        }
        
        if include_flasche and self.flasche:
            data['flasche'] = {
                'id': self.flasche.id,
                'flaschennummer': self.flasche.flaschennummer,
                'barcode': self.flasche.barcode,
                'groesse_liter': self.flasche.groesse_liter,
                'max_druck_bar': self.flasche.max_druck_bar,
                'ist_fuellbereit': self.flasche.ist_fuellbereit
            }
        
        if include_kunde and self.flasche and self.flasche.besitzer:
            data['kunde'] = {
                'id': self.flasche.besitzer.id,
                'vollname': self.flasche.besitzer.vollname,
                'mitgliedsnummer': self.flasche.besitzer.mitgliedsnummer,
                'telefon': self.flasche.besitzer.telefon
            }
        
        return data

# Import für Beziehungen
from datetime import timedelta
