# Warteliste-Management API Routes
from datetime import datetime, date
from flask import Blueprint, jsonify, request, send_file
from app.models.warteliste import WartelisteEintrag
from app.models.flaschen import Flasche
from app.models.kunden import Kunde
from app import db
import tempfile
# import openpyxl  # Temporarily disabled
# from openpyxl.styles import Font, Alignment, PatternFill

bp = Blueprint('warteliste_api', __name__, url_prefix='/api/warteliste')

@bp.route('/hinzufuegen', methods=['POST'])
def zur_warteliste_hinzufuegen():
    """Flasche zur Warteliste hinzufügen"""
    try:
        data = request.get_json()
        
        # Prüfe ob Flasche bereits in Warteliste
        existing = WartelisteEintrag.query.filter_by(
            flasche_id=data['flasche_id'],
            status='wartend'
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'Flasche ist bereits in der Warteliste'
            }), 400
        
        # Neuen Warteliste-Eintrag erstellen
        eintrag = WartelisteEintrag(
            flasche_id=data['flasche_id'],
            gewuenschter_druck=data['gewuenschter_druck'],
            besonderheiten=data.get('besonderheiten'),
            prioritaet=data.get('prioritaet', 'normal'),
            annahme_datum=datetime.strptime(data['annahme_datum'], '%Y-%m-%d').date(),
            status='wartend',
            erstellt_am=datetime.utcnow()
        )
        
        db.session.add(eintrag)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'warteliste_id': eintrag.id,
            'message': 'Flasche erfolgreich zur Warteliste hinzugefügt'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/liste')
def warteliste_laden():
    """Aktuelle Warteliste laden"""
    try:
        # Warteliste nach Priorität und Datum sortiert
        prioritaet_order = {'hoch': 1, 'normal': 2, 'niedrig': 3}
        
        eintraege = WartelisteEintrag.query.filter_by(status='wartend').join(
            Flasche
        ).join(
            Kunde
        ).add_columns(
            Flasche.flasche_nummer,
            Flasche.barcode,
            Kunde.vorname,
            Kunde.nachname
        ).order_by(
            WartelisteEintrag.annahme_datum.asc()
        ).all()
        
        warteliste = []
        for eintrag, flasche_nummer, barcode, vorname, nachname in eintraege:
            warteliste.append({
                'id': eintrag.id,
                'flasche_id': eintrag.flasche_id,
                'flasche_nummer': flasche_nummer,
                'barcode': barcode,
                'kunde_name': f"{vorname} {nachname}",
                'gewuenschter_druck': eintrag.gewuenschter_druck,
                'besonderheiten': eintrag.besonderheiten,
                'prioritaet': eintrag.prioritaet,
                'annahme_datum': eintrag.annahme_datum.isoformat(),
                'erstellt_am': eintrag.erstellt_am.isoformat()
            })
        
        # Nach Priorität sortieren
        warteliste.sort(key=lambda x: prioritaet_order.get(x['prioritaet'], 2))
        
        return jsonify({
            'success': True,
            'warteliste': warteliste,
            'count': len(warteliste)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:warteliste_id>', methods=['DELETE'])
def aus_warteliste_entfernen(warteliste_id):
    """Flasche aus Warteliste entfernen"""
    try:
        eintrag = WartelisteEintrag.query.get_or_404(warteliste_id)
        
        db.session.delete(eintrag)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Flasche aus Warteliste entfernt'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/statistiken')
def warteliste_statistiken():
    """Warteliste-Statistiken laden"""
    try:
        heute = date.today()
        
        # Anzahl in Warteliste
        in_warteliste = WartelisteEintrag.query.filter_by(status='wartend').count()
        
        # Heute angenommen
        heute_angenommen = WartelisteEintrag.query.filter(
            WartelisteEintrag.annahme_datum == heute
        ).count()
        
        # Wartende Kunden (unique)
        wartende_kunden = db.session.query(
            Kunde.id
        ).join(
            Flasche
        ).join(
            WartelisteEintrag
        ).filter(
            WartelisteEintrag.status == 'wartend'
        ).distinct().count()
        
        # Älteste Flasche
        aeltester_eintrag = WartelisteEintrag.query.filter_by(
            status='wartend'
        ).order_by(
            WartelisteEintrag.annahme_datum.asc()
        ).first()
        
        aelteste_flasche = aeltester_eintrag.annahme_datum.isoformat() if aeltester_eintrag else None
        
        return jsonify({
            'success': True,
            'statistiken': {
                'in_warteliste': in_warteliste,
                'heute_angenommen': heute_angenommen,
                'wartende_kunden': wartende_kunden,
                'aelteste_flasche': aelteste_flasche
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/fuellbar')
def fuellbare_flaschen():
    """Flaschen laden die gefüllt werden können"""
    try:
        # Warteliste nach Priorität für Füll-Interface
        prioritaet_order = {'hoch': 1, 'normal': 2, 'niedrig': 3}
        
        eintraege = WartelisteEintrag.query.filter_by(status='wartend').join(
            Flasche
        ).join(
            Kunde
        ).add_columns(
            Flasche.flasche_nummer,
            Flasche.barcode,
            Kunde.vorname,
            Kunde.nachname
        ).order_by(
            WartelisteEintrag.annahme_datum.asc()
        ).all()
        
        fuellbare_flaschen = []
        for eintrag, flasche_nummer, barcode, vorname, nachname in eintraege:
            fuellbare_flaschen.append({
                'warteliste_id': eintrag.id,
                'flasche_id': eintrag.flasche_id,
                'flasche_nummer': flasche_nummer,
                'barcode': barcode,
                'kunde_name': f"{vorname} {nachname}",
                'gewuenschter_druck': eintrag.gewuenschter_druck,
                'besonderheiten': eintrag.besonderheiten,
                'prioritaet': eintrag.prioritaet,
                'annahme_datum': eintrag.annahme_datum.isoformat(),
                'wartezeit_tage': (date.today() - eintrag.annahme_datum).days
            })
        
        # Nach Priorität sortieren
        fuellbare_flaschen.sort(key=lambda x: (prioritaet_order.get(x['prioritaet'], 2), x['annahme_datum']))
        
        return jsonify({
            'success': True,
            'flaschen': fuellbare_flaschen,
            'count': len(fuellbare_flaschen)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/fuellen/<int:warteliste_id>', methods=['POST'])
def flasche_fuellen_starten(warteliste_id):
    """Flasche aus Warteliste zum Füllen markieren"""
    try:
        data = request.get_json()
        
        eintrag = WartelisteEintrag.query.get_or_404(warteliste_id)
        
        # Status ändern
        eintrag.status = 'wird_gefuellt'
        eintrag.fueller = data.get('fueller')
        eintrag.luftgemisch = data.get('luftgemisch', 'Luft')
        eintrag.fuell_start = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Flasche wird gefüllt'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/abschliessen/<int:warteliste_id>', methods=['POST'])
def flasche_fuellen_abschliessen(warteliste_id):
    """Flasche als gefüllt markieren und archivieren"""
    try:
        data = request.get_json()
        
        eintrag = WartelisteEintrag.query.get_or_404(warteliste_id)
        
        # Füll-Daten speichern
        eintrag.status = 'gefuellt'
        eintrag.erreichter_druck = data.get('erreichter_druck')
        eintrag.fuell_ende = datetime.utcnow()
        eintrag.notizen = data.get('notizen')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Flasche erfolgreich gefüllt und archiviert'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/export/excel')
def warteliste_excel_export():
    """Warteliste als Excel exportieren"""
    try:
        # Excel-Export temporär deaktiviert - openpyxl nicht installiert
        return jsonify({
            'success': False,
            'error': 'Excel-Export benötigt openpyxl: pip install openpyxl'
        }), 501
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
