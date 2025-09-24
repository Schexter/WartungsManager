# Dashboard und Maintenance API Routes
from datetime import datetime, date
from flask import Blueprint, jsonify, request
from app.models.kunden import Kunde
from app.models.flaschen import Flasche
from app.services.patrone_vorbereitung_service import PatroneVorbereitungService
from app.services.patrone_einkauf_service import PatroneEinkaufService
from app.services.erweiterter_patronenwechsel_service import ErweiterterPatronenwechselService
from app import db
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('maintenance_api', __name__, url_prefix='/api/maintenance')

@bp.route('/dashboard-status')
def dashboard_status():
    """Dashboard-Status mit allen wichtigen Statistiken"""
    try:
        # Kunden-Statistiken
        kunden_stats = Kunde.get_kunden_statistiken()
        
        # Flaschen-Statistiken  
        flaschen_stats = Flasche.get_flaschen_statistiken()
        
        # System-Status
        system_status = {
            'database_online': True,
            'kompressor_connected': True,  # TODO: Echte Prüfung
            'last_update': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'kunden': kunden_stats,
            'flaschen': flaschen_stats,
            'system': system_status
        })
        
    except Exception as e:
        print(f"Fehler beim Dashboard-Status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'kunden': {
                'total_kunden': 0,
                'aktive_kunden': 0,
                'inaktive_kunden': 0
            },
            'flaschen': {
                'total_flaschen': 0,
                'aktive_flaschen': 0,
                'inaktive_flaschen': 0
            },
            'system': {
                'database_online': False,
                'kompressor_connected': False,
                'last_update': datetime.utcnow().isoformat()
            }
        }), 500

@bp.route('/system-health')
def system_health():
    """System-Gesundheitscheck"""
    try:
        health_checks = {
            'database': True,
            'models_loaded': True,
            'api_responsive': True
        }
        
        # Teste Datenbankverbindung
        try:
            db.session.execute('SELECT 1')
            health_checks['database'] = True
        except:
            health_checks['database'] = False
        
        # Teste Model-Zugriff
        try:
            Kunde.query.count()
            Flasche.query.count()
            health_checks['models_loaded'] = True
        except:
            health_checks['models_loaded'] = False
        
        all_healthy = all(health_checks.values())
        
        return jsonify({
            'healthy': all_healthy,
            'checks': health_checks,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'healthy': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# =============================================================================
# PATRONE VORBEREITEN API ROUTES
# =============================================================================

@bp.route('/patrone-vorbereiten', methods=['POST'])
def api_patrone_vorbereiten():
    """API: Neue Patrone vorbereiten"""
    try:
        data = request.get_json()
        
        result = PatroneVorbereitungService.neue_patrone_vorbereiten(
            vorbereitet_von=data.get('vorbereitet_von'),
            patrone_typ=data.get('patrone_typ'),
            charge_nummer=data.get('charge_nummer'),
            patrone_nummer=data.get('patrone_nummer'),
            gewicht_vor_fuellen=data.get('gewicht_vor_fuellen'),
            gewicht_nach_fuellen=data.get('gewicht_nach_fuellen'),
            material_verwendet=data.get('material_verwendet'),
            notizen=data.get('notizen'),
            etikett_drucken=data.get('etikett_drucken', True)
        )
        
        if result['success']:
            logger.info(f"API: Patrone vorbereitet - {result['message']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API FEHLER bei Patronenvorbereitung: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/patrone-vorbereitung-historie')
def api_patrone_vorbereitung_historie():
    """API: Historie der Patronenvorbereitungen abrufen"""
    try:
        limit = int(request.args.get('limit', 50))
        result = PatroneVorbereitungService.get_vorbereitungs_historie(limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER bei Vorbereitungs-Historie: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/etikett-drucken/<int:vorbereitung_id>', methods=['POST'])
def api_etikett_drucken(vorbereitung_id):
    """API: Etikett für vorbereitete Patrone drucken"""
    try:
        result = PatroneVorbereitungService.etikett_drucken(vorbereitung_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER beim Etikettendruck: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/verfuegbare-patronen')
def api_verfuegbare_patronen():
    """API: Verfügbare vorbereitete Patronen abrufen"""
    try:
        patrone_typ = request.args.get('typ')
        result = PatroneVorbereitungService.get_verfuegbare_patronen(patrone_typ)
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER bei verfügbaren Patronen: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/lagerbestand')
def api_lagerbestand():
    """API: Aktueller Lagerbestand abrufen"""
    try:
        result = PatroneEinkaufService.get_lagerbestand()
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER bei Lagerbestand: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500
