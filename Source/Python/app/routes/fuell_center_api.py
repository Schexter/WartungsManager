# Füll-Center API für vereinheitlichte Kundenverwaltung
# Erstellt von Hans Hahn - Alle Rechte vorbehalten

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from app.models.kunden import Kunde
from app.models.flaschen import Flasche
from app import db
from sqlalchemy import func, desc

# Blueprint erstellen
bp = Blueprint('fuell_center_api', __name__, url_prefix='/api/fuell-center')

@bp.route('/kunden/favoriten')
def kunden_favoriten():
    """
    Lädt die häufigsten Kunden basierend auf Flaschen-Aktivität
    """
    try:
        # Die 6 aktivsten Kunden der letzten 30 Tage
        vor_30_tagen = datetime.utcnow() - timedelta(days=30)
        
        # Kunden mit den meisten Flaschen-Aktivitäten
        favoriten = db.session.query(
            Kunde,
            func.count(Flasche.id).label('flasche_count')
        ).join(
            Flasche, Kunde.id == Flasche.kunde_id
        ).filter(
            Kunde.ist_aktiv == True,
            Flasche.updated_at >= vor_30_tagen
        ).group_by(
            Kunde.id
        ).order_by(
            desc('flasche_count')
        ).limit(6).all()
        
        result = []
        for kunde, count in favoriten:
            result.append({
                'id': kunde.id,
                'mitgliedsnummer': kunde.mitgliedsnummer,
                'name': kunde.vollname,
                'vorname': kunde.vorname,
                'nachname': kunde.nachname,
                'flaschen_aktivitaet': count
            })
        
        # Falls weniger als 6 Favoriten, fülle mit neuesten Kunden auf
        if len(result) < 6:
            bereits_ids = [k['id'] for k in result]
            weitere_kunden = Kunde.query.filter(
                Kunde.ist_aktiv == True,
                ~Kunde.id.in_(bereits_ids) if bereits_ids else True
            ).order_by(
                Kunde.erstellt_am.desc()
            ).limit(6 - len(result)).all()
            
            for kunde in weitere_kunden:
                result.append({
                    'id': kunde.id,
                    'mitgliedsnummer': kunde.mitgliedsnummer,
                    'name': kunde.vollname,
                    'vorname': kunde.vorname,
                    'nachname': kunde.nachname,
                    'flaschen_aktivitaet': 0
                })
        
        return jsonify({
            'success': True,
            'favoriten': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/kunden/suche')
def kunden_suche():
    """
    Sucht Kunden für Schnell-Annahme
    """
    try:
        suchbegriff = request.args.get('q', '').strip()
        
        if len(suchbegriff) < 2:
            return jsonify({
                'success': True,
                'kunden': []
            })
        
        # Nutze die Suchfunktion aus dem Kunde-Model
        kunden = Kunde.suche_kunde(suchbegriff)
        
        result = []
        for kunde in kunden[:10]:  # Maximal 10 Ergebnisse
            result.append({
                'id': kunde.id,
                'mitgliedsnummer': kunde.mitgliedsnummer,
                'name': kunde.vollname,
                'vorname': kunde.vorname,
                'nachname': kunde.nachname,
                'telefon': kunde.telefon or '',
                'email': kunde.email or '',
                'anzahl_flaschen': kunde.anzahl_flaschen
            })
        
        return jsonify({
            'success': True,
            'kunden': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/annahmen/heute')
def annahmen_heute():
    """
    Lädt die heutigen Flaschen-Annahmen
    """
    try:
        heute_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Flaschen die heute angenommen wurden (status = 'angenommen' oder 'wartend')
        annahmen = Flasche.query.filter(
            Flasche.updated_at >= heute_start,
            Flasche.status.in_(['angenommen', 'wartend', 'in_bearbeitung'])
        ).order_by(
            Flasche.updated_at.desc()
        ).all()
        
        result = []
        for flasche in annahmen:
            kunde = flasche.besitzer if hasattr(flasche, 'besitzer') and flasche.besitzer else None
            
            result.append({
                'id': flasche.id,
                'flasche_nummer': flasche.flasche_nummer,
                'kunde_name': kunde.vollname if kunde else 'Unbekannt',
                'kunde_id': kunde.id if kunde else None,
                'status': flasche.status,
                'angenommen_zeit': flasche.updated_at.strftime('%H:%M'),
                'ist_express': getattr(flasche, 'ist_express', False)
            })
        
        # Gruppiere nach Kunde
        kunden_annahmen = {}
        for annahme in result:
            kunde_key = annahme['kunde_name']
            if kunde_key not in kunden_annahmen:
                kunden_annahmen[kunde_key] = {
                    'kunde_name': annahme['kunde_name'],
                    'kunde_id': annahme['kunde_id'],
                    'flaschen': [],
                    'zeit': annahme['angenommen_zeit'],
                    'hat_express': False
                }
            kunden_annahmen[kunde_key]['flaschen'].append(annahme['flasche_nummer'])
            if annahme['ist_express']:
                kunden_annahmen[kunde_key]['hat_express'] = True
        
        return jsonify({
            'success': True,
            'annahmen': list(kunden_annahmen.values()),
            'anzahl_gesamt': len(annahmen)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/statistiken')
def statistiken():
    """
    Lädt die aktuellen Statistiken für das Dashboard
    """
    try:
        # Flaschen-Status zählen
        wartend = Flasche.query.filter_by(status='wartend', ist_aktiv=True).count()
        in_fuellung = Flasche.query.filter_by(status='in_bearbeitung', ist_aktiv=True).count()
        fertig = Flasche.query.filter_by(status='fertig', ist_aktiv=True).count()
        
        # Kompressor-Status
        from app.models.kompressor import KompressorLauf
        aktiver_lauf = KompressorLauf.query.filter_by(ende_zeit=None).first()
        kompressor_an = aktiver_lauf is not None
        
        return jsonify({
            'success': True,
            'statistiken': {
                'wartend': wartend,
                'in_fuellung': in_fuellung,
                'fertig': fertig,
                'kompressor_an': kompressor_an
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/warteliste')
def warteliste():
    """
    Lädt die Warteliste für Füllungen
    """
    try:
        # Flaschen die auf Füllung warten
        wartende_flaschen = Flasche.query.filter_by(
            status='wartend',
            ist_aktiv=True
        ).order_by(
            Flasche.updated_at
        ).all()
        
        result = []
        for flasche in wartende_flaschen:
            kunde = flasche.besitzer if hasattr(flasche, 'besitzer') and flasche.besitzer else None
            
            result.append({
                'id': flasche.id,
                'flasche_nummer': flasche.flasche_nummer,
                'kunde_name': kunde.vollname if kunde else 'Unbekannt',
                'kunde_id': kunde.id if kunde else None,
                'ziel_druck': getattr(flasche, 'ziel_druck', 200),
                'ist_express': getattr(flasche, 'ist_express', False),
                'wartezeit_minuten': int((datetime.utcnow() - flasche.updated_at).total_seconds() / 60)
            })
        
        return jsonify({
            'success': True,
            'warteliste': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/fertige-flaschen')
def fertige_flaschen():
    """
    Lädt fertige Flaschen zur Abholung
    """
    try:
        # Flaschen die fertig sind
        fertige = Flasche.query.filter_by(
            status='fertig',
            ist_aktiv=True
        ).order_by(
            Flasche.updated_at.desc()
        ).all()
        
        result = []
        for flasche in fertige:
            kunde = flasche.besitzer if hasattr(flasche, 'besitzer') and flasche.besitzer else None
            
            result.append({
                'id': flasche.id,
                'flasche_nummer': flasche.flasche_nummer,
                'kunde_name': kunde.vollname if kunde else 'Unbekannt',
                'kunde_id': kunde.id if kunde else None,
                'fertig_zeit': flasche.updated_at.strftime('%H:%M'),
                'preis': getattr(flasche, 'preis', 0.0)
            })
        
        # Gruppiere nach Kunde
        kunden_flaschen = {}
        for flasche in result:
            kunde_key = f"{flasche['kunde_id']}_{flasche['kunde_name']}"
            if kunde_key not in kunden_flaschen:
                kunden_flaschen[kunde_key] = {
                    'kunde_name': flasche['kunde_name'],
                    'kunde_id': flasche['kunde_id'],
                    'flaschen': [],
                    'gesamt_preis': 0.0,
                    'fertig_zeit': flasche['fertig_zeit']
                }
            kunden_flaschen[kunde_key]['flaschen'].append(flasche['flasche_nummer'])
            kunden_flaschen[kunde_key]['gesamt_preis'] += flasche['preis']
        
        return jsonify({
            'success': True,
            'fertige_flaschen': list(kunden_flaschen.values())
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
