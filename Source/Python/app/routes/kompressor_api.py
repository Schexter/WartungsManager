# Kompressor-System API Routes für WartungsManager
# RESTful API für alle Kompressor-System Funktionen

from flask import Blueprint, jsonify, request
from datetime import datetime, date
import logging
from app.services.kompressor_service import KompressorService, KompressorScheduleService
from app.services.bulk_fuelling_service import BulkFuellvorgangService
from app.services.kunden_service import KundenService
from app.services.flaschen_service import FlaschenService, FlaschenScanService
from app.services.wartungsintervall_service import WartungsintervallService
from app.services.patronenwechsel_service import PatronenwechselService

logger = logging.getLogger(__name__)
bp = Blueprint('kompressor_api', __name__, url_prefix='/api/kompressor')

# =============================================================================
# KOMPRESSOR STEUERUNG API
# =============================================================================

@bp.route('/status', methods=['GET', 'POST'])
def kompressor_status():
    """Gibt aktuellen Kompressor-Status zurück - mit optionaler Shelly-Integration"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            ip = data.get('ip')

            if ip:
                import requests
                try:
                    response = requests.get(f'http://{ip}/rpc/Shelly.GetStatus', timeout=5)
                    if response.status_code == 200:
                        shelly_data = response.json()
                        return jsonify({
                            'success': True,
                            'status': {
                                'output': shelly_data.get('switch:0', {}).get('output', False),
                                'apower': shelly_data.get('switch:0', {}).get('apower', 0),
                                'voltage': shelly_data.get('switch:0', {}).get('voltage', 0),
                                'temperature': shelly_data.get('switch:0', {}).get('temperature', {}),
                                'model': 'Shelly Plus Plug S',
                                'fw_id': shelly_data.get('sys', {}).get('fw_id', '-')
                            }
                        })
                except Exception as e:
                    logger.error(f"Shelly Status Fehler: {str(e)}")
                    return jsonify({'success': False, 'error': str(e)}), 200

        status = KompressorService.get_kompressor_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"API Fehler - Kompressor Status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/control', methods=['POST'])
def kompressor_control():
    """Steuert Kompressor über Shelly"""
    try:
        data = request.get_json() or {}
        ip = data.get('ip')
        action = data.get('action')

        if not ip or not action:
            return jsonify({'success': False, 'error': 'IP und Action erforderlich'}), 400

        import requests

        try:
            if action == 'on':
                response = requests.get(
                    f'http://{ip}/rpc/Switch.Set',
                    params={'id': 0, 'on': False},
                    timeout=2
                )
                import time
                time.sleep(0.5)

                response = requests.get(
                    f'http://{ip}/rpc/Switch.Set',
                    params={'id': 0, 'on': True},
                    timeout=5
                )
            else:
                response = requests.get(
                    f'http://{ip}/rpc/Switch.Set',
                    params={'id': 0, 'on': False},
                    timeout=5
                )

            if response.status_code == 200:
                return jsonify({'success': True, 'action': action})
            else:
                return jsonify({'success': False, 'error': f'HTTP {response.status_code}'}), 200

        except Exception as e:
            logger.error(f"Shelly Control Fehler: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 200

    except Exception as e:
        logger.error(f"API Fehler - Kompressor Control: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/einschalten', methods=['POST'])
def kompressor_einschalten():
    """Schaltet Kompressor ein"""
    try:
        data = request.get_json() or {}
        
        result = KompressorService.kompressor_einschalten(
            fueller=data.get('fueller', 'Unbekannt'),
            oel_getestet=data.get('oel_getestet', False),
            oel_test_ergebnis=data.get('oel_test_ergebnis'),
            oel_tester=data.get('oel_tester'),
            fueller_id=data.get('fueller_id'),
            oel_tester_id=data.get('oel_tester_id')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Kompressor einschalten: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/ausschalten', methods=['POST'])
def kompressor_ausschalten():
    """Schaltet Kompressor aus"""
    try:
        data = request.get_json() or {}
        
        result = KompressorService.kompressor_ausschalten(
            notizen=data.get('notizen')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Kompressor ausschalten: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/notaus', methods=['POST'])
def kompressor_notaus():
    """Not-Aus des Kompressors"""
    try:
        data = request.get_json() or {}
        
        result = KompressorService.kompressor_notaus(
            grund=data.get('grund', 'Not-Aus über API')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Kompressor Not-Aus: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/reset', methods=['POST'])
def kompressor_reset():
    """Passwortgeschützter Reset des Kompressors (auf 00:00:00)"""
    try:
        data = request.get_json() or {}
        
        passwort = data.get('passwort', '')
        grund = data.get('grund', 'Reset über Wartungsinterface')
        
        if not passwort:
            return jsonify({
                'success': False, 
                'error': 'Passwort erforderlich für Reset-Funktion'
            }), 400
        
        result = KompressorService.kompressor_reset_passwortgeschuetzt(
            passwort=passwort,
            grund=grund
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Kompressor Reset: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/betriebsstunden/report', methods=['GET'])
def betriebsstunden_report():
    """Betriebsstunden-Report"""
    try:
        tage = request.args.get('tage', 30, type=int)
        report = KompressorService.get_betriebsstunden_report(tage)
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"API Fehler - Betriebsstunden Report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/wartung/check', methods=['GET'])
def wartung_check():
    """Prüft ob Wartung fällig ist"""
    try:
        check = KompressorScheduleService.check_wartung_faellig()
        return jsonify(check)
        
    except Exception as e:
        logger.error(f"API Fehler - Wartung Check: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/wartungsintervall/status', methods=['GET'])
def wartungsintervall_status():
    """Gibt Wartungsintervall-Status zurück"""
    try:
        status = WartungsintervallService.get_wartungsintervall_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"API Fehler - Wartungsintervall Status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/wartungsintervall/reset', methods=['POST'])
def wartungsintervall_reset():
    """Setzt Wartungsintervall nach Patronenwechsel zurück"""
    try:
        data = request.get_json() or {}
        
        passwort = data.get('passwort', '')
        durchgefuehrt_von = data.get('durchgefuehrt_von', 'Unbekannt')
        wartungsintervall_stunden = data.get('wartungsintervall_stunden', 100.0)
        notizen = data.get('notizen')
        
        if not passwort:
            return jsonify({
                'success': False, 
                'error': 'Passwort erforderlich für Wartungsintervall-Reset'
            }), 400
        
        result = WartungsintervallService.intervall_reset_patronenwechsel(
            passwort=passwort,
            durchgefuehrt_von=durchgefuehrt_von,
            wartungsintervall_stunden=wartungsintervall_stunden,
            notizen=notizen
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Wartungsintervall Reset: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/gesamt-betriebszeit/korrigieren', methods=['POST'])
def gesamt_betriebszeit_korrigieren():
    """Korrigiert die Gesamt-Betriebszeit (einmalige Korrektur)"""
    try:
        data = request.get_json() or {}
        
        passwort = data.get('passwort', '')
        neue_gesamt_stunden = data.get('neue_gesamt_stunden')
        grund = data.get('grund', 'Korrektur der Gesamt-Betriebszeit')
        
        if not passwort:
            return jsonify({
                'success': False, 
                'error': 'Passwort erforderlich für Gesamt-Betriebszeit Korrektur'
            }), 400
            
        if neue_gesamt_stunden is None:
            return jsonify({
                'success': False, 
                'error': 'neue_gesamt_stunden Parameter erforderlich'
            }), 400
        
        result = WartungsintervallService.gesamt_betriebszeit_korrigieren(
            passwort=passwort,
            neue_gesamt_stunden=float(neue_gesamt_stunden),
            grund=grund
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Gesamt-Betriebszeit Korrektur: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# BULK-FÜLLVORGANG API
# =============================================================================

@bp.route('/bulk/status', methods=['GET'])
def bulk_status():
    """Aktueller Bulk-Füllvorgang Status"""
    try:
        status = BulkFuellvorgangService.get_aktiver_bulk_vorgang()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"API Fehler - Bulk Status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/bulk/erstellen', methods=['POST'])
def bulk_erstellen():
    """Erstellt neuen Bulk-Füllvorgang"""
    try:
        data = request.get_json() or {}
        
        result = BulkFuellvorgangService.bulk_vorgang_erstellen(
            operator=data.get('operator', 'Unbekannt'),
            operator_id=data.get('operator_id'),
            flaschen_ids=data.get('flaschen_ids', [])
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Bulk erstellen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk/<int:bulk_id>/flasche/hinzufuegen', methods=['POST'])
def bulk_flasche_hinzufuegen(bulk_id):
    """Fügt Flasche zu Bulk-Füllvorgang hinzu"""
    try:
        data = request.get_json() or {}
        
        result = BulkFuellvorgangService.flasche_hinzufuegen(
            bulk_vorgang_id=bulk_id,
            flasche_id=data.get('flasche_id'),
            ziel_druck=data.get('ziel_druck', 300)
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flasche hinzufügen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk/<int:bulk_id>/flasche/<int:flasche_id>/entfernen', methods=['DELETE'])
def bulk_flasche_entfernen(bulk_id, flasche_id):
    """Entfernt Flasche aus Bulk-Füllvorgang"""
    try:
        result = BulkFuellvorgangService.flasche_entfernen(bulk_id, flasche_id)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flasche entfernen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk/<int:bulk_id>/starten', methods=['POST'])
def bulk_starten(bulk_id):
    """Startet Bulk-Füllvorgang"""
    try:
        result = BulkFuellvorgangService.bulk_vorgang_starten(bulk_id)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Bulk starten: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk/<int:bulk_id>/flasche/<int:flasche_id>/gefuellt', methods=['POST'])
def bulk_flasche_gefuellt(bulk_id, flasche_id):
    """Markiert Flasche als erfolgreich gefüllt"""
    try:
        data = request.get_json() or {}
        
        result = BulkFuellvorgangService.flasche_als_gefuellt_markieren(
            bulk_vorgang_id=bulk_id,
            flasche_id=flasche_id,
            erreicher_druck=data.get('erreicher_druck')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flasche als gefüllt markieren: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk/<int:bulk_id>/flasche/<int:flasche_id>/fehlgeschlagen', methods=['POST'])
def bulk_flasche_fehlgeschlagen(bulk_id, flasche_id):
    """Markiert Flasche als fehlgeschlagen"""
    try:
        data = request.get_json() or {}
        
        result = BulkFuellvorgangService.flasche_als_fehlgeschlagen_markieren(
            bulk_vorgang_id=bulk_id,
            flasche_id=flasche_id,
            grund=data.get('grund')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flasche als fehlgeschlagen markieren: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk/<int:bulk_id>/beenden', methods=['POST'])
def bulk_beenden(bulk_id):
    """Beendet Bulk-Füllvorgang"""
    try:
        data = request.get_json() or {}
        
        result = BulkFuellvorgangService.bulk_vorgang_beenden(
            bulk_vorgang_id=bulk_id,
            notizen=data.get('notizen')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Bulk beenden: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/bulk/<int:bulk_id>/starten-selected', methods=['POST'])
def bulk_starten_selected(bulk_id):
    """Startet Füllung für ausgewählte Flaschen mit Füller-Informationen"""
    try:
        data = request.get_json() or {}
        
        result = BulkFuellvorgangService.bulk_fuellung_mit_auswahl_starten(
            bulk_vorgang_id=bulk_id,
            selected_flaschen_ids=data.get('selected_flaschen_ids', []),
            fueller_name=data.get('fueller'),
            kompressor_id=data.get('kompressor_id'),
            notizen=data.get('notizen')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Bulk Selected starten: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# KUNDEN API
# =============================================================================

@bp.route('/kunden/suchen', methods=['GET'])
def kunden_suchen():
    """Sucht Kunden"""
    try:
        suchbegriff = request.args.get('q', '')
        result = KundenService.kunde_suchen(suchbegriff)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler - Kunden suchen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/kunden/erstellen', methods=['POST'])
def kunde_erstellen():
    """Erstellt oder findet Kunden"""
    try:
        data = request.get_json() or {}
        
        result = KundenService.kunde_erstellen_oder_finden(data)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Kunde erstellen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/kunden/quick', methods=['POST'])
def kunde_quick_anlage():
    """Schnelle Kundenanlage"""
    try:
        data = request.get_json() or {}
        
        result = KundenService.quick_kundenanlage_fuer_fuellung(
            vorname=data.get('vorname', ''),
            nachname=data.get('nachname', ''),
            telefon=data.get('telefon'),
            email=data.get('email')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Quick Kundenanlage: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/kunden/<int:kunde_id>', methods=['GET'])
def kunde_details(kunde_id):
    """Kunde Details abrufen"""
    try:
        result = KundenService.kunde_details_abrufen(kunde_id=kunde_id)
        
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Kunde Details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/kunden/<int:kunde_id>', methods=['PUT'])
def kunde_aktualisieren(kunde_id):
    """Kunde aktualisieren"""
    try:
        data = request.get_json() or {}
        
        result = KundenService.kunde_aktualisieren(kunde_id, data)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Kunde aktualisieren: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/kunden/statistiken', methods=['GET'])
def kunden_statistiken():
    """Kunden-Statistiken"""
    try:
        result = KundenService.get_kunden_statistiken()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler - Kunden Statistiken: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# FLASCHEN API
# =============================================================================

@bp.route('/flaschen/leere-annehmen', methods=['POST'])
def flaschen_leere_annehmen():
    """Nimmt leere Flaschen ohne Kompressor-Betrieb an"""
    try:
        data = request.get_json() or {}
        
        result = FlaschenService.leere_flasche_annehmen(
            barcode=data.get('barcode'),
            kunde_name=data.get('kunde_name'),
            status=data.get('status', 'leer'),
            notizen=data.get('notizen'),
            ohne_kompressor=data.get('ohne_kompressor', True)
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Leere Flaschen annehmen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/suchen', methods=['GET'])
def flaschen_suchen():
    """Sucht Flaschen"""
    try:
        suchbegriff = request.args.get('q', '')
        result = FlaschenService.flasche_suchen(suchbegriff)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler - Flaschen suchen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/erstellen', methods=['POST'])
def flasche_erstellen():
    """Erstellt neue Flasche"""
    try:
        data = request.get_json() or {}
        kunde_id = data.pop('kunde_id', None)
        
        if not kunde_id:
            return jsonify({'success': False, 'error': 'kunde_id erforderlich'}), 400
        
        result = FlaschenService.flasche_erstellen(kunde_id, data)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flasche erstellen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/<int:flasche_id>', methods=['GET'])
def flasche_details(flasche_id):
    """Flasche Details abrufen"""
    try:
        result = FlaschenService.flasche_details_abrufen(flasche_id=flasche_id)
        
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flasche Details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/barcode/<barcode>', methods=['GET'])
def flasche_by_barcode(barcode):
    """Flasche per Barcode finden"""
    try:
        result = FlaschenScanService.flasche_by_barcode_finden(barcode)
        
        status_code = 200 if result['found'] else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flasche Barcode: {str(e)}")
        return jsonify({'found': False, 'error': str(e)}), 500

@bp.route('/flaschen/<int:flasche_id>', methods=['PUT'])
def flasche_aktualisieren(flasche_id):
    """Flasche aktualisieren"""
    try:
        data = request.get_json() or {}
        
        result = FlaschenService.flasche_aktualisieren(flasche_id, data)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flasche aktualisieren: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/<int:flasche_id>/tuev', methods=['POST'])
def flasche_tuev_erneuern(flasche_id):
    """TÜV-Prüfung erneuern"""
    try:
        data = request.get_json() or {}
        
        # Datum-String zu Date konvertieren
        neues_pruef_datum = data.get('neues_pruef_datum')
        if isinstance(neues_pruef_datum, str):
            neues_pruef_datum = datetime.strptime(neues_pruef_datum, '%Y-%m-%d').date()
        
        naechste_pruefung = data.get('naechste_pruefung')
        if naechste_pruefung and isinstance(naechste_pruefung, str):
            naechste_pruefung = datetime.strptime(naechste_pruefung, '%Y-%m-%d').date()
        
        result = FlaschenService.flasche_tuev_erneuern(
            flasche_id=flasche_id,
            neues_pruef_datum=neues_pruef_datum,
            naechste_pruefung=naechste_pruefung
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - TÜV erneuern: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/vormerkung', methods=['POST'])
def flaschen_vormerkung():
    """Setzt Vormerkung für mehrere Flaschen"""
    try:
        data = request.get_json() or {}
        
        result = FlaschenService.flasche_vormerkung_setzen(
            flasche_ids=data.get('flasche_ids', []),
            vorgemerkt=data.get('vorgemerkt', True)
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Flaschen Vormerkung: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/vorgemerkt', methods=['GET'])
def vorgemerkte_flaschen():
    """Gibt vorgemerkte Flaschen zurück"""
    try:
        result = FlaschenService.get_vorgemerkte_flaschen()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler - Vorgemerkte Flaschen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/pruefung-faellig', methods=['GET'])
def pruefung_faellige_flaschen():
    """Gibt prüfungsfällige Flaschen zurück"""
    try:
        result = FlaschenService.get_pruefung_faellige_flaschen()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler - Prüfungsfällige Flaschen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/statistiken', methods=['GET'])
def flaschen_statistiken():
    """Flaschen-Statistiken"""
    try:
        result = FlaschenService.get_flaschen_statistiken()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler - Flaschen Statistiken: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flaschen/scan/multiple', methods=['POST'])
def flaschen_multiple_scan():
    """Verarbeitet mehrere gescannte Barcodes"""
    try:
        data = request.get_json() or {}
        
        result = FlaschenScanService.mehrere_flaschen_scannen(
            barcodes=data.get('barcodes', [])
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Multiple Scan: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# SYSTEM API
# =============================================================================

@bp.route('/system/status', methods=['GET'])
def system_status():
    """Gesamtsystem-Status"""
    try:
        kompressor_status = KompressorService.get_kompressor_status()
        bulk_status = BulkFuellvorgangService.get_aktiver_bulk_vorgang()
        kunden_stats = KundenService.get_kunden_statistiken()
        flaschen_stats = FlaschenService.get_flaschen_statistiken()
        
        return jsonify({
            'kompressor': kompressor_status,
            'bulk_fuellung': bulk_status,
            'kunden': kunden_stats['statistiken'] if kunden_stats['success'] else {},
            'flaschen': flaschen_stats['statistiken'] if flaschen_stats['success'] else {},
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"API Fehler - System Status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# PATRONENWECHSEL API
# =============================================================================

@bp.route('/patronenwechsel/status', methods=['GET'])
def patronenwechsel_status():
    """Gibt aktuellen Patronenwechsel-Status zurück"""
    try:
        status = PatronenwechselService.get_patronenwechsel_dashboard_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"API Fehler - Patronenwechsel Status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/patronenwechsel/durchfuehren', methods=['POST'])
def patronenwechsel_durchfuehren():
    """Führt einen Patronenwechsel durch"""
    try:
        data = request.get_json() or {}
        
        # Validierung der erforderlichen Felder
        if not data.get('passwort'):
            return jsonify({
                'success': False, 
                'error': 'Passwort erforderlich für Patronenwechsel'
            }), 400
            
        if not data.get('durchgefuehrt_von'):
            return jsonify({
                'success': False, 
                'error': 'Name der durchführenden Person erforderlich'
            }), 400
        
        result = PatronenwechselService.patronenwechsel_durchfuehren(
            passwort=data.get('passwort'),
            durchgefuehrt_von=data.get('durchgefuehrt_von'),
            wechsel_datum=data.get('wechsel_datum'),
            molekularsieb_1=data.get('molekularsieb_1', True),
            molekularsieb_2=data.get('molekularsieb_2', True),
            kohle_filter=data.get('kohle_filter', True),
            mol_1_charge=data.get('mol_1_charge'),
            mol_2_charge=data.get('mol_2_charge'),
            kohle_charge=data.get('kohle_charge'),
            alte_mol_1=data.get('alte_mol_1'),
            alte_mol_2=data.get('alte_mol_2'),
            alte_kohle=data.get('alte_kohle'),
            notizen=data.get('notizen')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Patronenwechsel durchführen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/patronenwechsel/konfiguration', methods=['GET'])
def patronenwechsel_konfiguration_get():
    """Gibt aktuelle Patronenwechsel-Konfiguration zurück"""
    try:
        from app.models.patronenwechsel import PatronenwechselKonfiguration
        config = PatronenwechselKonfiguration.get_aktuelle_konfiguration()
        
        return jsonify({
            'success': True,
            'konfiguration': {
                'id': config.id,
                'patronenwechsel_intervall_stunden': config.patronenwechsel_intervall_stunden,
                'warnung_vor_stunden': config.warnung_vor_stunden,
                'erstellt_von': config.erstellt_von,
                'erstellt_am': config.erstellt_am.isoformat(),
                'ist_aktiv': config.ist_aktiv
            }
        })
        
    except Exception as e:
        logger.error(f"API Fehler - Patronenwechsel Konfiguration abrufen: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/patronenwechsel/konfiguration', methods=['POST'])
def patronenwechsel_konfiguration_update():
    """Aktualisiert Patronenwechsel-Konfiguration"""
    try:
        data = request.get_json() or {}
        
        if not data.get('passwort'):
            return jsonify({
                'success': False, 
                'error': 'Passwort erforderlich für Konfiguration'
            }), 400
        
        if not data.get('patronenwechsel_intervall_stunden'):
            return jsonify({
                'success': False, 
                'error': 'Patronenwechsel-Intervall erforderlich'
            }), 400
        
        result = PatronenwechselService.konfiguration_aktualisieren(
            passwort=data.get('passwort'),
            patronenwechsel_intervall_stunden=float(data.get('patronenwechsel_intervall_stunden')),
            warnung_vor_stunden=float(data.get('warnung_vor_stunden', 2.0)),
            erstellt_von=data.get('erstellt_von', 'API-Benutzer')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler - Patronenwechsel Konfiguration aktualisieren: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/patronenwechsel/historie', methods=['GET'])
def patronenwechsel_historie():
    """Gibt Patronenwechsel-Historie zurück"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        historie = PatronenwechselService.get_patronenwechsel_historie(limit=limit)
        return jsonify(historie)
        
    except Exception as e:
        logger.error(f"API Fehler - Patronenwechsel Historie: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/patronenwechsel/validate', methods=['POST'])
def patronenwechsel_validate():
    """Validiert Patronenwechsel-Daten vor Durchführung"""
    try:
        data = request.get_json() or {}
        
        validation = PatronenwechselService.validate_patronenwechsel_daten(
            durchgefuehrt_von=data.get('durchgefuehrt_von', ''),
            molekularsieb_1=data.get('molekularsieb_1', True),
            molekularsieb_2=data.get('molekularsieb_2', True),
            kohle_filter=data.get('kohle_filter', True)
        )
        
        return jsonify(validation)
        
    except Exception as e:
        logger.error(f"API Fehler - Patronenwechsel Validierung: {str(e)}")
        return jsonify({'valid': False, 'errors': [str(e)]}), 500

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404

@bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': 'Something went wrong'}), 500
