# Print Jobs Model für WartungsManager - 62mm Drucker Integration
# Verwaltung von Druckjobs für Patronenwechsel-Etiketten

from datetime import datetime
from app import db
import json

class PrinterKonfiguration(db.Model):
    """
    Drucker-Konfiguration für verschiedene 62mm Thermodrucker
    """
    
    __tablename__ = 'printer_konfiguration'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Drucker-Details
    name = db.Column(db.String(100), nullable=False, unique=True)  # z.B. "Hauptdrucker"
    drucker_typ = db.Column(db.String(50), nullable=False)  # z.B. "Epson TM-T20II"
    interface_typ = db.Column(db.String(20), nullable=False, default='usb')  # usb, serial, network
    
    # Verbindungsdetails (JSON)
    verbindung_config = db.Column(db.Text, nullable=True)  # JSON-String mit spezifischer Config
    
    # Drucker-Einstellungen
    papier_breite_mm = db.Column(db.Integer, nullable=False, default=62)  # 62mm Standard
    max_zeichen_pro_zeile = db.Column(db.Integer, nullable=False, default=42)  # Bei 62mm ca. 42 Zeichen
    
    # Status
    ist_aktiv = db.Column(db.Boolean, nullable=False, default=True)
    ist_standard = db.Column(db.Boolean, nullable=False, default=False)
    letzter_test = db.Column(db.DateTime, nullable=True)  # Letzter erfolgreicher Test
    
    # System-Info
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    erstellt_von = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<PrinterKonfiguration {self.name}: {self.drucker_typ}>'
    
    @staticmethod
    def get_standard_drucker():
        """Gibt den Standard-Drucker zurück"""
        drucker = PrinterKonfiguration.query.filter_by(ist_standard=True, ist_aktiv=True).first()
        if not drucker:
            # Fallback: ersten aktiven Drucker
            drucker = PrinterKonfiguration.query.filter_by(ist_aktiv=True).first()
        return drucker
    
    def get_verbindung_dict(self):
        """Gibt Verbindungskonfiguration als Dictionary zurück"""
        if self.verbindung_config:
            try:
                return json.loads(self.verbindung_config)
            except:
                return {}
        return {}
    
    def set_verbindung_dict(self, config_dict):
        """Setzt Verbindungskonfiguration aus Dictionary"""
        self.verbindung_config = json.dumps(config_dict, ensure_ascii=False)

class PrintJob(db.Model):
    """
    Druckjobs für 62mm Etiketten
    
    Jeder Druckjob speichert alle Informationen für Wiederholungsdrucke
    """
    
    __tablename__ = 'print_jobs'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Job-Informationen
    job_typ = db.Column(db.String(50), nullable=False)  # 'patronenwechsel_etikett'
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    erstellt_von = db.Column(db.String(100), nullable=False)
    
    # Referenzen
    patronenwechsel_id = db.Column(db.Integer, nullable=True)  # Referenz zu Patronenwechsel
    
    # Drucker
    drucker_id = db.Column(db.Integer, db.ForeignKey('printer_konfiguration.id'), nullable=True)
    drucker = db.relationship('PrinterKonfiguration', backref='print_jobs')
    
    # Etikett-Daten (JSON)
    etikett_daten = db.Column(db.Text, nullable=False)  # JSON mit allen Etikett-Informationen
    
    # Druck-Status
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, printing, success, error, cancelled
    druckversuche = db.Column(db.Integer, nullable=False, default=0)
    letzter_druckversuch = db.Column(db.DateTime, nullable=True)
    gedruckt_am = db.Column(db.DateTime, nullable=True)
    
    # Fehler-Behandlung
    fehler_nachricht = db.Column(db.Text, nullable=True)
    
    # Wiederholungsdrucke
    wiederholungsdrucke = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<PrintJob {self.id}: {self.job_typ} - {self.status}>'
    
    def get_etikett_daten_dict(self):
        """Gibt Etikett-Daten als Dictionary zurück"""
        try:
            return json.loads(self.etikett_daten)
        except:
            return {}
    
    def set_etikett_daten_dict(self, daten_dict):
        """Setzt Etikett-Daten aus Dictionary"""
        self.etikett_daten = json.dumps(daten_dict, ensure_ascii=False, indent=2)
    
    @staticmethod
    def create_patronenwechsel_job(patronenwechsel_id, erstellt_von, drucker_id=None):
        """Erstellt einen neuen Druckjob für Patronenwechsel-Etiketten"""
        from app.models.patronenwechsel import Patronenwechsel
        
        # Patronenwechsel-Daten laden
        wechsel = Patronenwechsel.query.get(patronenwechsel_id)
        if not wechsel:
            raise ValueError(f"Patronenwechsel {patronenwechsel_id} nicht gefunden")
        
        # Standard-Drucker wenn nicht angegeben
        if not drucker_id:
            standard_drucker = PrinterKonfiguration.get_standard_drucker()
            if standard_drucker:
                drucker_id = standard_drucker.id
        
        # Etikett-Daten zusammenstellen
        etikett_daten = {
            'wechsel_id': wechsel.id,
            'wechsel_datum': wechsel.wechsel_datum.isoformat(),
            'durchgefuehrt_von': wechsel.durchgefuehrt_von,
            'betriebsstunden': wechsel.betriebsstunden_bei_wechsel,
            'molekularsieb_1': {
                'gewechselt': wechsel.molekularsieb_patrone_1_gewechselt,
                'charge': wechsel.molekularsieb_1_charge,
                'alte_charge': wechsel.alte_molekularsieb_1_charge
            },
            'molekularsieb_2': {
                'gewechselt': wechsel.molekularsieb_patrone_2_gewechselt,
                'charge': wechsel.molekularsieb_2_charge,
                'alte_charge': wechsel.alte_molekularsieb_2_charge
            },
            'kohle_filter': {
                'gewechselt': wechsel.kohle_filter_gewechselt,
                'charge': wechsel.kohle_filter_charge,
                'alte_charge': wechsel.alte_kohle_filter_charge
            },
            'notizen': wechsel.notizen,
            'naechster_wechsel_bei': wechsel.naechster_wechsel_faellig_bei,
            # QR-Code Daten
            'qr_code_url': f'/patronenwechsel/{wechsel.id}',
            'generiert_am': datetime.utcnow().isoformat()
        }
        
        # Druckjob erstellen
        job = PrintJob(
            job_typ='patronenwechsel_etikett',
            erstellt_von=erstellt_von,
            patronenwechsel_id=patronenwechsel_id,
            drucker_id=drucker_id,
            status='pending'
        )
        job.set_etikett_daten_dict(etikett_daten)
        
        db.session.add(job)
        db.session.commit()
        
        return job
    
    def mark_as_printing(self):
        """Markiert Job als gerade in Bearbeitung"""
        self.status = 'printing'
        self.letzter_druckversuch = datetime.utcnow()
        self.druckversuche += 1
        db.session.commit()
    
    def mark_as_success(self):
        """Markiert Job als erfolgreich gedruckt"""
        self.status = 'success'
        self.gedruckt_am = datetime.utcnow()
        db.session.commit()
    
    def mark_as_error(self, fehler_nachricht):
        """Markiert Job als fehlgeschlagen"""
        self.status = 'error'
        self.fehler_nachricht = fehler_nachricht
        db.session.commit()
    
    def mark_as_cancelled(self):
        """Markiert Job als abgebrochen"""
        self.status = 'cancelled'
        db.session.commit()
    
    def increment_wiederholung(self):
        """Erhöht Wiederholungszähler"""
        self.wiederholungsdrucke += 1
        db.session.commit()
    
    @staticmethod
    def get_pending_jobs():
        """Gibt alle wartenden Druckjobs zurück"""
        return PrintJob.query.filter_by(status='pending').order_by(PrintJob.erstellt_am.asc()).all()
    
    @staticmethod
    def get_recent_jobs(limit=20):
        """Gibt die letzten Druckjobs zurück"""
        return PrintJob.query.order_by(PrintJob.erstellt_am.desc()).limit(limit).all()
    
    @staticmethod
    def get_jobs_by_patronenwechsel(patronenwechsel_id):
        """Gibt alle Druckjobs für einen bestimmten Patronenwechsel zurück"""
        return PrintJob.query.filter_by(patronenwechsel_id=patronenwechsel_id).order_by(PrintJob.erstellt_am.desc()).all()
    
    def to_dict(self):
        """Konvertiert zu Dictionary für JSON API"""
        return {
            'id': self.id,
            'job_typ': self.job_typ,
            'erstellt_am': self.erstellt_am.isoformat(),
            'erstellt_von': self.erstellt_von,
            'patronenwechsel_id': self.patronenwechsel_id,
            'drucker': {
                'id': self.drucker.id if self.drucker else None,
                'name': self.drucker.name if self.drucker else None,
                'typ': self.drucker.drucker_typ if self.drucker else None
            },
            'status': self.status,
            'druckversuche': self.druckversuche,
            'letzter_druckversuch': self.letzter_druckversuch.isoformat() if self.letzter_druckversuch else None,
            'gedruckt_am': self.gedruckt_am.isoformat() if self.gedruckt_am else None,
            'fehler_nachricht': self.fehler_nachricht,
            'wiederholungsdrucke': self.wiederholungsdrucke,
            'etikett_daten': self.get_etikett_daten_dict()
        }

class PrinterStatus(db.Model):
    """Status-Log für Drucker (für Monitoring)"""
    
    __tablename__ = 'printer_status'
    
    id = db.Column(db.Integer, primary_key=True)
    drucker_id = db.Column(db.Integer, db.ForeignKey('printer_konfiguration.id'), nullable=False)
    drucker = db.relationship('PrinterKonfiguration', backref='status_logs')
    
    # Status-Info
    zeitpunkt = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # online, offline, error, testing
    nachricht = db.Column(db.String(255), nullable=True)
    
    # Details (JSON)
    details = db.Column(db.Text, nullable=True)  # JSON mit erweiterten Status-Infos
    
    @staticmethod
    def log_status(drucker_id, status, nachricht=None, details=None):
        """Erstellt einen neuen Status-Log Eintrag"""
        log = PrinterStatus(
            drucker_id=drucker_id,
            status=status,
            nachricht=nachricht
        )
        
        if details:
            log.details = json.dumps(details, ensure_ascii=False)
        
        db.session.add(log)
        db.session.commit()
        
        return log
