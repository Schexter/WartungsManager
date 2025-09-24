# Erweiterte Flaschen-API mit Prüfungsmanagement
# Blueprint für neue API-Endpunkte

from datetime import date, datetime
from flask import Blueprint, jsonify, request
from app.models.flaschen import Flasche
from app.models.kunden import Kunde
from app import db

# Blueprint erstellen
bp = Blueprint('flaschen_api_erweitert', __name__, url_prefix='/api/flaschen')

@bp.route('/pruefung/faellig')
def pruefung_faellige_flaschen():
    """Flaschen mit fälliger Prüfung"""
    try:
        # Service temporär inline implementieren bis Service verfügbar ist
        vorlauf_tage = request.args.get('vorlauf_tage', 30, type=int)
        
        heute = date.today()
        from datetime import timedelta
        stichtag = heute + timedelta(days=vorlauf_tage)
        
        # Fällige Flaschen suchen
        faellige_flaschen = Flasche.query.filter(
            Flasche.ist_aktiv == True,
            db.or_(
                Flasche.naechste_pruefung == None,
                Flasche.naechste_pruefung <= stichtag
            )
        ).order_by(Flasche.naechste_pruefung).all()
        
        flaschen_daten = []
        for flasche in faellige_flaschen:
            flasche_dict = flasche.to_dict(include_extended=True)
            if hasattr(flasche, 'pruefung_faellig_in_tagen'):
                flasche_dict['pruefung_faellig_tage'] = flasche.pruefung_faellig_in_tagen
            flaschen_daten.append(flasche_dict)
        
        return jsonify({
            'success': True,
            'faellige_flaschen': flaschen_daten,
            'anzahl': len(flaschen_daten),
            'vorlauf_tage': vorlauf_tage
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/pruefung/statistiken')
def pruefung_statistiken():
    """Prüfungsstatistiken"""
    try:
        heute = date.today()
        from datetime import timedelta
        
        # Grundzahlen
        total_flaschen = Flasche.query.filter_by(ist_aktiv=True).count()
        
        # Überfällige Prüfungen
        ueberfaellig = Flasche.query.filter(
            Flasche.ist_aktiv == True,
            db.or_(
                Flasche.naechste_pruefung == None,
                Flasche.naechste_pruefung < heute
            )
        ).count()
        
        # Bald fällige Prüfungen (nächste 30 Tage)
        bald_faellig = Flasche.query.filter(
            Flasche.ist_aktiv == True,
            Flasche.naechste_pruefung.between(
                heute, heute + timedelta(days=30)
            )
        ).count()
        
        # Gültige Prüfungen
        gueltig = Flasche.query.filter(
            Flasche.ist_aktiv == True,
            Flasche.naechste_pruefung > heute + timedelta(days=30)
        ).count()
        
        # Noch nicht benachrichtigt (approximiert)
        nicht_benachrichtigt = ueberfaellig + bald_faellig
        
        statistiken = {
            'total_flaschen': total_flaschen,
            'ueberfaellig': ueberfaellig,
            'bald_faellig': bald_faellig,
            'gueltig': gueltig,
            'kein_pruef_datum': total_flaschen - (ueberfaellig + bald_faellig + gueltig),
            'nicht_benachrichtigt': nicht_benachrichtigt,
            'benachrichtigung_quote': (total_flaschen - nicht_benachrichtigt) / total_flaschen * 100 if total_flaschen > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'statistiken': statistiken
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:flasche_id>/pruefung', methods=['POST'])
def pruefung_aktualisieren(flasche_id):
    """Neue Prüfung eintragen"""
    try:
        flasche = Flasche.query.get_or_404(flasche_id)
        data = request.get_json()
        
        # Prüfungsdatum validieren
        pruef_datum_str = data.get('pruef_datum')
        if not pruef_datum_str:
            return jsonify({
                'success': False,
                'error': 'Prüfungsdatum ist erforderlich'
            }), 400
        
        try:
            pruef_datum = datetime.strptime(pruef_datum_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Ungültiges Datumsformat (YYYY-MM-DD)'
            }), 400
        
        # Nächste Prüfung berechnen (Standard: 2.5 Jahre)
        from datetime import timedelta
        naechste_pruefung = pruef_datum + timedelta(days=912)  # ~2.5 Jahre
        
        # Flasche aktualisieren
        flasche.pruef_datum = pruef_datum
        flasche.naechste_pruefung = naechste_pruefung
        
        # Prüfungsprotokoll erstellen (vereinfacht)
        if hasattr(flasche, 'letzte_pruefung_protokoll'):
            import json
            protokoll = {
                'datum': datetime.now().isoformat(),
                'pruef_datum': pruef_datum.isoformat(),
                'pruefer': data.get('pruefer', ''),
                'pruef_stelle': data.get('pruef_stelle', ''),
                'ergebnis': data.get('ergebnis', 'bestanden'),
                'bemerkungen': data.get('bemerkungen', '')
            }
            flasche.letzte_pruefung_protokoll = json.dumps(protokoll)
        
        # Benachrichtigung zurücksetzen
        if hasattr(flasche, 'pruefung_benachrichtigt'):
            flasche.pruefung_benachrichtigt = False
            flasche.pruefung_benachrichtigung_datum = None
        
        flasche.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Prüfung für Flasche {flasche.flasche_nummer} erfolgreich eingetragen',
            'flasche': flasche.to_dict(include_extended=True)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:flasche_id>/pruefung/benachrichtigung', methods=['POST'])
def pruefung_benachrichtigung_senden(flasche_id):
    """Prüfungsbenachrichtigung als gesendet markieren"""
    try:
        flasche = Flasche.query.get_or_404(flasche_id)
        
        if hasattr(flasche, 'pruefung_benachrichtigt'):
            flasche.pruefung_benachrichtigt = True
            
        if hasattr(flasche, 'pruefung_benachrichtigung_datum'):
            flasche.pruefung_benachrichtigung_datum = date.today()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Benachrichtigung für Flasche {flasche.flasche_nummer} als gesendet markiert'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/pruefung/reminder-liste')
def pruefung_reminder_liste():
    """Liste für Prüfungs-Reminder"""
    try:
        # Vereinfachte Reminder-Liste
        heute = date.today()
        from datetime import timedelta
        
        faellige_flaschen = Flasche.query.filter(
            Flasche.ist_aktiv == True,
            db.or_(
                Flasche.naechste_pruefung == None,
                Flasche.naechste_pruefung <= heute + timedelta(days=30)
            )
        ).all()
        
        reminder_liste = []
        for flasche in faellige_flaschen:
            # Besitzer-Information laden
            besitzer = None
            if hasattr(flasche, 'besitzer') and flasche.besitzer:
                besitzer = {
                    'name': flasche.besitzer.vollname,
                    'telefon': getattr(flasche.besitzer, 'telefon', ''),
                    'email': getattr(flasche.besitzer, 'email', '')
                }
            
            reminder_info = {
                'flasche_id': flasche.id,
                'flasche_nummer': flasche.flasche_nummer,
                'externe_nummer': getattr(flasche, 'externe_flasche_nummer', ''),
                'besitzer': besitzer,
                'naechste_pruefung': flasche.naechste_pruefung.isoformat() if flasche.naechste_pruefung else None,
                'tage_bis_pruefung': flasche.pruefung_faellig_in_tagen if hasattr(flasche, 'pruefung_faellig_in_tagen') else None,
                'status': flasche.pruefung_status_text if hasattr(flasche, 'pruefung_status_text') else 'Unbekannt',
                'ist_ueberfaellig': flasche.pruefung_faellig if hasattr(flasche, 'pruefung_faellig') else False,
                'benachrichtigt': getattr(flasche, 'pruefung_benachrichtigt', False)
            }
            
            reminder_liste.append(reminder_info)
        
        return jsonify({
            'success': True,
            'reminder_liste': reminder_liste,
            'anzahl': len(reminder_liste)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/generiere-flaschennummer', methods=['POST'])
def generiere_flaschennummer():
    """Generiert eine neue interne Flaschennummer"""
    try:
        data = request.get_json()
        kunde_id = data.get('kunde_id')
        
        if not kunde_id:
            return jsonify({
                'success': False,
                'error': 'Kunde-ID ist erforderlich'
            }), 400
        
        kunde = Kunde.query.get(kunde_id)
        if not kunde:
            return jsonify({
                'success': False,
                'error': 'Kunde nicht gefunden'
            }), 404
        
        # Flaschennummer generieren
        flasche_nummer = Flasche.generiere_interne_flaschennummer(kunde, auto_increment=True)
        
        # Barcode generieren
        if hasattr(Flasche, 'generiere_barcode'):
            barcode = Flasche.generiere_barcode(flasche_nummer)
        else:
            # Fallback: Einfache Barcode-Generierung
            barcode = flasche_nummer.replace('-', '').upper()
        
        return jsonify({
            'success': True,
            'flasche_nummer': flasche_nummer,
            'barcode': barcode
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
