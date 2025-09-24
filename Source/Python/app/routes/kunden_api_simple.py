# Erweiterte API für Kunden-Management - Vereinfacht
# Erstellt von Hans Hahn - Alle Rechte vorbehalten
# Datum: 04.07.2025

from flask import Blueprint, request, jsonify
from app import db
from app.models.kunden import Kunde
from app.models.flaschen import Flasche
from datetime import datetime
from sqlalchemy import or_
import re

# Blueprint
kunden_api_simple = Blueprint('kunden_api_simple', __name__)

@kunden_api_simple.route('/api/kunden/schnellsuche', methods=['GET'])
def schnelle_kundensuche():
    """
    Vereinfachte Kundensuche für Flaschen-Annahme
    
    Query Parameters:
        q: Suchbegriff (Name, Telefon, Nummer)
    """
    try:
        suchbegriff = request.args.get('q', '').strip()
        
        if len(suchbegriff) < 1:
            return jsonify({
                'success': True,
                'kunden': []
            })
        
        # Suche in verschiedenen Feldern
        suchbegriff_like = f"%{suchbegriff}%"
        
        kunden = Kunde.query.filter(
            or_(
                Kunde.vorname.ilike(suchbegriff_like),
                Kunde.nachname.ilike(suchbegriff_like),
                Kunde.mitgliedsnummer.ilike(suchbegriff_like),
                Kunde.telefon.ilike(suchbegriff_like),
                Kunde.externe_kundennummer.ilike(suchbegriff_like),
                # Kombinierte Suche für Vor- und Nachname
                (Kunde.vorname + ' ' + Kunde.nachname).ilike(suchbegriff_like)
            )
        ).filter_by(ist_aktiv=True).limit(5).all()
        
        # Formatiere Ergebnisse
        kunden_liste = []
        for kunde in kunden:
            kunde_data = {
                'id': kunde.id,
                'vorname': kunde.vorname,
                'nachname': kunde.nachname or '',
                'vollname': kunde.vollname,
                'mitgliedsnummer': kunde.mitgliedsnummer,
                'telefon': kunde.telefon,
                'externe_kundennummer': kunde.externe_kundennummer,
                'anzahl_flaschen': kunde.anzahl_flaschen
            }
            kunden_liste.append(kunde_data)
        
        return jsonify({
            'success': True,
            'kunden': kunden_liste
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler bei der Suche: {str(e)}'
        }), 500

@kunden_api_simple.route('/api/kunden/schnell-anlegen', methods=['POST'])
def schnell_kunde_anlegen():
    """
    Legt schnell einen neuen Kunden an mit minimalen Daten
    """
    try:
        data = request.get_json()
        
        vorname = data.get('vorname', '').strip()
        nachname = data.get('nachname', '').strip()
        
        if not vorname:
            return jsonify({
                'success': False,
                'error': 'Vorname ist erforderlich'
            }), 400
        
        # Prüfe ob Kunde bereits existiert
        if nachname:
            existierend = Kunde.query.filter_by(
                vorname=vorname,
                nachname=nachname
            ).first()
            
            if existierend:
                return jsonify({
                    'success': False,
                    'error': 'Kunde existiert bereits',
                    'kunde': existierend.to_dict()
                }), 409
        
        # Erstelle neuen Kunden
        neuer_kunde = Kunde(
            vorname=vorname,
            nachname=nachname,
            mitgliedsnummer=Kunde.get_naechste_mitgliedsnummer(),
            telefon=data.get('telefon'),
            externe_kundennummer=data.get('externe_nummer'),
            mitglied_seit=datetime.utcnow().date()
        )
        
        db.session.add(neuer_kunde)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'kunde': neuer_kunde.to_dict(),
            'message': f'Kunde {neuer_kunde.vollname} angelegt'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Fehler beim Anlegen: {str(e)}'
        }), 500

@kunden_api_simple.route('/api/kunden/<int:kunde_id>/letzte-flaschen', methods=['GET'])
def hole_letzte_flaschen(kunde_id):
    """
    Holt die letzten Flaschen eines Kunden für Quick-Select
    """
    try:
        kunde = Kunde.query.get(kunde_id)
        if not kunde:
            return jsonify({
                'success': False,
                'error': 'Kunde nicht gefunden'
            }), 404
        
        # Hole aktive Flaschen
        flaschen = kunde.flaschen.filter_by(ist_aktiv=True).limit(5).all()
        
        flaschen_liste = []
        for flasche in flaschen:
            flaschen_liste.append({
                'id': flasche.id,
                'flasche_nummer': flasche.flasche_nummer,
                'externe_nummer': flasche.externe_flasche_nummer,
                'groesse': flasche.groesse_liter,
                'typ': flasche.flaschen_typ,
                'pruefung_status': flasche.pruefung_status_text
            })
        
        return jsonify({
            'success': True,
            'flaschen': flaschen_liste
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler: {str(e)}'
        }), 500
