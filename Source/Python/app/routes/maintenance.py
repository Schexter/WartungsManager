# Wartungs-Routes für WartungsManager  
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.models import Wartung
from app.services.patrone_vorbereitung_service import PatroneVorbereitungService
from app.services.patrone_einkauf_service import PatroneEinkaufService
from app.services.erweiterter_patronenwechsel_service import ErweiterterPatronenwechselService
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('maintenance', __name__)

@bp.route('/')
def index():
    """Wartungs-Übersichtsseite mit Patronenverwaltung"""
    
    # Verfügbare vorbereitete Patronen laden
    verfuegbare_patronen = PatroneVorbereitungService.get_verfuegbare_patronen()
    
    # Lagerbestand laden
    lagerbestand = PatroneEinkaufService.get_lagerbestand()
    
    # Dashboard-Status für Countdown
    dashboard_status = ErweiterterPatronenwechselService.get_dashboard_status_minimal()
    
    return render_template('maintenance/index.html', 
                         verfuegbare_patronen=verfuegbare_patronen,
                         lagerbestand=lagerbestand,
                         dashboard_status=dashboard_status)

# =============================================================================
# PATRONE VORBEREITEN
# =============================================================================

@bp.route('/patrone-vorbereiten')
def patrone_vorbereiten():
    """Seite für Patronenvorbereitung"""
    historie = PatroneVorbereitungService.get_vorbereitungs_historie(limit=20)
    return render_template('maintenance/patrone_vorbereiten.html', historie=historie)

@bp.route('/api/patrone-vorbereiten', methods=['POST'])
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

@bp.route('/api/etikett-drucken/<int:vorbereitung_id>', methods=['POST'])
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

# =============================================================================
# GEKAUFTE PATRONE EINBUCHEN
# =============================================================================

@bp.route('/patrone-einkauf')
def patrone_einkauf():
    """Seite für Patronen-Einkauf"""
    historie = PatroneEinkaufService.get_einkaufs_historie(limit=20)
    lagerbestand = PatroneEinkaufService.get_lagerbestand()
    return render_template('maintenance/patrone_einkauf.html', 
                         historie=historie, 
                         lagerbestand=lagerbestand)

@bp.route('/api/patrone-einkauf', methods=['POST'])
def api_patrone_einkauf():
    """API: Neuen Patronen-Einkauf einbuchen"""
    try:
        data = request.get_json()
        
        result = PatroneEinkaufService.neuen_einkauf_einbuchen(
            eingekauft_von=data.get('eingekauft_von'),
            lieferant=data.get('lieferant'),
            produkt_name=data.get('produkt_name'),
            produkt_typ=data.get('produkt_typ'),
            menge=data.get('menge'),
            einheit=data.get('einheit'),
            einkauf_datum=data.get('einkauf_datum'),
            einzelpreis=data.get('einzelpreis'),
            gesamtpreis=data.get('gesamtpreis'),
            lieferdatum=data.get('lieferdatum'),
            charge_nummer_lieferant=data.get('charge_nummer_lieferant'),
            haltbarkeitsdatum=data.get('haltbarkeitsdatum'),
            lagerort=data.get('lagerort'),
            notizen=data.get('notizen'),
            kleber_drucken=data.get('kleber_drucken', True)
        )
        
        if result['success']:
            logger.info(f"API: Einkauf eingebucht - {result['message']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API FEHLER bei Einkaufs-Einbuchung: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/api/kleber-drucken/<int:einkauf_id>', methods=['POST'])
def api_kleber_drucken(einkauf_id):
    """API: Kleber für Einkauf drucken"""
    try:
        result = PatroneEinkaufService.kleber_drucken(einkauf_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER beim Kleber-Druck: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/api/lieferung-erhalten/<int:einkauf_id>', methods=['POST'])
def api_lieferung_erhalten(einkauf_id):
    """API: Lieferung als erhalten markieren"""
    try:
        data = request.get_json() or {}
        result = PatroneEinkaufService.lieferung_erhalten(
            einkauf_id, 
            data.get('lieferdatum')
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER bei Lieferung-Update: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

# =============================================================================
# PATRONE WECHSELN
# =============================================================================

@bp.route('/patrone-wechseln')
def patrone_wechseln():
    """Seite für Patronenwechsel mit vorbereiteten Patronen"""
    verfuegbare_patronen = PatroneVorbereitungService.get_verfuegbare_patronen()
    wechsel_historie = ErweiterterPatronenwechselService.get_wechsel_historie_erweitert(limit=10)
    dashboard_status = ErweiterterPatronenwechselService.get_dashboard_status_minimal()
    
    return render_template('maintenance/patrone_wechseln.html',
                         verfuegbare_patronen=verfuegbare_patronen,
                         wechsel_historie=wechsel_historie,
                         dashboard_status=dashboard_status)

@bp.route('/api/patrone-wechseln', methods=['POST'])
def api_patrone_wechseln():
    """API: Patronenwechsel mit vorbereiteten Patronen durchführen"""
    try:
        data = request.get_json()
        
        result = ErweiterterPatronenwechselService.patronenwechsel_mit_vorbereiteten_patronen(
            passwort=data.get('passwort'),
            gewechselt_von=data.get('gewechselt_von'),
            molekularsieb_1_vorbereitung_id=data.get('molekularsieb_1_vorbereitung_id'),
            molekularsieb_2_vorbereitung_id=data.get('molekularsieb_2_vorbereitung_id'),
            kohle_vorbereitung_id=data.get('kohle_vorbereitung_id'),
            alte_mol_1_gewicht=data.get('alte_mol_1_gewicht'),
            alte_mol_2_gewicht=data.get('alte_mol_2_gewicht'),
            alte_kohle_gewicht=data.get('alte_kohle_gewicht'),
            wechsel_grund=data.get('wechsel_grund', 'Planmäßiger Wechsel'),
            alte_patronen_zustand=data.get('alte_patronen_zustand'),
            notizen=data.get('notizen')
        )
        
        if result['success']:
            logger.info(f"API: Patronenwechsel durchgeführt - {result['message']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API FEHLER bei Patronenwechsel: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/api/alte-patrone-entsorgen/<int:protokoll_id>', methods=['POST'])
def api_alte_patrone_entsorgen(protokoll_id):
    """API: Alte Patrone als entsorgt markieren"""
    try:
        data = request.get_json()
        result = ErweiterterPatronenwechselService.alte_patrone_entsorgen(
            protokoll_id,
            data.get('entsorgung_art'),
            data.get('notizen')
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER bei Entsorgung: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

@bp.route('/api/verfuegbare-patronen')
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

@bp.route('/api/patrone-vorbereitung-historie')
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

@bp.route('/api/einkaufs-historie')
def api_einkaufs_historie():
    """API: Einkaufs-Historie abrufen"""
    try:
        limit = int(request.args.get('limit', 50))
        result = PatroneEinkaufService.get_einkaufs_historie(limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER bei Einkaufs-Historie: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/api/lagerbestand')
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

@bp.route('/api/wechsel-historie-erweitert')
def api_wechsel_historie_erweitert():
    """API: Erweiterte Wechsel-Historie abrufen"""
    try:
        limit = int(request.args.get('limit', 20))
        result = ErweiterterPatronenwechselService.get_wechsel_historie_erweitert(limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER bei erweiterter Wechsel-Historie: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'API-Fehler: {str(e)}'
        }), 500

@bp.route('/api/dashboard-status')
def api_dashboard_status():
    """API: Minimaler Dashboard-Status für Countdown"""
    try:
        result = ErweiterterPatronenwechselService.get_dashboard_status_minimal()
        return jsonify(result)
    except Exception as e:
        logger.error(f"API FEHLER bei Dashboard-Status: {str(e)}")
        return jsonify({
            'countdown_text': 'Fehler',
            'countdown_class': 'text-danger',
            'countdown_icon': '❌',
            'error': str(e)
        }), 500

@bp.route('/reset-test')
def reset_test():
    """Reset-Test Seite für Entwicklung und Tests"""
    return render_template('reset_test.html')
