# SQLAlchemy Model für Flaschen-Verwaltung
from datetime import datetime, timedelta
from app import db

class Flasche(db.Model):
    """
    Model für Flaschen-Verwaltung
    
    Erfasst:
    - Flaschen-Registry
    - Besitzer-Zuordnungen
    - Füllhistorie
    - Status und Eigenschaften
    """
    
    __tablename__ = 'flaschen'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Flaschen-Identifikation
    flasche_nummer = db.Column(db.String(50), unique=True, nullable=False)  # Interne Nummer
    externe_flasche_nummer = db.Column(db.String(100), nullable=True)  # Externe/Kunden-Nummer
    barcode = db.Column(db.String(100), unique=True, nullable=True)  # Für Scanning
    
    # Erweiterte Zertifizierung und Rückverfolgbarkeit
    bauart_zulassung = db.Column(db.String(100), nullable=True)  # z.B. "UN DOT-3AA-2015"
    seriennummer = db.Column(db.String(100), nullable=True)  # Hersteller-Seriennummer
    herstellungs_datum = db.Column(db.Date, nullable=True)  # Herstellungsdatum
    
    # Erweiterte Identifikation für Rückverfolgbarkeit
    interne_flaschennummer_auto = db.Column(db.Boolean, default=False)  # Auto-generiert?
    barcode_typ = db.Column(db.String(20), default='CODE128')  # Barcode-Format
    
    # Prüfungsmanagement erweitert
    letzte_pruefung_protokoll = db.Column(db.Text, nullable=True)  # Prüfungsdetails
    pruefung_benachrichtigt = db.Column(db.Boolean, default=False)  # Benachrichtigung gesendet
    pruefung_benachrichtigung_datum = db.Column(db.Date, nullable=True)  # Wann benachrichtigt
    
    # Physische Eigenschaften erweitert
    flaschen_gewicht_kg = db.Column(db.Float, nullable=True)  # Eigengewicht in kg
    ventil_typ = db.Column(db.String(50), nullable=True)  # z.B. "DIN477-1", "M25x2"
    ursprungsland = db.Column(db.String(50), nullable=True)  # Herstellungsland
    
    # Wirtschaftliche Daten
    kaufdatum = db.Column(db.Date, nullable=True)  # Kaufdatum
    garantie_bis = db.Column(db.Date, nullable=True)  # Garantieende
    
    # Integration externe Systeme
    externe_referenzen = db.Column(db.Text, nullable=True)  # JSON für externe IDs
    
    # Besitzer-Information
    kunde_id = db.Column(db.Integer, db.ForeignKey('kunden.id'), nullable=False)
    
    # Flaschen-Eigenschaften
    groesse_liter = db.Column(db.Float, nullable=False, default=11.0)  # Standard 11L
    flaschen_typ = db.Column(db.String(50), default='Standard')  # Standard, Alu, Carbon, etc.
    farbe = db.Column(db.String(30), nullable=True)
    hersteller = db.Column(db.String(100), nullable=True)
    
    # Technische Daten
    pruef_datum = db.Column(db.Date, nullable=True)  # TÜV-Prüfung
    naechste_pruefung = db.Column(db.Date, nullable=True)
    max_druck_bar = db.Column(db.Integer, default=300)
    
    # Status
    ist_aktiv = db.Column(db.Boolean, default=True)
    ist_zum_fuellen_vorgemerkt = db.Column(db.Boolean, default=False)  # Für Bulk-Füllungen
    letzter_fuellstand = db.Column(db.Float, nullable=True)  # Bar
    
    # Zusätzliche Informationen
    notizen = db.Column(db.Text, nullable=True)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (definiert in kunden.py: besitzer)
    
    def __repr__(self):
        return f'<Flasche {self.flasche_nummer}: {self.besitzer.vollname if self.besitzer else "Unbekannt"}>'
    
    @property
    def flaschennummer(self):
        """Alias für Kompatibilität"""
        return self.flasche_nummer
    
    @property
    def pruefung_faellig(self):
        """Prüft ob TÜV-Prüfung fällig ist"""
        if not self.naechste_pruefung:
            return True  # Kein Prüfdatum = fällig
        
        heute = datetime.utcnow().date()
        return self.naechste_pruefung <= heute
    
    @property
    def pruefung_faellig_in_tagen(self):
        """Tage bis zur nächsten Prüfung (negativ = überfällig)"""
        if not self.naechste_pruefung:
            return -999  # Sehr überfällig
        
        heute = datetime.utcnow().date()
        delta = self.naechste_pruefung - heute
        return delta.days
    
    @property
    def pruefung_status_text(self):
        """Lesbarer Prüfungsstatus"""
        if not self.naechste_pruefung:
            return "Kein Prüfdatum"
        
        tage = self.pruefung_faellig_in_tagen
        if tage < 0:
            return f"Überfällig ({abs(tage)} Tage)"
        elif tage <= 30:
            return f"Bald fällig ({tage} Tage)"
        else:
            return f"Gültig ({tage} Tage)"
    
    @property
    def ist_fuellbereit(self):
        """Prüft ob Flasche gefüllt werden kann"""
        return (
            self.ist_aktiv and 
            not self.pruefung_faellig and
            self.max_druck_bar >= 200  # Mindestdruck
        )
    
    @staticmethod
    def generiere_interne_flaschennummer(kunde, auto_increment=True):
        """Generiert eine interne Flaschennummer basierend auf Kunde und Sequenz"""
        try:
            if auto_increment:
                # Format: FL-[MITGLIEDSNUMMER]-[SEQUENZ]
                # Beispiel: FL-M-001-01, FL-M-001-02, etc.
                
                # Sicherstellen, dass Kunde eine Mitgliedsnummer hat
                if not kunde or not hasattr(kunde, 'mitgliedsnummer') or not kunde.mitgliedsnummer:
                    # Fallback: Verwende Kunden-ID
                    prefix = f"FL-K{kunde.id if kunde else '0'}-"
                else:
                    prefix = f"FL-{kunde.mitgliedsnummer}-"
                
                # Finde höchste Sequenznummer für diesen Kunden
                existing_flaschen = Flasche.query.filter(
                    Flasche.flasche_nummer.like(f"{prefix}%")
                ).all()
                
                # Extrahiere Sequenznummern
                sequenzen = []
                for flasche in existing_flaschen:
                    try:
                        sequenz_teil = flasche.flasche_nummer.replace(prefix, '')
                        sequenz = int(sequenz_teil)
                        sequenzen.append(sequenz)
                    except (ValueError, IndexError):
                        continue
                
                # Nächste Sequenznummer
                naechste_sequenz = max(sequenzen) + 1 if sequenzen else 1
                
                return f"{prefix}{naechste_sequenz:02d}"
            else:
                # Manuelle Eingabe erwünscht
                return None
            
        except Exception as e:
            # Fallback: Timestamp-basierte Nummer
            import time
            timestamp = int(time.time())
            if kunde and hasattr(kunde, 'mitgliedsnummer') and kunde.mitgliedsnummer:
                return f"FL-{kunde.mitgliedsnummer}-{timestamp}"
            else:
                return f"FL-TEMP-{timestamp}"
    
    @staticmethod
    def generiere_barcode(flasche_nummer, barcode_typ='CODE128'):
        """Generiert einen Barcode basierend auf der Flaschennummer"""
        try:
            # Bereinige Flaschennummer für Barcode
            barcode_data = flasche_nummer.replace('-', '').upper()
            
            # Füge Präfix für Flaschen hinzu
            if not barcode_data.startswith('FL'):
                barcode_data = f"FL{barcode_data}"
            
            return barcode_data
        except Exception as e:
            # Fallback
            import time
            return f"FL{int(time.time())}"
    
    def aktualisiere_pruefung_benachrichtigung(self, benachrichtigt=True):
        """Markiert Prüfungsbenachrichtigung als gesendet"""
        self.pruefung_benachrichtigt = benachrichtigt
        if benachrichtigt:
            self.pruefung_benachrichtigung_datum = datetime.utcnow().date()
        db.session.commit()
    
    def setze_externe_referenz(self, system_name, externe_id):
        """Fügt externe Referenz hinzu (z.B. für Integration mit anderen Systemen)"""
        import json
        
        try:
            # Lade vorhandene Referenzen
            if self.externe_referenzen:
                referenzen = json.loads(self.externe_referenzen)
            else:
                referenzen = {}
            
            # Füge neue Referenz hinzu
            referenzen[system_name] = externe_id
            
            # Speichere zurück
            self.externe_referenzen = json.dumps(referenzen)
            db.session.commit()
            
        except Exception as e:
            print(f"Fehler beim Setzen externer Referenz: {e}")
    
    def hole_externe_referenz(self, system_name):
        """Holt externe Referenz für bestimmtes System"""
        import json
        
        try:
            if not self.externe_referenzen:
                return None
            
            referenzen = json.loads(self.externe_referenzen)
            return referenzen.get(system_name)
            
        except Exception as e:
            print(f"Fehler beim Holen externer Referenz: {e}")
            return None
    
    @property
    def vollstaendige_identifikation(self):
        """Vollständige Flaschen-Identifikation für Anzeige"""
        parts = [self.flasche_nummer]
        
        if self.externe_flasche_nummer:
            parts.append(f"Ext: {self.externe_flasche_nummer}")
        
        if self.seriennummer:
            parts.append(f"SN: {self.seriennummer}")
            
        return " | ".join(parts)
    def get_flaschen_statistiken():
        """Gibt Flaschen-Statistiken zurück"""
        try:
            total_flaschen = Flasche.query.count()
            aktive_flaschen = Flasche.query.filter_by(ist_aktiv=True).count()
            
            # Prüfung fällige Flaschen
            heute = datetime.utcnow().date()
            pruefung_faellig = Flasche.query.filter(
                Flasche.naechste_pruefung <= heute
            ).count()
            
            # Flaschen-Typen - vereinfacht
            from sqlalchemy import func
            try:
                typen_result = db.session.query(
                    Flasche.flaschen_typ,
                    func.count(Flasche.id)
                ).group_by(Flasche.flaschen_typ).all()
                typen = dict(typen_result)
            except Exception as e:
                print(f"Fehler bei Flaschen-Typen: {e}")
                typen = {}
            
            return {
                'total_flaschen': total_flaschen,
                'aktive_flaschen': aktive_flaschen,
                'inaktive_flaschen': total_flaschen - aktive_flaschen,
                'pruefung_faellig': pruefung_faellig,
                'flaschen_typen': typen
            }
            
        except Exception as e:
            print(f"Fehler bei Flaschen-Statistiken: {str(e)}")
            return {
                'total_flaschen': 0,
                'aktive_flaschen': 0,
                'inaktive_flaschen': 0,
                'pruefung_faellig': 0,
                'flaschen_typen': {}
            }
    
    def to_dict(self, include_besitzer=True, include_extended=False):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        data = {
            'id': self.id,
            'flasche_nummer': self.flasche_nummer,
            'flaschennummer': self.flasche_nummer,  # Alias
            'externe_flasche_nummer': self.externe_flasche_nummer,
            'barcode': self.barcode,
            'bauart_zulassung': self.bauart_zulassung,
            'seriennummer': self.seriennummer,
            'herstellungs_datum': self.herstellungs_datum.isoformat() if self.herstellungs_datum else None,
            'groesse_liter': self.groesse_liter,
            'flaschen_typ': self.flaschen_typ,
            'farbe': self.farbe,
            'hersteller': self.hersteller,
            'pruef_datum': self.pruef_datum.isoformat() if self.pruef_datum else None,
            'naechste_pruefung': self.naechste_pruefung.isoformat() if self.naechste_pruefung else None,
            'pruefung_faellig': self.pruefung_faellig,
            'pruefung_faellig_in_tagen': self.pruefung_faellig_in_tagen,
            'pruefung_status_text': self.pruefung_status_text,
            'max_druck_bar': self.max_druck_bar,
            'ist_aktiv': self.ist_aktiv,
            'ist_zum_fuellen_vorgemerkt': self.ist_zum_fuellen_vorgemerkt,
            'ist_fuellbereit': self.ist_fuellbereit,
            'letzter_fuellstand': self.letzter_fuellstand,
            'notizen': self.notizen,
            'erstellt_am': self.erstellt_am.isoformat() if self.erstellt_am else None
        }
        
        # Erweiterte Felder für Rückverfolgbarkeit
        if include_extended:
            data.update({
                'interne_flaschennummer_auto': getattr(self, 'interne_flaschennummer_auto', False),
                'barcode_typ': getattr(self, 'barcode_typ', 'CODE128'),
                'letzte_pruefung_protokoll': getattr(self, 'letzte_pruefung_protokoll', None),
                'pruefung_benachrichtigt': getattr(self, 'pruefung_benachrichtigt', False),
                'pruefung_benachrichtigung_datum': getattr(self, 'pruefung_benachrichtigung_datum', None).isoformat() if getattr(self, 'pruefung_benachrichtigung_datum', None) else None,
                'flaschen_gewicht_kg': getattr(self, 'flaschen_gewicht_kg', None),
                'ventil_typ': getattr(self, 'ventil_typ', None),
                'ursprungsland': getattr(self, 'ursprungsland', None),
                'kaufdatum': getattr(self, 'kaufdatum', None).isoformat() if getattr(self, 'kaufdatum', None) else None,
                'garantie_bis': getattr(self, 'garantie_bis', None).isoformat() if getattr(self, 'garantie_bis', None) else None,
                'externe_referenzen': getattr(self, 'externe_referenzen', None),
                'vollstaendige_identifikation': self.vollstaendige_identifikation
            })
        
        if include_besitzer and hasattr(self, 'besitzer') and self.besitzer:
            data['besitzer'] = {
                'id': self.besitzer.id,
                'vollname': self.besitzer.vollname,
                'mitgliedsnummer': self.besitzer.mitgliedsnummer
            }
        
        return data
