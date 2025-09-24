# Patronenwechsel-Routes für WartungsManager
from flask import Blueprint, render_template, request, jsonify
from app.services.patronenwechsel_service import PatronenwechselService
from app.services.print_service import print_service
from app.models.print_jobs import PrintJob, PrinterKonfiguration
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('patronenwechsel', __name__, url_prefix='/patronenwechsel')

@bp.route('/')
def index():
    """Patronenwechsel-Übersichtsseite"""
    return render_template('patronenwechsel/index.html')

@bp.route('/historie')
def historie():
    """Patronenwechsel-Historie Seite"""
    return render_template('patronenwechsel/historie.html')

@bp.route('/konfiguration') 
def konfiguration():
    """Patronenwechsel-Konfiguration Seite"""
    return render_template('patronenwechsel/konfiguration.html')

# ============================================================================
# 62MM DRUCKER APIs - NEU
# ============================================================================

@bp.route('/api/print/<int:wechsel_id>', methods=['POST'])
def print_patronenwechsel_etikett(wechsel_id):
    """Druckt Etiketten für einen Patronenwechsel"""
    
    try:
        data = request.get_json() or {}
        erstellt_von = data.get('erstellt_von', 'Unbekannt')
        drucker_id = data.get('drucker_id')
        
        # Patronenwechsel-Etikett drucken
        result = print_service.create_and_print_patronenwechsel_etikett(
            patronenwechsel_id=wechsel_id,
            erstellt_von=erstellt_von,
            drucker_id=drucker_id
        )
        
        if result['success']:
            logger.info(f"Etikett-Druck erfolgreich: Wechsel {wechsel_id} von {erstellt_von}")
            return jsonify(result), 200
        else:
            logger.error(f"Etikett-Druck fehlgeschlagen: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        error_msg = f"API-Fehler beim Etikett-Druck: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@bp.route('/api/reprint/<int:job_id>', methods=['POST'])
def reprint_etikett(job_id):
    """Wiederholungsdruck eines existierenden Druckjobs"""
    
    try:
        data = request.get_json() or {}
        angefordert_von = data.get('angefordert_von', 'Unbekannt')
        
        result = print_service.reprint_job(
            job_id=job_id,
            angefordert_von=angefordert_von
        )
        
        if result['success']:
            logger.info(f"Wiederholungsdruck erfolgreich: Job {job_id} von {angefordert_von}")
            return jsonify(result), 200
        else:
            logger.error(f"Wiederholungsdruck fehlgeschlagen: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        error_msg = f"API-Fehler beim Wiederholungsdruck: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@bp.route('/api/print/jobs/<int:wechsel_id>', methods=['GET'])
def get_print_jobs_for_wechsel(wechsel_id):
    """Gibt alle Druckjobs für einen Patronenwechsel zurück"""
    
    try:
        jobs = PrintJob.get_jobs_by_patronenwechsel(wechsel_id)
        
        return jsonify({
            'success': True,
            'patronenwechsel_id': wechsel_id,
            'print_jobs': [job.to_dict() for job in jobs],
            'anzahl_jobs': len(jobs)
        }), 200
        
    except Exception as e:
        error_msg = f"Fehler beim Laden der Print-Jobs: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@bp.route('/api/print/queue', methods=['GET'])
def get_print_queue_status():
    """Gibt Status der Druckwarteschlange zurück"""
    
    try:
        pending_jobs = PrintJob.get_pending_jobs()
        recent_jobs = PrintJob.get_recent_jobs(limit=10)
        
        return jsonify({
            'success': True,
            'warteschlange': {
                'wartende_jobs': len(pending_jobs),
                'pending_jobs': [job.to_dict() for job in pending_jobs]
            },
            'letzte_jobs': [job.to_dict() for job in recent_jobs]
        }), 200
        
    except Exception as e:
        error_msg = f"Fehler beim Laden der Warteschlange: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@bp.route('/api/print/queue/process', methods=['POST'])
def process_print_queue():
    """Verarbeitet die Druckwarteschlange"""
    
    try:
        result = print_service.process_print_queue()
        
        if result['success']:
            logger.info(f"Druckwarteschlange verarbeitet: {result.get('verarbeitet', 0)} Jobs")
            return jsonify(result), 200
        else:
            logger.error(f"Warteschlangen-Verarbeitung fehlgeschlagen: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        error_msg = f"API-Fehler bei Warteschlangen-Verarbeitung: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@bp.route('/api/printer/test/<int:drucker_id>', methods=['POST'])
def test_printer(drucker_id):
    """Testet einen spezifischen Drucker"""
    
    try:
        drucker = PrinterKonfiguration.query.get(drucker_id)
        if not drucker:
            return jsonify({
                'success': False,
                'error': f'Drucker {drucker_id} nicht gefunden'
            }), 404
        
        result = print_service.test_printer_connection(drucker)
        
        if result['success']:
            logger.info(f"Drucker-Test erfolgreich: {drucker.name}")
            return jsonify(result), 200
        else:
            logger.error(f"Drucker-Test fehlgeschlagen: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        error_msg = f"API-Fehler beim Drucker-Test: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@bp.route('/api/printer/status', methods=['GET'])
@bp.route('/api/printer/status/<int:drucker_id>', methods=['GET'])
def get_printer_status(drucker_id=None):
    """Gibt Drucker-Status zurück"""
    
    try:
        result = print_service.get_printer_status(drucker_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        error_msg = f"Fehler beim Laden des Drucker-Status: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@bp.route('/api/printers', methods=['GET'])
def get_printers():
    """Gibt alle konfigurierten Drucker zurück"""
    
    try:
        drucker = PrinterKonfiguration.query.filter_by(ist_aktiv=True).all()
        
        return jsonify({
            'success': True,
            'drucker': [{
                'id': d.id,
                'name': d.name,
                'typ': d.drucker_typ,
                'interface': d.interface_typ,
                'ist_standard': d.ist_standard,
                'letzter_test': d.letzter_test.isoformat() if d.letzter_test else None
            } for d in drucker]
        }), 200
        
    except Exception as e:
        error_msg = f"Fehler beim Laden der Drucker: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
