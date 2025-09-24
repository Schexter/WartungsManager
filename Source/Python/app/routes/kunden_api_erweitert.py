# Erweiterte Kunden-API mit intelligenten Features
# Erstellt von Hans Hahn - Alle Rechte vorbehalten
# Datum: 04.07.2025

from flask import Blueprint, request, jsonify
from app import db
from app.models.kunden import Kunde
from app.models.flaschen import Flasche
from app.services.intelligenter_kunden_service import IntelligenterKundenService
from datetime import datetime
import qrcode
import io
import base64

# Blueprint erweitern
kunden_api_erweitert = Blueprint('kunden_api_erweitert', __name__)

# ============================================================================
# INTELLIGENTE SUCHE
# ============================================================================

@kunden_api_erweitert.route('/api/kunden/intelligente-suche', methods=['GET'])
def intelligente_kundensuche():
    """
    Intelligente Kundensuche mit Fuzzy-Matching
    
    Query Parameters:
        q: Suchbegriff
        limit: Max. Anzahl Ergebnisse (default: 10)
        min_score: Minimale Ähnlichkeit 0-1 (default: 0.3)
    """
    try:
        suchbegriff = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        min_score = float(request.args.get('min_score', 0.3))
        
        if not suchbegriff:
            return jsonify({
                'success': True,
                'kunden': [],
                'nachricht': 'Kein Suchbegriff angegeben'
            })
        
        # Intelligente Suche durchführen
        ergebnisse = IntelligenterKundenService.intelligente_suche(
            suchbegriff=suchbegriff,
            limit=limit,
            min_score=min_score
        )
        
        # Formatiere Ergebnisse
        kunden_liste = []
        for ergebnis in ergebnisse:
            kunde = ergebnis['kunde']
            kunde_data = kunde.to_dict()
            kunde_data['relevanz_score'] = round(ergebnis['score'], 2)
            kunde_data['match_typ'] = ergebnis['match_type']
            
            # Füge letzte Aktivität hinzu
            if hasattr(kunde, 'letzter_besuch') and kunde.letzter_besuch:
                kunde_data['letzter_besuch'] = kunde.letzter_besuch.isoformat()
                kunde_data['tage_seit_besuch'] = (datetime.utcnow() - kunde.letzter_besuch).days
            
            kunden_liste.append(kunde_data)
        
        return jsonify({
            'success': True,
            'kunden': kunden_liste,
            'anzahl': len(kunden_liste),
            'suchbegriff': suchbegriff
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler bei der Suche: {str(e)}'
        }), 500

# ============================================================================
# QUICK-CREATE
# ============================================================================

@kunden_api_erweitert.route('/api/kunden/quick-create', methods=['POST'])
def quick_kunde_erstellen():
    """
    Schnelles Erstellen eines Kunden mit minimalen Daten
    
    JSON Body:
        vorname: Pflichtfeld
        nachname: Optional
        telefon: Optional
        externe_nummer: Optional
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Keine Daten übermittelt'
            }), 400
        
        # Quick-Create durchführen
        ergebnis = IntelligenterKundenService.quick_kunde_anlegen(
            vorname=data.get('vorname'),
            nachname=data.get('nachname'),
            telefon=data.get('telefon'),
            externe_nummer=data.get('externe_nummer')
        )
        
        if ergebnis['success']:
            kunde_data = ergebnis['kunde'].to_dict()
            
            # QR-Code generieren
            qr_data = f"KUNDE:{ergebnis['kunde'].mitgliedsnummer}"
            kunde_data['qr_code'] = generate_qr_code_base64(qr_data)
            
            return jsonify({
                'success': True,
                'kunde': kunde_data,
                'message': ergebnis['message']
            })
        else:
            # Bei Duplikaten
            if 'duplikate' in ergebnis:
                duplikat_liste = []
                for dup in ergebnis['duplikate']:
                    duplikat_liste.append({
                        'kunde': dup['kunde'].to_dict(),
                        'grund': dup['grund']
                    })
                
                return jsonify({
                    'success': False,
                    'error': ergebnis['error'],
                    'duplikate': duplikat_liste
                }), 409  # Conflict
            else:
                return jsonify({
                    'success': False,
                    'error': ergebnis['error']
                }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Serverfehler: {str(e)}'
        }), 500

# ============================================================================
# DUPLIKAT-PRÜFUNG
# ============================================================================

@kunden_api_erweitert.route('/api/kunden/pruefe-duplikate', methods=['POST'])
def pruefe_duplikate():
    """
    Prüft auf mögliche Duplikate vor dem Anlegen
    
    JSON Body:
        vorname: Zu prüfender Vorname
        nachname: Zu prüfender Nachname
        telefon: Zu prüfende Telefonnummer
        email: Zu prüfende Email
    """
    try:
        data = request.get_json()
        
        duplikate = IntelligenterKundenService.pruefe_duplikate(
            vorname=data.get('vorname'),
            nachname=data.get('nachname'),
            telefon=data.get('telefon'),
            email=data.get('email')
        )
        
        duplikat_liste = []
        for dup in duplikate:
            duplikat_liste.append({
                'kunde': dup['kunde'].to_dict(),
                'grund': dup['grund']
            })
        
        return jsonify({
            'success': True,
            'hat_duplikate': len(duplikat_liste) > 0,
            'duplikate': duplikat_liste
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler bei Duplikat-Prüfung: {str(e)}'
        }), 500

# ============================================================================
# FLASCHEN-VERKNÜPFUNG
# ============================================================================

@kunden_api_erweitert.route('/api/kunden/<int:kunde_id>/flaschen/verknuepfen', methods=['POST'])
def flaschen_verknuepfen(kunde_id):
    """
    Verknüpft mehrere Flaschen mit einem Kunden
    
    JSON Body:
        flasche_ids: Liste von Flaschen-IDs
    """
    try:
        data = request.get_json()
        flasche_ids = data.get('flasche_ids', [])
        
        if not flasche_ids:
            return jsonify({
                'success': False,
                'error': 'Keine Flaschen-IDs angegeben'
            }), 400
        
        ergebnis = IntelligenterKundenService.kunde_mit_flaschen_verknuepfen(
            kunde_id=kunde_id,
            flasche_ids=flasche_ids
        )
        
        if ergebnis['success']:
            return jsonify(ergebnis)
        else:
            return jsonify(ergebnis), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Serverfehler: {str(e)}'
        }), 500

@kunden_api_erweitert.route('/api/kunden/<int:kunde_id>/flaschen', methods=['GET'])
def hole_kunden_flaschen(kunde_id):
    """
    Holt alle Flaschen eines Kunden mit Status
    
    Query Parameters:
        nur_aktive: true/false (default: true)
    """
    try:
        nur_aktive = request.args.get('nur_aktive', 'true').lower() == 'true'
        
        flaschen_mit_status = IntelligenterKundenService.hole_kunden_flaschen(
            kunde_id=kunde_id,
            nur_aktive=nur_aktive
        )
        
        # Formatiere für JSON
        flaschen_liste = []
        for item in flaschen_mit_status:
            flasche_data = item['flasche'].to_dict()
            flasche_data['aktueller_status'] = item['status']
            flasche_data['ist_fuellbereit'] = item['ist_fuellbereit']
            flaschen_liste.append(flasche_data)
        
        return jsonify({
            'success': True,
            'kunde_id': kunde_id,
            'flaschen': flaschen_liste,
            'anzahl': len(flaschen_liste)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der Flaschen: {str(e)}'
        }), 500

# ============================================================================
# FAVORITEN & AKTIVITÄT
# ============================================================================

@kunden_api_erweitert.route('/api/kunden/favoriten', methods=['GET'])
def hole_favoriten_kunden():
    """
    Holt die am häufigsten aktiven Kunden
    
    Query Parameters:
        limit: Anzahl Kunden (default: 10)
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        favoriten = IntelligenterKundenService.hole_favoriten_kunden(limit=limit)
        
        kunden_liste = []
        for kunde in favoriten:
            kunde_data = kunde.to_dict()
            
            # Füge Aktivitätsdaten hinzu
            if hasattr(kunde, 'letzter_besuch') and kunde.letzter_besuch:
                kunde_data['letzter_besuch'] = kunde.letzter_besuch.isoformat()
                kunde_data['tage_seit_besuch'] = (datetime.utcnow() - kunde.letzter_besuch).days
            
            kunden_liste.append(kunde_data)
        
        return jsonify({
            'success': True,
            'favoriten': kunden_liste,
            'anzahl': len(kunden_liste)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der Favoriten: {str(e)}'
        }), 500

@kunden_api_erweitert.route('/api/kunden/<int:kunde_id>/besuch', methods=['POST'])
def aktualisiere_besuch(kunde_id):
    """Aktualisiert den letzten Besuch eines Kunden"""
    try:
        erfolg = IntelligenterKundenService.aktualisiere_letzten_besuch(kunde_id)
        
        if erfolg:
            return jsonify({
                'success': True,
                'message': 'Besuch aktualisiert'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Kunde nicht gefunden'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler: {str(e)}'
        }), 500

# ============================================================================
# STATISTIKEN
# ============================================================================

@kunden_api_erweitert.route('/api/kunden/<int:kunde_id>/statistiken', methods=['GET'])
def hole_kunden_statistiken(kunde_id):
    """Holt detaillierte Statistiken für einen Kunden"""
    try:
        stats = IntelligenterKundenService.statistiken_fuer_kunde(kunde_id)
        
        if stats:
            return jsonify({
                'success': True,
                'statistiken': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Kunde nicht gefunden'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler bei Statistiken: {str(e)}'
        }), 500

# ============================================================================
# QR-CODE GENERIERUNG
# ============================================================================

@kunden_api_erweitert.route('/api/kunden/<int:kunde_id>/qr-code', methods=['GET'])
def generiere_qr_code(kunde_id):
    """Generiert einen QR-Code für einen Kunden"""
    try:
        kunde = Kunde.query.get(kunde_id)
        if not kunde:
            return jsonify({
                'success': False,
                'error': 'Kunde nicht gefunden'
            }), 404
        
        # QR-Code Daten
        qr_data = f"KUNDE:{kunde.mitgliedsnummer}"
        
        # Als Base64
        qr_base64 = generate_qr_code_base64(qr_data)
        
        return jsonify({
            'success': True,
            'kunde_id': kunde_id,
            'mitgliedsnummer': kunde.mitgliedsnummer,
            'qr_code_base64': qr_base64,
            'qr_data': qr_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler bei QR-Code: {str(e)}'
        }), 500

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def generate_qr_code_base64(data):
    """Generiert einen QR-Code als Base64-String"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # In Base64 konvertieren
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
        
    except Exception as e:
        print(f"Fehler bei QR-Code Generierung: {str(e)}")
        return None

# ============================================================================
# ERWEITERTE KUNDEN-AKTIONEN
# ============================================================================

@kunden_api_erweitert.route('/api/kunden/<int:kunde_id>/merge', methods=['POST'])
def kunden_zusammenfuehren(kunde_id):
    """
    Führt zwei Kunden zusammen (Duplikate bereinigen)
    
    JSON Body:
        merge_kunde_id: ID des Kunden der übernommen werden soll
    """
    try:
        data = request.get_json()
        merge_kunde_id = data.get('merge_kunde_id')
        
        if not merge_kunde_id:
            return jsonify({
                'success': False,
                'error': 'Keine merge_kunde_id angegeben'
            }), 400
        
        # Haupt-Kunde
        haupt_kunde = Kunde.query.get(kunde_id)
        merge_kunde = Kunde.query.get(merge_kunde_id)
        
        if not haupt_kunde or not merge_kunde:
            return jsonify({
                'success': False,
                'error': 'Kunde nicht gefunden'
            }), 404
        
        # Übertrage alle Flaschen
        flaschen_uebertragen = 0
        for flasche in merge_kunde.flaschen:
            flasche.kunde_id = kunde_id
            flaschen_uebertragen += 1
        
        # Übertrage fehlende Daten
        if not haupt_kunde.telefon and merge_kunde.telefon:
            haupt_kunde.telefon = merge_kunde.telefon
        if not haupt_kunde.email and merge_kunde.email:
            haupt_kunde.email = merge_kunde.email
        if not haupt_kunde.adresse and merge_kunde.adresse:
            haupt_kunde.adresse = merge_kunde.adresse
        
        # Notiz hinzufügen
        notiz = f"\n[{datetime.utcnow().strftime('%d.%m.%Y')}] Zusammengeführt mit: {merge_kunde.vollname} ({merge_kunde.mitgliedsnummer})"
        haupt_kunde.notizen = (haupt_kunde.notizen or '') + notiz
        
        # Deaktiviere merge_kunde
        merge_kunde.ist_aktiv = False
        merge_kunde.notizen = (merge_kunde.notizen or '') + f"\n[{datetime.utcnow().strftime('%d.%m.%Y')}] Zusammengeführt mit: {haupt_kunde.vollname} ({haupt_kunde.mitgliedsnummer})"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Kunden erfolgreich zusammengeführt',
            'flaschen_uebertragen': flaschen_uebertragen,
            'haupt_kunde': haupt_kunde.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Fehler beim Zusammenführen: {str(e)}'
        }), 500
