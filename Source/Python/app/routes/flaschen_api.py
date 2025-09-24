# Flaschen-Annahme API Routes
from datetime import datetime, date
from flask import Blueprint, jsonify, request
from app.models.flaschen import Flasche
from app.models.kunden import Kunde
from app.models.warteliste import WartelisteEintrag
from app import db

bp = Blueprint('flaschen_api', __name__, url_prefix='/api/flaschen')

@bp.route('/barcode/<barcode>')
def flasche_by_barcode(barcode):
    """Flasche nach Barcode suchen"""
    try:
        flasche = Flasche.query.filter_by(barcode=barcode).first()
        
        if flasche:
            return jsonify({
                'found': True,
                'flasche': {
                    'id': flasche.id,
                    'barcode': flasche.barcode,
                    'flasche_nummer': flasche.flasche_nummer,
                    'kunde_id': flasche.kunde_id,
                    'kunde_name': f"{flasche.kunde.vorname} {flasche.kunde.nachname}" if flasche.kunde else None
                }
            })
        else:
            return jsonify({
                'found': False,
                'message': 'Flasche nicht gefunden'
            })
            
    except Exception as e:
        return jsonify({
            'found': False,
            'error': str(e)
        }), 500

@bp.route('/erstellen', methods=['POST'])
def flasche_erstellen():
    """Neue Flasche erstellen"""
    try:
        data = request.get_json()
        
        print(f"Flaschen-Erstellung: {data}")  # Debug
        
        # Validierung der erforderlichen Felder
        if not data.get('kunde_id'):
            return jsonify({
                'success': False,
                'error': 'Kunde-ID ist erforderlich'
            }), 400
        
        # Prüfe ob Kunde existiert
        kunde = Kunde.query.get(data['kunde_id'])
        if not kunde:
            return jsonify({
                'success': False,
                'error': 'Kunde nicht gefunden'
            }), 404
        
        # Generiere automatische interne Flaschennummer
        flasche_nummer = Flasche.generiere_interne_flaschennummer(kunde)
        
        # Prüfe ob Flasche mit Barcode bereits existiert (falls Barcode vorhanden)
        barcode = data.get('barcode')
        if barcode:
            existing = Flasche.query.filter_by(barcode=barcode).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': f'Flasche mit Barcode {barcode} existiert bereits'
                }), 400
        
        # Neue Flasche erstellen mit erweiterten Feldern
        neue_flasche = Flasche(
            kunde_id=data['kunde_id'],
            flasche_nummer=flasche_nummer,
            externe_flasche_nummer=data.get('externe_flasche_nummer'),
            barcode=barcode,
            bauart_zulassung=data.get('bauart_zulassung'),
            seriennummer=data.get('seriennummer'),
            groesse_liter=data.get('groesse_liter', 11.0),
            flaschen_typ=data.get('flaschen_typ', 'Standard'),
            max_druck_bar=data.get('max_druck_bar', 300),
            erstellt_am=datetime.utcnow()
        )
        
        # Erweiterte Felder aus dem neuen Formular
        if hasattr(neue_flasche, 'hersteller'):
            neue_flasche.hersteller = data.get('hersteller')
        if hasattr(neue_flasche, 'ventil_typ'):
            neue_flasche.ventil_typ = data.get('ventiltyp', 'Mono')  # Feld heißt ventil_typ im Model
        if hasattr(neue_flasche, 'material'):
            neue_flasche.material = data.get('flaschen_typ', 'Stahl')  # Wir nutzen flaschen_typ für Material
        if hasattr(neue_flasche, 'farbe'):
            neue_flasche.farbe = data.get('farbe')
        if hasattr(neue_flasche, 'gewicht_leer'):
            neue_flasche.gewicht_leer = data.get('gewicht_leer')
        if hasattr(neue_flasche, 'sichtkontrolle_ok'):
            neue_flasche.sichtkontrolle_ok = data.get('sichtkontrolle_ok', True)
        if hasattr(neue_flasche, 'o2_clean'):
            neue_flasche.o2_clean = data.get('o2_clean', False)
        if hasattr(neue_flasche, 'letzte_inspektion') and data.get('letzte_inspektion'):
            try:
                neue_flasche.letzte_inspektion = datetime.strptime(data['letzte_inspektion'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Notizen
        if data.get('notizen'):
            neue_flasche.notizen = data['notizen']
        
        # Status setzen
        if hasattr(neue_flasche, 'status'):
            neue_flasche.status = 'angenommen'  # Neu angenommene Flasche
        
        # Erweiterte Felder für Rückverfolgbarkeit
        if hasattr(neue_flasche, 'interne_flaschennummer_auto'):
            neue_flasche.interne_flaschennummer_auto = True  # Auto-generiert
        if hasattr(neue_flasche, 'barcode_typ'):
            neue_flasche.barcode_typ = data.get('barcode_typ', 'CODE128')
        if hasattr(neue_flasche, 'flaschen_gewicht_kg'):
            neue_flasche.flaschen_gewicht_kg = data.get('flaschen_gewicht_kg')
        if hasattr(neue_flasche, 'ventil_typ'):
            neue_flasche.ventil_typ = data.get('ventil_typ')
        if hasattr(neue_flasche, 'ursprungsland'):
            neue_flasche.ursprungsland = data.get('ursprungsland')
        if hasattr(neue_flasche, 'kaufdatum') and data.get('kaufdatum'):
            try:
                neue_flasche.kaufdatum = datetime.strptime(data['kaufdatum'], '%Y-%m-%d').date()
            except ValueError:
                pass
        if hasattr(neue_flasche, 'garantie_bis') and data.get('garantie_bis'):
            try:
                neue_flasche.garantie_bis = datetime.strptime(data['garantie_bis'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Datum-Felder setzen (falls vorhanden)
        if data.get('herstellungs_datum'):
            try:
                neue_flasche.herstellungs_datum = datetime.strptime(data['herstellungs_datum'], '%Y-%m-%d').date()
            except ValueError:
                pass
                
        if data.get('pruef_datum'):
            try:
                neue_flasche.pruef_datum = datetime.strptime(data['pruef_datum'], '%Y-%m-%d').date()
            except ValueError:
                pass
                
        if data.get('naechste_pruefung'):
            try:
                neue_flasche.naechste_pruefung = datetime.strptime(data['naechste_pruefung'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        db.session.add(neue_flasche)
        db.session.commit()
        
        print(f"Flasche erfolgreich erstellt: {neue_flasche.id}")
        
        return jsonify({
            'success': True,
            'flasche': {
                'id': neue_flasche.id,
                'flasche_nummer': neue_flasche.flasche_nummer,
                'barcode': neue_flasche.barcode,
                'externe_flasche_nummer': neue_flasche.externe_flasche_nummer,
                'bauart_zulassung': neue_flasche.bauart_zulassung,
                'seriennummer': neue_flasche.seriennummer,
                'kunde_id': neue_flasche.kunde_id,
                'kunde_name': f"{kunde.vorname} {kunde.nachname}",
                'vollstaendige_identifikation': neue_flasche.vollstaendige_identifikation,
                'ist_fuellbereit': neue_flasche.ist_fuellbereit,
                'pruefung_status': neue_flasche.pruefung_status_text
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Fehler beim Erstellen der Flasche: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/ventiltypen')
def ventiltypen_liste():
    """Liste aller verwendeten Ventiltypen"""
    try:
        # Alle eindeutigen Ventiltypen aus der Datenbank holen
        ventiltypen = db.session.query(Flasche.ventil_typ).filter(
            Flasche.ventil_typ.isnot(None),
            Flasche.ventil_typ != ''
        ).distinct().all()
        
        # Zu Liste konvertieren
        typen_liste = [typ[0] for typ in ventiltypen if typ[0]]
        
        # Sortieren
        typen_liste.sort()
        
        return jsonify({
            'success': True,
            'ventiltypen': typen_liste
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/ventiltyp/neu', methods=['POST'])
def ventiltyp_hinzufuegen():
    """Neuen Ventiltyp zur Liste hinzufügen"""
    try:
        data = request.get_json()
        ventiltyp = data.get('ventiltyp')
        
        if not ventiltyp:
            return jsonify({
                'success': False,
                'error': 'Ventiltyp ist erforderlich'
            }), 400
        
        # Hier könnten wir den Ventiltyp in einer separaten Tabelle speichern
        # Für jetzt wird er automatisch zur Liste hinzugefügt, wenn eine Flasche damit erstellt wird
        
        return jsonify({
            'success': True,
            'message': f'Ventiltyp "{ventiltyp}" kann jetzt verwendet werden'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:flasche_id>', methods=['PUT'])
def flasche_aktualisieren(flasche_id):
    """Flasche aktualisieren"""
    try:
        flasche = Flasche.query.get_or_404(flasche_id)
        data = request.get_json()
        
        # Aktualisierbare Felder
        if 'flasche_nummer' in data:
            flasche.flasche_nummer = data['flasche_nummer']
        if 'barcode' in data:
            flasche.barcode = data['barcode']
        if 'groesse_liter' in data:
            flasche.groesse_liter = data['groesse_liter']
        if 'flaschen_typ' in data:
            flasche.flaschen_typ = data['flaschen_typ']
        if 'max_druck_bar' in data:
            flasche.max_druck_bar = data['max_druck_bar']
        if 'ist_aktiv' in data:
            flasche.ist_aktiv = data['ist_aktiv']
        if 'notizen' in data:
            flasche.notizen = data['notizen']
        if 'pruef_datum' in data:
            if data['pruef_datum']:
                flasche.pruef_datum = datetime.strptime(data['pruef_datum'], '%Y-%m-%d').date()
            else:
                flasche.pruef_datum = None
        if 'naechste_pruefung' in data:
            if data['naechste_pruefung']:
                flasche.naechste_pruefung = datetime.strptime(data['naechste_pruefung'], '%Y-%m-%d').date()
            else:
                flasche.naechste_pruefung = None
        
        flasche.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Flasche erfolgreich aktualisiert'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
