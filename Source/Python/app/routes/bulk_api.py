# Bulk-Filling API Routes für WartungsManager
from flask import Blueprint, jsonify, request
from app.services.bulk_fuelling_service import BulkFuellvorgangService
from app.services.flaschen_service import FlaschenService
from app.services.kunden_service import KundenService
from app.models import KompressorBetrieb
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('bulk_api', __name__, url_prefix='/api/kompressor/bulk')

# ============================================================================
# BULK-VORGANG MANAGEMENT
# ============================================================================

@bp.route('/erstellen', methods=['POST'])
def bulk_vorgang_erstellen():
    """
    Erstellt neuen Bulk-Füllvorgang
    
    POST /api/kompressor/bulk/erstellen
    Body: {
        "operator": "Name des Operators",
        "operator_id": 123 (optional),
        "flaschen_ids": [1, 2, 3] (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'operator' not in data:
            return jsonify({
                'success': False,
                'error': 'Operator-Name ist erforderlich'
            }), 400
        
        operator = data['operator'].strip()
        operator_id = data.get('operator_id')
        flaschen_ids = data.get('flaschen_ids', [])
        
        if not operator:
            return jsonify({
                'success': False,
                'error': 'Operator-Name darf nicht leer sein'
            }), 400
        
        # Service aufrufen
        result = BulkFuellvorgangService.bulk_vorgang_erstellen(
            operator=operator,
            operator_id=operator_id,
            flaschen_ids=flaschen_ids
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler bulk_vorgang_erstellen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

@bp.route('/status')
def bulk_status():
    """
    Gibt aktuellen Bulk-Füllvorgang Status zurück
    
    GET /api/kompressor/bulk/status
    """
    try:
        result = BulkFuellvorgangService.get_aktiver_bulk_vorgang()
        
        return jsonify({
            'success': True,
            'hat_aktiven_bulk': result['ist_aktiv'],
            'bulk_vorgang': result['aktiver_vorgang'],
            'flaschen_status': result.get('flaschen_status'),
            'error': result.get('error')
        })
        
    except Exception as e:
        logger.error(f"API Fehler bulk_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Abrufen des Status'
        }), 500

@bp.route('/<int:bulk_id>/starten', methods=['POST'])
def bulk_vorgang_starten(bulk_id):
    """
    Startet Bulk-Füllvorgang
    
    POST /api/kompressor/bulk/{bulk_id}/starten
    """
    try:
        result = BulkFuellvorgangService.bulk_vorgang_starten(bulk_id)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler bulk_vorgang_starten: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

@bp.route('/<int:bulk_id>/beenden', methods=['POST'])
def bulk_vorgang_beenden(bulk_id):
    """
    Beendet Bulk-Füllvorgang
    
    POST /api/kompressor/bulk/{bulk_id}/beenden
    Body: {
        "notizen": "Optional Abschluss-Notizen"
    }
    """
    try:
        data = request.get_json() or {}
        notizen = data.get('notizen')
        
        result = BulkFuellvorgangService.bulk_vorgang_beenden(bulk_id, notizen)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler bulk_vorgang_beenden: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

# ============================================================================
# FLASCHEN MANAGEMENT
# ============================================================================

@bp.route('/<int:bulk_id>/flasche/hinzufuegen', methods=['POST'])
def flasche_hinzufuegen(bulk_id):
    """
    Fügt Flasche zum Bulk-Füllvorgang hinzu
    
    POST /api/kompressor/bulk/{bulk_id}/flasche/hinzufuegen
    Body: {
        "flasche_id": 123,
        "ziel_druck": 300
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'flasche_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Flasche-ID ist erforderlich'
            }), 400
        
        flasche_id = data['flasche_id']
        ziel_druck = data.get('ziel_druck', 300)
        
        # Validierung
        if not isinstance(flasche_id, int) or flasche_id <= 0:
            return jsonify({
                'success': False,
                'error': 'Ungültige Flasche-ID'
            }), 400
        
        if not isinstance(ziel_druck, int) or ziel_druck < 100 or ziel_druck > 400:
            return jsonify({
                'success': False,
                'error': 'Ziel-Druck muss zwischen 100 und 400 Bar liegen'
            }), 400
        
        # Service aufrufen
        result = BulkFuellvorgangService.flasche_hinzufuegen(bulk_id, flasche_id, ziel_druck)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler flasche_hinzufuegen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

@bp.route('/<int:bulk_id>/flasche/<int:flasche_id>/entfernen', methods=['DELETE'])
def flasche_entfernen(bulk_id, flasche_id):
    """
    Entfernt Flasche aus Bulk-Füllvorgang
    
    DELETE /api/kompressor/bulk/{bulk_id}/flasche/{flasche_id}/entfernen
    """
    try:
        result = BulkFuellvorgangService.flasche_entfernen(bulk_id, flasche_id)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler flasche_entfernen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

@bp.route('/<int:bulk_id>/flasche/<int:flasche_id>/gefuellt', methods=['POST'])
def flasche_gefuellt(bulk_id, flasche_id):
    """
    Markiert Flasche als erfolgreich gefüllt
    
    POST /api/kompressor/bulk/{bulk_id}/flasche/{flasche_id}/gefuellt
    Body: {
        "erreicher_druck": 300,
        "fueller_name": "Optional",
        "kompressor_id": "Optional"
    }
    """
    try:
        data = request.get_json() or {}
        erreicher_druck = data.get('erreicher_druck')
        fueller_name = data.get('fueller_name')
        kompressor_id = data.get('kompressor_id')
        
        # Validierung
        if erreicher_druck and (not isinstance(erreicher_druck, int) or erreicher_druck < 50 or erreicher_druck > 450):
            return jsonify({
                'success': False,
                'error': 'Erreichter Druck muss zwischen 50 und 450 Bar liegen'
            }), 400
        
        # Service aufrufen
        result = BulkFuellvorgangService.flasche_als_gefuellt_markieren(
            bulk_id, flasche_id, erreicher_druck
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler flasche_gefuellt: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

@bp.route('/<int:bulk_id>/flasche/<int:flasche_id>/fehlgeschlagen', methods=['POST'])
def flasche_fehlgeschlagen(bulk_id, flasche_id):
    """
    Markiert Flasche als fehlgeschlagen
    
    POST /api/kompressor/bulk/{bulk_id}/flasche/{flasche_id}/fehlgeschlagen
    Body: {
        "grund": "Grund für Fehlschlag"
    }
    """
    try:
        data = request.get_json() or {}
        grund = data.get('grund', 'Unbekannter Fehler')
        
        # Service aufrufen
        result = BulkFuellvorgangService.flasche_als_fehlgeschlagen_markieren(
            bulk_id, flasche_id, grund
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler flasche_fehlgeschlagen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

# ============================================================================
# FLASCHEN-SUCHE UND ERSTELLUNG
# ============================================================================

@bp.route('/flaschen/barcode/<barcode>')
def flasche_by_barcode(barcode):
    """
    Sucht Flasche anhand Barcode
    
    GET /api/kompressor/bulk/flaschen/barcode/{barcode}
    """
    try:
        # FlaschenService verwenden falls verfügbar
        try:
            result = FlaschenService.flasche_by_barcode(barcode)
        except:
            # Fallback: Direkte DB-Abfrage
            from app.models import Flasche
            flasche = Flasche.query.filter_by(barcode=barcode).first()
            if not flasche:
                flasche = Flasche.query.filter_by(flaschennummer=barcode).first()
            
            if flasche:
                result = {
                    'found': True,
                    'flasche': flasche.to_dict(include_besitzer=True)
                }
            else:
                result = {'found': False}
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler flasche_by_barcode: {str(e)}")
        return jsonify({
            'found': False,
            'error': 'Fehler bei Flasche-Suche'
        }), 500

@bp.route('/flaschen/erstellen', methods=['POST'])
def flasche_erstellen():
    """
    Erstellt neue Flasche
    
    POST /api/kompressor/bulk/flaschen/erstellen
    Body: {
        "kunde_id": 123,
        "barcode": "12345",
        "flasche_nummer": "FL001",
        "typ": "Stahl",
        "groesse": 12
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'kunde_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Kunde-ID ist erforderlich'
            }), 400
        
        # FlaschenService verwenden falls verfügbar
        try:
            result = FlaschenService.flasche_erstellen(data)
        except:
            # Fallback: Direkte Erstellung
            from app.models import Flasche
            from app import db
            
            flasche = Flasche(
                besitzer_id=data['kunde_id'],
                barcode=data.get('barcode'),
                flaschennummer=data.get('flasche_nummer'),
                typ=data.get('typ', 'Stahl'),
                groesse_liter=data.get('groesse', 12)
            )
            
            db.session.add(flasche)
            db.session.commit()
            
            result = {
                'success': True,
                'flasche': flasche.to_dict(include_besitzer=True)
            }
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler flasche_erstellen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

# ============================================================================
# KUNDEN-MANAGEMENT
# ============================================================================

@bp.route('/kunden/suchen')
def kunden_suchen():
    """
    Sucht Kunden anhand Suchbegriff
    
    GET /api/kompressor/bulk/kunden/suchen?q=suchbegriff
    """
    try:
        suchbegriff = request.args.get('q', '').strip()
        
        if len(suchbegriff) < 2:
            return jsonify({
                'success': False,
                'error': 'Suchbegriff muss mindestens 2 Zeichen haben',
                'kunden': []
            })
        
        # KundenService verwenden falls verfügbar
        try:
            result = KundenService.kunden_suchen(suchbegriff)
        except:
            # Fallback: Direkte DB-Abfrage
            from app.models import Kunde
            kunden = Kunde.query.filter(
                db.or_(
                    Kunde.vorname.ilike(f'%{suchbegriff}%'),
                    Kunde.nachname.ilike(f'%{suchbegriff}%'),
                    Kunde.telefon.ilike(f'%{suchbegriff}%'),
                    Kunde.email.ilike(f'%{suchbegriff}%')
                )
            ).limit(10).all()
            
            result = {
                'success': True,
                'kunden': [k.to_dict() for k in kunden]
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler kunden_suchen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Fehler bei Kunden-Suche',
            'kunden': []
        }), 500

@bp.route('/kunden/quick', methods=['POST'])
def kunde_quick_erstellen():
    """
    Erstellt schnell neuen Kunden
    
    POST /api/kompressor/bulk/kunden/quick
    Body: {
        "vorname": "Max",
        "nachname": "Mustermann",
        "telefon": "0123456789",
        "email": "max@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'vorname' not in data or 'nachname' not in data:
            return jsonify({
                'success': False,
                'error': 'Vor- und Nachname sind erforderlich'
            }), 400
        
        # KundenService verwenden falls verfügbar
        try:
            result = KundenService.kunde_erstellen(data)
        except:
            # Fallback: Direkte Erstellung
            from app.models import Kunde
            from app import db
            
            kunde = Kunde(
                vorname=data['vorname'].strip(),
                nachname=data['nachname'].strip(),
                telefon=data.get('telefon', '').strip(),
                email=data.get('email', '').strip()
            )
            
            db.session.add(kunde)
            db.session.commit()
            
            result = {
                'success': True,
                'kunde': kunde.to_dict()
            }
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API Fehler kunde_quick_erstellen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Interner Server-Fehler'
        }), 500

# ============================================================================
# STATISTIKEN UND STATUS
# ============================================================================

@bp.route('/statistiken')
def bulk_statistiken():
    """
    Gibt Bulk-Füllvorgang Statistiken zurück
    
    GET /api/kompressor/bulk/statistiken
    """
    try:
        from app.models.bulk_fuelling import BulkFuellvorgang
        
        stats = BulkFuellvorgang.get_statistiken()
        
        # Zusätzliche Live-Statistiken
        vorgemerkte = BulkFuellvorgangService.get_vorgemerkte_flaschen()
        
        return jsonify({
            'success': True,
            'historische_statistiken': stats,
            'aktuelle_vorgemerkten_flaschen': vorgemerkte['anzahl'],
            'vorgemerkte_flaschen': vorgemerkte['flaschen']
        })
        
    except Exception as e:
        logger.error(f"API Fehler bulk_statistiken: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Abrufen der Statistiken'
        }), 500

@bp.route('/vorgemerkte-flaschen')
def vorgemerkte_flaschen():
    """
    Gibt alle vorgemerkten Flaschen zurück
    
    GET /api/kompressor/bulk/vorgemerkte-flaschen
    """
    try:
        result = BulkFuellvorgangService.get_vorgemerkte_flaschen()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler vorgemerkte_flaschen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Abrufen vorgemerkter Flaschen',
            'flaschen': []
        }), 500

# ============================================================================
# KOMPRESSOR-STATUS FÜR BULK-FILLING
# ============================================================================

@bp.route('/kompressor-status')
def kompressor_status_bulk():
    """
    Gibt Kompressor-Status für Bulk-Filling zurück
    
    GET /api/kompressor/bulk/kompressor-status
    """
    try:
        aktiver_kompressor = KompressorBetrieb.get_aktiver_kompressor()
        
        if aktiver_kompressor:
            return jsonify({
                'success': True,
                'ist_an': True,
                'aktiver_kompressor': aktiver_kompressor.to_dict(),
                'kann_bulk_starten': True,
                'fueller': aktiver_kompressor.fueller,
                'seit': aktiver_kompressor.start_zeit.isoformat() if aktiver_kompressor.start_zeit else None
            })
        else:
            return jsonify({
                'success': True,
                'ist_an': False,
                'aktiver_kompressor': None,
                'kann_bulk_starten': False,
                'nachricht': 'Kompressor muss zuerst gestartet werden'
            })
        
    except Exception as e:
        logger.error(f"API Fehler kompressor_status_bulk: {str(e)}")
        return jsonify({
            'success': False,
            'ist_an': False,
            'error': 'Fehler beim Kompressor-Status-Check'
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'API-Endpunkt nicht gefunden'
    }), 404

@bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'HTTP-Methode nicht erlaubt'
    }), 405

@bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Interner Server-Fehler'
    }), 500
