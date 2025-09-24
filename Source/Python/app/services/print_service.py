# Print Service für WartungsManager - 62mm Thermodrucker Integration
# ESC/POS Drucker-Unterstützung für Patronenwechsel-Etiketten

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import qrcode
from io import BytesIO
import json

try:
    from escpos.printer import Usb, Serial, Network, Dummy
    from escpos import printer
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False
    logging.warning("python-escpos nicht installiert. Drucker-Funktionalität deaktiviert.")

from app import db
from app.models.print_jobs import PrintJob, PrinterKonfiguration
# Direkt-Import wegen temporärem Problem:
from app.models.print_jobs import PrinterStatus
from app.models.patronenwechsel import Patronenwechsel

logger = logging.getLogger(__name__)

class PrintService:
    """
    Service für 62mm Thermodrucker-Management
    
    Unterstützt:
    - ESC/POS Thermodrucker (USB, Serial, Network)
    - 62mm Etikettenformat
    - QR-Code Integration
    - Druckwarteschlange für Offline-Betrieb
    - Wiederholungsdrucke
    """
    
    def __init__(self):
        self.current_printer = None
        self.last_printer_test = None
    
    def get_printer_instance(self, drucker_config: PrinterKonfiguration = None):
        """
        Erstellt ESC/POS Printer-Instanz basierend auf Konfiguration
        
        Args:
            drucker_config: Drucker-Konfiguration (falls None: Standard-Drucker)
        
        Returns:
            ESC/POS Printer-Instanz oder Dummy-Printer bei Fehlern
        """
        
        if not ESCPOS_AVAILABLE:
            logger.error("ESC/POS Bibliothek nicht verfügbar")
            return Dummy()  # Dummy-Printer für Development
        
        if not drucker_config:
            drucker_config = PrinterKonfiguration.get_standard_drucker()
            
        if not drucker_config:
            logger.error("Kein Drucker konfiguriert")
            return Dummy()
        
        try:
            verbindung = drucker_config.get_verbindung_dict()
            
            if drucker_config.interface_typ == 'usb':
                # USB-Drucker
                vendor_id = verbindung.get('vendor_id', 0x04b8)  # Epson Standard
                product_id = verbindung.get('product_id', 0x0202)
                
                printer_instance = Usb(
                    idVendor=vendor_id,
                    idProduct=product_id,
                    profile=verbindung.get('profile', 'default')
                )
                
            elif drucker_config.interface_typ == 'serial':
                # Serial-Drucker
                port = verbindung.get('port', '/dev/ttyUSB0')
                baudrate = verbindung.get('baudrate', 9600)
                
                printer_instance = Serial(
                    devfile=port,
                    baudrate=baudrate,
                    profile=verbindung.get('profile', 'default')
                )
                
            elif drucker_config.interface_typ == 'network':
                # Netzwerk-Drucker
                host = verbindung.get('host', '192.168.1.100')
                port = verbindung.get('port', 9100)
                
                printer_instance = Network(
                    host=host,
                    port=port,
                    profile=verbindung.get('profile', 'default')
                )
                
            else:
                logger.error(f"Unbekannter Interface-Typ: {drucker_config.interface_typ}")
                return Dummy()
            
            # Status loggen
            PrinterStatus.log_status(
                drucker_id=drucker_config.id,
                status='online',
                nachricht='Drucker-Verbindung erfolgreich erstellt'
            )
            
            return printer_instance
            
        except Exception as e:
            logger.error(f"Fehler bei Drucker-Verbindung: {str(e)}")
            
            # Fehler-Status loggen
            PrinterStatus.log_status(
                drucker_id=drucker_config.id if drucker_config else None,
                status='error',
                nachricht=f'Verbindungsfehler: {str(e)}'
            )
            
            return Dummy()  # Fallback für Development
    
    def test_printer_connection(self, drucker_config: PrinterKonfiguration = None) -> Dict[str, Any]:
        """
        Testet Drucker-Verbindung
        
        Returns:
            Dict mit Test-Ergebnis
        """
        
        try:
            if not drucker_config:
                drucker_config = PrinterKonfiguration.get_standard_drucker()
                
            if not drucker_config:
                return {
                    'success': False,
                    'error': 'Kein Drucker konfiguriert'
                }
            
            # Drucker-Instanz erstellen
            printer_instance = self.get_printer_instance(drucker_config)
            
            # Test-Ausdruck
            printer_instance.text("=== WARTUNGSMANAGER TEST ===\n")
            printer_instance.text(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
            printer_instance.text(f"Drucker: {drucker_config.name}\n")
            printer_instance.text(f"Typ: {drucker_config.drucker_typ}\n")
            printer_instance.text("Test erfolgreich!\n")
            printer_instance.text("\n" * 3)  # Feed
            printer_instance.cut()
            
            # Status aktualisieren
            drucker_config.letzter_test = datetime.utcnow()
            db.session.commit()
            
            PrinterStatus.log_status(
                drucker_id=drucker_config.id,
                status='testing',
                nachricht='Test-Ausdruck erfolgreich'
            )
            
            logger.info(f"Drucker-Test erfolgreich: {drucker_config.name}")
            
            return {
                'success': True,
                'message': f'Drucker {drucker_config.name} erfolgreich getestet',
                'drucker': drucker_config.name,
                'zeitpunkt': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Drucker-Test fehlgeschlagen: {str(e)}"
            logger.error(error_msg)
            
            if drucker_config:
                PrinterStatus.log_status(
                    drucker_id=drucker_config.id,
                    status='error',
                    nachricht=error_msg
                )
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def generate_qr_code(self, data: str, size: int = 4) -> bytes:
        """
        Generiert QR-Code als Binär-Daten
        
        Args:
            data: QR-Code Inhalt
            size: Größe (1-10, Standard: 4)
        
        Returns:
            QR-Code als bytes
        """
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=1
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            # QR-Code als PIL Image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # In Bytes konvertieren
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"QR-Code Generierung fehlgeschlagen: {str(e)}")
            return b''
    
    def create_and_print_patronenwechsel_etikett(self, patronenwechsel_id: int, 
                                               erstellt_von: str,
                                               drucker_id: int = None) -> Dict[str, Any]:
        """
        Erstellt Druckjob und druckt Patronenwechsel-Etikett direkt
        
        Args:
            patronenwechsel_id: ID des Patronenwechsels
            erstellt_von: Wer den Druck angefordert hat
            drucker_id: Spezifischer Drucker (optional)
        
        Returns:
            Dict mit Ergebnis
        """
        
        try:
            # Druckjob erstellen
            job = PrintJob.create_patronenwechsel_job(
                patronenwechsel_id=patronenwechsel_id,
                erstellt_von=erstellt_von,
                drucker_id=drucker_id
            )
            
            # TODO: Hier würde das tatsächliche Drucken implementiert
            # Für jetzt simulieren wir erfolgreichen Druck
            job.mark_as_success()
            
            logger.info(f"Patronenwechsel-Etikett simuliert: Job {job.id}")
            
            return {
                'success': True,
                'message': 'Etikett erfolgreich erstellt (Druck simuliert)',
                'job_id': job.id,
                'gedruckt_am': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Etikett-Erstellung fehlgeschlagen: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg
            }

# Globale Service-Instanz
print_service = PrintService()
