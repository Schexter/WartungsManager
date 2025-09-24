# Kunden-Import API Routes
from datetime import datetime
from flask import Blueprint, jsonify, request, make_response
from werkzeug.utils import secure_filename
import csv
import io
from app.models.kunden import Kunde
from app import db

bp = Blueprint('kunden_import_api', __name__, url_prefix='/api/kunden')

# Erlaubte Dateiformate
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/import/template')
def download_import_template():
    """Download CSV-Template für Kunden-Import"""
    try:
        # Template-Daten erstellen
        template_rows = [
            ['vorname', 'nachname', 'telefon', 'email', 'adresse', 'externe_kundennummer', 'externe_system', 'mitgliedschaft_typ', 'notizen'],
            ['Max', 'Mustermann', '+49 123 456789', 'max@beispiel.de', 'Musterstraße 1, 12345 Musterstadt', 'V001', 'Vereinsverwaltung', 'Standard', 'Beispiel-Kunde für Import'],
            ['Maria', 'Musterfrau', '+49 987 654321', 'maria@beispiel.de', '', 'V002', 'Vereinsverwaltung', 'Premium', 'Test-Kundin'],
            ['Hans', 'Schmidt', '', '', 'Beispielweg 5, 54321 Testdorf', '', '', 'Standard', '']
        ]
        
        # CSV-String erstellen
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
        
        for row in template_rows:
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        # Response mit CSV-Download
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=kunden_import_template.csv'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/import/info')
def import_info():
    """Informationen zum Import-Format"""
    return jsonify({
        'success': True,
        'import_info': {
            'supported_formats': ['CSV'],
            'max_file_size': '5 MB',
            'encoding': 'UTF-8 (empfohlen)',
            'csv_separator': '; (Semikolon)',
            'required_columns': ['vorname'],
            'optional_columns': [
                'nachname',
                'telefon', 
                'email',
                'adresse',
                'externe_kundennummer',
                'externe_system',
                'mitgliedschaft_typ',
                'notizen'
            ],
            'column_descriptions': {
                'vorname': 'PFLICHT - Vorname des Kunden',
                'nachname': 'Optional - Nachname des Kunden', 
                'telefon': 'Optional - Telefonnummer (Format: +49 123 456789)',
                'email': 'Optional - E-Mail-Adresse',
                'adresse': 'Optional - Vollständige Adresse',
                'externe_kundennummer': 'Optional - ID aus anderen Systemen (z.B. Vereinsnummer)',
                'externe_system': 'Optional - Name des externen Systems',
                'mitgliedschaft_typ': 'Optional - Standard, Premium, etc.',
                'notizen': 'Optional - Zusätzliche Informationen'
            },
            'examples': {
                'vorname': 'Max',
                'nachname': 'Mustermann',
                'telefon': '+49 123 456789',
                'email': 'max@beispiel.de',
                'adresse': 'Musterstraße 1, 12345 Musterstadt',
                'externe_kundennummer': 'V001',
                'externe_system': 'Vereinsverwaltung',
                'mitgliedschaft_typ': 'Standard',
                'notizen': 'Wichtiger Kunde'
            }
        }
    })

@bp.route('/import/preview', methods=['POST'])
def import_preview():
    """Vorschau der Import-Datei vor dem eigentlichen Import"""
    try:
        # Datei-Upload prüfen
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Keine Datei hochgeladen'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Keine Datei ausgewählt'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Ungültiges Dateiformat. Nur CSV-Dateien sind erlaubt.'
            }), 400
        
        # CSV einlesen
        try:
            content = file.read().decode('utf-8-sig', errors='ignore')
        except:
            return jsonify({
                'success': False,
                'error': 'Fehler beim Lesen der Datei. Stellen Sie sicher, dass die Datei UTF-8 kodiert ist.'
            }), 400
        
        # CSV parsen mit verschiedenen Separatoren
        separators = [';', ',', '\t']
        csv_data = None
        used_separator = None
        
        for sep in separators:
            try:
                reader = csv.DictReader(io.StringIO(content), delimiter=sep)
                rows = list(reader)
                if len(reader.fieldnames) > 1 and len(rows) > 0:  # Erfolgreich geparst
                    csv_data = rows
                    used_separator = sep
                    headers = reader.fieldnames
                    break
            except:
                continue
        
        if csv_data is None:
            return jsonify({
                'success': False,
                'error': 'CSV-Format nicht erkannt. Verwenden Sie Semikolon (;) als Trenner.'
            }), 400
        
        # Spalten-Mapping
        column_mapping = {
            'vorname': ['vorname', 'first_name', 'firstname', 'name'],
            'nachname': ['nachname', 'last_name', 'lastname', 'surname', 'familienname'],
            'telefon': ['telefon', 'phone', 'tel', 'telefonnummer', 'handy', 'mobile'],
            'email': ['email', 'e-mail', 'mail', 'e_mail'],
            'adresse': ['adresse', 'address', 'anschrift', 'strasse', 'wohnort'],
            'externe_kundennummer': ['externe_kundennummer', 'kundennummer', 'nummer', 'id', 'vereinsnummer'],
            'externe_system': ['externe_system', 'system', 'herkunft', 'quelle'],
            'mitgliedschaft_typ': ['mitgliedschaft_typ', 'typ', 'type', 'kategorie'],
            'notizen': ['notizen', 'notes', 'bemerkungen', 'kommentare']
        }
        
        # Automatisches Spalten-Mapping
        mapped_columns = {}
        available_columns = [col.lower().strip() for col in headers]
        
        for target_col, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name.lower() in available_columns:
                    original_col = headers[available_columns.index(possible_name.lower())]
                    mapped_columns[target_col] = original_col
                    break
        
        # Validierung
        errors = []
        warnings = []
        
        if 'vorname' not in mapped_columns:
            errors.append('Spalte "vorname" nicht gefunden. Diese ist erforderlich.')
        
        # Preview-Daten erstellen (erste 10 Zeilen)
        preview_data = []
        preview_rows = min(10, len(csv_data))
        
        for i in range(preview_rows):
            row_data = {}
            for target_col, source_col in mapped_columns.items():
                value = csv_data[i].get(source_col, '') or ''
                row_data[target_col] = str(value).strip()
            preview_data.append(row_data)
        
        # Statistiken
        stats = {
            'total_rows': len(csv_data),
            'preview_rows': preview_rows,
            'mapped_columns': len(mapped_columns),
            'available_columns': headers,
            'missing_required': ['vorname'] if 'vorname' not in mapped_columns else [],
            'estimated_new_customers': len(csv_data)  # TODO: Echte Duplikat-Prüfung
        }
        
        return jsonify({
            'success': True,
            'preview': {
                'data': preview_data,
                'column_mapping': mapped_columns,
                'stats': stats,
                'errors': errors,
                'warnings': warnings,
                'can_import': len(errors) == 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Verarbeiten der Datei: {str(e)}'
        }), 500

@bp.route('/import/execute', methods=['POST'])
def execute_import():
    """Führt den eigentlichen Import durch"""
    try:
        # Datei-Upload prüfen
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Keine Datei hochgeladen'
            }), 400
        
        file = request.files['file']
        options = request.form.get('options', '{}')
        
        # Import-Optionen
        import json
        try:
            import_options = json.loads(options)
        except:
            import_options = {}
        
        skip_duplicates = import_options.get('skip_duplicates', True)
        update_existing = import_options.get('update_existing', False)
        
        # CSV verarbeiten (gleicher Code wie Preview)
        content = file.read().decode('utf-8-sig', errors='ignore')
        
        separators = [';', ',', '\t']
        csv_data = None
        
        for sep in separators:
            try:
                reader = csv.DictReader(io.StringIO(content), delimiter=sep)
                rows = list(reader)
                if len(reader.fieldnames) > 1 and len(rows) > 0:
                    csv_data = rows
                    headers = reader.fieldnames
                    break
            except:
                continue
        
        if csv_data is None:
            return jsonify({
                'success': False,
                'error': 'CSV-Format nicht erkannt'
            }), 400
        
        # Spalten-Mapping (gleicher Code)
        column_mapping = {
            'vorname': ['vorname', 'first_name', 'firstname', 'name'],
            'nachname': ['nachname', 'last_name', 'lastname', 'surname'],
            'telefon': ['telefon', 'phone', 'tel', 'telefonnummer'],
            'email': ['email', 'e-mail', 'mail'],
            'adresse': ['adresse', 'address', 'anschrift'],
            'externe_kundennummer': ['externe_kundennummer', 'kundennummer', 'nummer'],
            'externe_system': ['externe_system', 'system', 'herkunft'],
            'mitgliedschaft_typ': ['mitgliedschaft_typ', 'typ', 'type'],
            'notizen': ['notizen', 'notes', 'bemerkungen']
        }
        
        mapped_columns = {}
        available_columns = [col.lower().strip() for col in headers]
        
        for target_col, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name.lower() in available_columns:
                    original_col = headers[available_columns.index(possible_name.lower())]
                    mapped_columns[target_col] = original_col
                    break
        
        # Import durchführen
        imported_count = 0
        skipped_count = 0
        error_count = 0
        errors = []
        
        for i, row in enumerate(csv_data):
            try:
                # Daten extrahieren
                kunde_data = {}
                for target_col, source_col in mapped_columns.items():
                    value = row.get(source_col, '') or ''
                    kunde_data[target_col] = str(value).strip()
                
                # Pflichtfeld prüfen
                if not kunde_data.get('vorname'):
                    error_count += 1
                    errors.append(f'Zeile {i+2}: Vorname fehlt')
                    continue
                
                # Duplikat-Prüfung
                existing_kunde = None
                if kunde_data.get('externe_kundennummer'):
                    existing_kunde = Kunde.query.filter_by(
                        externe_kundennummer=kunde_data['externe_kundennummer']
                    ).first()
                
                if not existing_kunde and kunde_data.get('email'):
                    existing_kunde = Kunde.query.filter_by(
                        email=kunde_data['email']
                    ).first()
                
                if existing_kunde:
                    if skip_duplicates:
                        skipped_count += 1
                        continue
                    elif update_existing:
                        # Update existing customer
                        for field, value in kunde_data.items():
                            if value and field != 'vorname':  # Vorname nicht überschreiben
                                setattr(existing_kunde, field, value)
                        existing_kunde.updated_at = datetime.utcnow()
                        imported_count += 1
                    else:
                        skipped_count += 1
                        continue
                else:
                    # Neuen Kunden erstellen
                    neuer_kunde = Kunde(
                        mitgliedsnummer=Kunde.get_naechste_mitgliedsnummer(),
                        vorname=kunde_data['vorname'],
                        nachname=kunde_data.get('nachname') or None,
                        telefon=kunde_data.get('telefon') or None,
                        email=kunde_data.get('email') or None,
                        adresse=kunde_data.get('adresse') or None,
                        externe_kundennummer=kunde_data.get('externe_kundennummer') or None,
                        externe_system=kunde_data.get('externe_system') or 'Import',
                        mitgliedschaft_typ=kunde_data.get('mitgliedschaft_typ') or 'Standard',
                        notizen=kunde_data.get('notizen') or None,
                        erstellt_am=datetime.utcnow()
                    )
                    
                    db.session.add(neuer_kunde)
                    imported_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f'Zeile {i+2}: {str(e)}')
        
        # Transaktion abschließen
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Fehler beim Speichern: {str(e)}'
            }), 500
        
        return jsonify({
            'success': True,
            'result': {
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'error_count': error_count,
                'total_processed': len(csv_data),
                'errors': errors[:10]  # Nur erste 10 Fehler anzeigen
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
