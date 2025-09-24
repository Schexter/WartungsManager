# Kunden-Management API Routes
from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from app.models.kunden import Kunde
from app.models.flaschen import Flasche
from app import db

bp = Blueprint('kunden_api', __name__, url_prefix='/api/kunden')

@bp.route('/suchen')
def kunden_suchen():
    """Kunden nach Name, Telefon, E-Mail oder externe Kundennummer suchen"""
    try:
        suchbegriff = request.args.get('q', '').strip()
        
        print(f"Kunden-Suche: '{suchbegriff}'")  # Debug
        
        if len(suchbegriff) < 1:  # Reduziert von 2 auf 1
            return jsonify({
                'kunden': [],
                'message': 'Suchbegriff zu kurz'
            })
        
        # Erweiterte Suche mit externen Kundennummern
        search_pattern = f'%{suchbegriff}%'
        
        kunden = Kunde.query.filter(
            or_(
                Kunde.vorname.ilike(search_pattern),
                Kunde.nachname.ilike(search_pattern),
                Kunde.telefon.ilike(search_pattern),
                Kunde.email.ilike(search_pattern),
                Kunde.mitgliedsnummer.ilike(search_pattern),
                Kunde.externe_kundennummer.ilike(search_pattern),
                # Kombinierte Suche für "Vorname Nachname" (SQLite-Syntax)
                (Kunde.vorname + ' ' + Kunde.nachname).ilike(search_pattern)
            )
        ).limit(10).all()
        
        print(f"Gefundene Kunden: {len(kunden)}")  # Debug
        
        kunden_liste = []
        for kunde in kunden:
            kunde_data = {
                'id': kunde.id,
                'vorname': kunde.vorname,
                'nachname': kunde.nachname or '',  # Null-Handling
                'mitgliedsnummer': kunde.mitgliedsnummer,
                'externe_kundennummer': kunde.externe_kundennummer,
                'externe_system': kunde.externe_system,
                'telefon': kunde.telefon,
                'email': kunde.email,
                'adresse': kunde.adresse
            }
            kunden_liste.append(kunde_data)
            print(f"  - {kunde.vorname} {kunde.nachname or ''}")  # Debug
        
        return jsonify({
            'kunden': kunden_liste,
            'count': len(kunden_liste)
        })
        
    except Exception as e:
        print(f"Fehler bei Kunden-Suche: {str(e)}")
        return jsonify({
            'kunden': [],
            'error': str(e)
        }), 500

@bp.route('/erstellen', methods=['POST'])
def kunde_erstellen():
    """Neuen Kunden erstellen"""
    try:
        data = request.get_json()
        
        # Validierung - nur Vorname ist Pflicht
        if not data.get('vorname'):
            return jsonify({
                'success': False,
                'error': 'Vorname ist erforderlich'
            }), 400
        
        vorname = data['vorname'].strip()
        nachname = data.get('nachname', '').strip() or None  # Leere Strings zu None
        
        # Prüfe ob Kunde bereits existiert
        existing = None
        
        # Prüfe externe Kundennummer falls vorhanden
        if data.get('externe_kundennummer'):
            existing = Kunde.query.filter_by(
                externe_kundennummer=data['externe_kundennummer']
            ).first()
        
        # Prüfe Name + Telefon/E-Mail (nur wenn Nachname vorhanden)
        if not existing and nachname and data.get('telefon'):
            existing = Kunde.query.filter_by(
                vorname=vorname,
                nachname=nachname,
                telefon=data['telefon']
            ).first()
        elif not existing and nachname and data.get('email'):
            existing = Kunde.query.filter_by(
                vorname=vorname,
                nachname=nachname,
                email=data['email']
            ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'Kunde mit diesen Daten existiert bereits',
                'existing_kunde': {
                    'id': existing.id,
                    'vorname': existing.vorname,
                    'nachname': existing.nachname,
                    'externe_kundennummer': existing.externe_kundennummer
                }
            }), 409
        
        # Neuen Kunden erstellen
        neuer_kunde = Kunde(
            mitgliedsnummer=Kunde.get_naechste_mitgliedsnummer(),
            vorname=vorname,
            nachname=nachname,  # Kann None sein
            telefon=data.get('telefon'),
            email=data.get('email'),
            adresse=data.get('adresse'),
            externe_kundennummer=data.get('externe_kundennummer'),
            externe_system=data.get('externe_system'),
            erstellt_am=datetime.utcnow()
        )
        
        db.session.add(neuer_kunde)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'kunde': {
                'id': neuer_kunde.id,
                'vorname': neuer_kunde.vorname,
                'nachname': neuer_kunde.nachname,
                'mitgliedsnummer': neuer_kunde.mitgliedsnummer,
                'externe_kundennummer': neuer_kunde.externe_kundennummer,
                'telefon': neuer_kunde.telefon,
                'email': neuer_kunde.email
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:kunde_id>')
def kunde_details(kunde_id):
    """Kunde-Details abrufen"""
    try:
        kunde = Kunde.query.get(kunde_id)
        
        if not kunde:
            return jsonify({
                'success': False,
                'error': 'Kunde nicht gefunden'
            }), 404
        
        return jsonify({
            'success': True,
            'kunde': {
                'id': kunde.id,
                'vorname': kunde.vorname,
                'nachname': kunde.nachname,
                'mitgliedsnummer': kunde.mitgliedsnummer,
                'externe_kundennummer': kunde.externe_kundennummer,
                'externe_system': kunde.externe_system,
                'telefon': kunde.telefon,
                'email': kunde.email,
                'adresse': kunde.adresse,
                'firma': kunde.firma,
                'mitglied_seit': kunde.mitglied_seit.isoformat() if kunde.mitglied_seit else None,
                'mitgliedschaft_typ': kunde.mitgliedschaft_typ,
                'ist_aktiv': kunde.ist_aktiv,
                'notizen': kunde.notizen,
                'erstellt_am': kunde.erstellt_am.isoformat() if kunde.erstellt_am else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@bp.route('/<int:kunde_id>/flaschen')
def kunde_flaschen(kunde_id):
    """Alle Flaschen eines Kunden abrufen"""
    try:
        kunde = Kunde.query.get_or_404(kunde_id)
        
        flaschen_liste = []
        for flasche in kunde.flaschen:
            flasche_data = {
                'id': flasche.id,
                'flasche_nummer': flasche.flasche_nummer,
                'externe_flasche_nummer': getattr(flasche, 'externe_flasche_nummer', None),
                'barcode': flasche.barcode,
                'seriennummer': getattr(flasche, 'seriennummer', None),
                'bauart_zulassung': getattr(flasche, 'bauart_zulassung', None),
                'herstellungs_datum': getattr(flasche, 'herstellungs_datum', None),
                'groesse_liter': flasche.groesse_liter,
                'flaschen_typ': flasche.flaschen_typ,
                'max_druck_bar': flasche.max_druck_bar,
                'pruef_datum': flasche.pruef_datum.isoformat() if flasche.pruef_datum else None,
                'naechste_pruefung': flasche.naechste_pruefung.isoformat() if flasche.naechste_pruefung else None,
                'pruefung_faellig': flasche.pruefung_faellig,
                'status': getattr(flasche, 'status', 'unbekannt'),
                'ist_aktiv': flasche.ist_aktiv,
                'notizen': flasche.notizen,
                'erstellt_am': flasche.erstellt_am.isoformat() if flasche.erstellt_am else None
            }
            flaschen_liste.append(flasche_data)
        
        return jsonify({
            'success': True,
            'flaschen': flaschen_liste,
            'count': len(flaschen_liste)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:kunde_id>/fuellhistorie')
def kunde_fuellhistorie(kunde_id):
    """Füllhistorie eines Kunden abrufen"""
    try:
        from app.models.fuelling import Fuelling
        from datetime import datetime, timedelta
        
        kunde = Kunde.query.get_or_404(kunde_id)
        
        # Filter-Parameter
        filter_param = request.args.get('filter', 'alle')
        
        query = db.session.query(Fuelling).join(
            Flasche, Fuelling.flasche_id == Flasche.id
        ).filter(Flasche.kunde_id == kunde_id)
        
        # Datum-Filter anwenden
        if filter_param == '30':
            start_date = datetime.utcnow() - timedelta(days=30)
            query = query.filter(Fuelling.gefuellt_am >= start_date)
        elif filter_param == '90':
            start_date = datetime.utcnow() - timedelta(days=90)
            query = query.filter(Fuelling.gefuellt_am >= start_date)
        elif filter_param == 'jahr':
            start_date = datetime.utcnow() - timedelta(days=365)
            query = query.filter(Fuelling.gefuellt_am >= start_date)
        
        fuellungen = query.order_by(Fuelling.gefuellt_am.desc()).all()
        
        fuellhistorie = []
        for fuellung in fuellungen:
            fuellung_data = {
                'id': fuellung.id,
                'flasche_nummer': fuellung.flasche.flasche_nummer,
                'flasche_groesse': fuellung.flasche.groesse_liter,
                'start_druck': fuellung.start_druck,
                'end_druck': fuellung.end_druck,
                'gasgemisch': fuellung.gasgemisch,
                'gefuellt_am': fuellung.gefuellt_am.isoformat() if fuellung.gefuellt_am else None,
                'bearbeiter': fuellung.bearbeiter,
                'notizen': fuellung.notizen
            }
            fuellhistorie.append(fuellung_data)
        
        return jsonify({
            'success': True,
            'fuellhistorie': fuellhistorie,
            'count': len(fuellhistorie)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:kunde_id>/wartungen')
def kunde_wartungen(kunde_id):
    """Wartungen und anstehende Prüfungen eines Kunden"""
    try:
        from datetime import datetime, timedelta
        
        kunde = Kunde.query.get_or_404(kunde_id)
        
        # Anstehende Prüfungen (fällig oder in den nächsten 30 Tagen)
        heute = datetime.utcnow().date()
        pruefungsfrist = heute + timedelta(days=30)
        
        anstehende_pruefungen = []
        for flasche in kunde.flaschen:
            if (flasche.ist_aktiv and flasche.naechste_pruefung and 
                flasche.naechste_pruefung <= pruefungsfrist):
                
                tage_bis_pruefung = (flasche.naechste_pruefung - heute).days
                
                pruefung_data = {
                    'flasche_id': flasche.id,
                    'flasche_nummer': flasche.flasche_nummer,
                    'naechste_pruefung': flasche.naechste_pruefung.isoformat(),
                    'tage_ueberfaellig': -tage_bis_pruefung if tage_bis_pruefung < 0 else tage_bis_pruefung,
                    'ist_ueberfaellig': tage_bis_pruefung < 0
                }
                anstehende_pruefungen.append(pruefung_data)
        
        # Wartungshistorie (TODO: Wartungsmodell erstellen)
        wartungen = []  # Placeholder
        
        return jsonify({
            'success': True,
            'anstehende_pruefungen': anstehende_pruefungen,
            'wartungen': wartungen
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:kunde_id>/statistiken')
def kunde_statistiken(kunde_id):
    """Statistiken für einen Kunden"""
    try:
        from app.models.fuelling import Fuelling
        from datetime import datetime
        
        kunde = Kunde.query.get_or_404(kunde_id)
        
        # Flaschen-Statistiken
        total_flaschen = kunde.flaschen.count()
        aktive_flaschen = kunde.flaschen.filter_by(ist_aktiv=True).count()
        
        # Prüfungen fällig
        heute = datetime.utcnow().date()
        pruefungen_faellig = 0
        for flasche in kunde.flaschen:
            if (flasche.ist_aktiv and flasche.naechste_pruefung and 
                flasche.naechste_pruefung <= heute):
                pruefungen_faellig += 1
        
        # Füllungen-Statistiken
        flasche_ids = [f.id for f in kunde.flaschen]
        total_fuellungen = 0
        letzte_fuellung = None
        
        if flasche_ids:
            total_fuellungen = Fuelling.query.filter(
                Fuelling.flasche_id.in_(flasche_ids)
            ).count()
            
            letzte_fuellung_obj = Fuelling.query.filter(
                Fuelling.flasche_id.in_(flasche_ids)
            ).order_by(Fuelling.gefuellt_am.desc()).first()
            
            if letzte_fuellung_obj:
                letzte_fuellung = letzte_fuellung_obj.gefuellt_am.isoformat()
        
        return jsonify({
            'success': True,
            'statistiken': {
                'total_flaschen': total_flaschen,
                'aktive_flaschen': aktive_flaschen,
                'total_fuellungen': total_fuellungen,
                'letzte_fuellung': letzte_fuellung,
                'pruefungen_faellig': pruefungen_faellig
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:kunde_id>/export')
def kunde_export(kunde_id):
    """Kompletten Kundendatensatz als Excel exportieren"""
    try:
        from io import BytesIO
        import pandas as pd
        from flask import send_file
        
        kunde = Kunde.query.get_or_404(kunde_id)
        
        # Excel-Datei erstellen
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Kundendaten
            kunde_df = pd.DataFrame([{
                'Mitgliedsnummer': kunde.mitgliedsnummer,
                'Vorname': kunde.vorname,
                'Nachname': kunde.nachname or '',
                'Firma': kunde.firma or '',
                'Telefon': kunde.telefon or '',
                'E-Mail': kunde.email or '',
                'Adresse': kunde.adresse or '',
                'Externe Nummer': kunde.externe_kundennummer or '',
                'Externes System': kunde.externe_system or '',
                'Mitglied seit': kunde.mitglied_seit.strftime('%d.%m.%Y') if kunde.mitglied_seit else '',
                'Mitgliedschaftstyp': kunde.mitgliedschaft_typ or '',
                'Aktiv': 'Ja' if kunde.ist_aktiv else 'Nein',
                'Notizen': kunde.notizen or '',
                'Erstellt am': kunde.erstellt_am.strftime('%d.%m.%Y %H:%M') if kunde.erstellt_am else ''
            }])
            kunde_df.to_excel(writer, sheet_name='Kundendaten', index=False)
            
            # Flaschen
            if kunde.flaschen.count() > 0:
                flaschen_data = []
                for flasche in kunde.flaschen:
                    flaschen_data.append({
                        'Flaschennummer': flasche.flasche_nummer,
                        'Barcode': flasche.barcode or '',
                        'Größe (L)': flasche.groesse_liter,
                        'Typ': flasche.flaschen_typ or 'Standard',
                        'Max. Druck (bar)': flasche.max_druck_bar,
                        'Letztes Prüfdatum': flasche.pruef_datum.strftime('%d.%m.%Y') if flasche.pruef_datum else '',
                        'Nächste Prüfung': flasche.naechste_pruefung.strftime('%d.%m.%Y') if flasche.naechste_pruefung else '',
                        'Prüfung fällig': 'Ja' if flasche.pruefung_faellig else 'Nein',
                        'Aktiv': 'Ja' if flasche.ist_aktiv else 'Nein',
                        'Notizen': flasche.notizen or '',
                        'Erstellt am': flasche.erstellt_am.strftime('%d.%m.%Y') if flasche.erstellt_am else ''
                    })
                
                flaschen_df = pd.DataFrame(flaschen_data)
                flaschen_df.to_excel(writer, sheet_name='Flaschen', index=False)
        
        output.seek(0)
        
        filename = f"Kunde_{kunde.mitgliedsnummer}_{kunde.vorname}_{kunde.nachname or 'unbekannt'}.xlsx"
        filename = filename.replace(' ', '_').replace('/', '_')
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/alle')
def alle_kunden():
    """Alle Kunden abrufen"""
    try:
        kunden = Kunde.query.all()
        
        kunden_liste = []
        for kunde in kunden:
            # Flaschen-Statistiken
            anzahl_flaschen = kunde.flaschen.count()
            
            # Prüfungen fällig
            from datetime import datetime
            heute = datetime.utcnow().date()
            pruefungen_faellig = 0
            for flasche in kunde.flaschen:
                if (flasche.ist_aktiv and flasche.naechste_pruefung and 
                    flasche.naechste_pruefung <= heute):
                    pruefungen_faellig += 1
            
            kunde_data = {
                'id': kunde.id,
                'vorname': kunde.vorname,
                'nachname': kunde.nachname,
                'mitgliedsnummer': kunde.mitgliedsnummer,
                'externe_kundennummer': kunde.externe_kundennummer,
                'telefon': kunde.telefon,
                'email': kunde.email,
                'firma': kunde.firma,
                'ist_aktiv': kunde.ist_aktiv,
                'mitglied_seit': kunde.mitglied_seit.isoformat() if kunde.mitglied_seit else None,
                'erstellt_am': kunde.erstellt_am.isoformat() if kunde.erstellt_am else None,
                'anzahl_flaschen': anzahl_flaschen,
                'pruefungen_faellig': pruefungen_faellig
            }
            kunden_liste.append(kunde_data)
        
        return jsonify({
            'success': True,
            'kunden': kunden_liste,
            'count': len(kunden_liste)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/statistiken')
def alle_kunden_statistiken():
    """Gesamtstatistiken aller Kunden"""
    try:
        from datetime import datetime
        
        total_kunden = Kunde.query.count()
        aktive_kunden = Kunde.query.filter_by(ist_aktiv=True).count()
        
        # Kunden mit Flaschen
        kunden_mit_flaschen = db.session.query(Kunde.id).join(
            Flasche, Kunde.id == Flasche.kunde_id
        ).distinct().count()
        
        # Prüfungen fällig (über alle Kunden)
        heute = datetime.utcnow().date()
        pruefungen_faellig = db.session.query(Flasche).filter(
            Flasche.ist_aktiv == True,
            Flasche.naechste_pruefung <= heute,
            Flasche.naechste_pruefung.isnot(None)
        ).count()
        
        return jsonify({
            'success': True,
            'statistiken': {
                'total_kunden': total_kunden,
                'aktive_kunden': aktive_kunden,
                'kunden_mit_flaschen': kunden_mit_flaschen,
                'pruefungen_faellig': pruefungen_faellig
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/export/alle')
def export_alle_kunden():
    """Alle Kunden als Excel exportieren"""
    try:
        from io import BytesIO
        import pandas as pd
        from flask import send_file
        from datetime import datetime
        
        kunden = Kunde.query.all()
        
        # Excel-Datei erstellen
        output = BytesIO()
        
        kunden_data = []
        for kunde in kunden:
            kunden_data.append({
                'Mitgliedsnummer': kunde.mitgliedsnummer,
                'Vorname': kunde.vorname,
                'Nachname': kunde.nachname or '',
                'Firma': kunde.firma or '',
                'Telefon': kunde.telefon or '',
                'E-Mail': kunde.email or '',
                'Externe Nummer': kunde.externe_kundennummer or '',
                'Mitglied seit': kunde.mitglied_seit.strftime('%d.%m.%Y') if kunde.mitglied_seit else '',
                'Aktiv': 'Ja' if kunde.ist_aktiv else 'Nein',
                'Anzahl Flaschen': kunde.flaschen.count(),
                'Erstellt am': kunde.erstellt_am.strftime('%d.%m.%Y %H:%M') if kunde.erstellt_am else ''
            })
        
        df = pd.DataFrame(kunden_data)
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Alle Kunden', index=False)
        
        output.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"Alle_Kunden_{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
