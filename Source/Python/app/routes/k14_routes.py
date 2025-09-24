# K14 Dokumentation Routes
from flask import Blueprint, render_template, send_file, jsonify, request, abort
from flask_login import login_required
import os
from datetime import datetime
from app import db
from app.models.wartungsintervall import Wartungsintervall
from app.models.kompressor import KompressorBetrieb

bp = Blueprint('k14', __name__, url_prefix='/k14')

# Pfad zu K14 Dokumenten
K14_DOCS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'K14 Unterlagen'))

@bp.route('/dokumentation')
@login_required
def dokumentation():
    """K14 Dokumentation Hauptseite"""
    return render_template('k14/dokumentation.html')

@bp.route('/api/dokumente')
@login_required
def api_dokumente_liste():
    """API: Liste aller K14 Dokumente"""
    try:
        dokumente = []
        
        if os.path.exists(K14_DOCS_PATH):
            for datei in os.listdir(K14_DOCS_PATH):
                if datei.endswith('.pdf'):
                    dateipfad = os.path.join(K14_DOCS_PATH, datei)
                    dateiinfo = os.stat(dateipfad)
                    
                    # Kategorisierung basierend auf Dateinamen
                    if 'Bedienungsantl' in datei or 'betreiberhandbuch' in datei or 'B140D' in datei:
                        kategorie = 'bedienung'
                    elif 'Schaltplan' in datei:
                        kategorie = 'technisch'
                    else:
                        kategorie = 'sonstiges'
                    
                    dokumente.append({
                        'dateiname': datei,
                        'groesse': f"{dateiinfo.st_size / 1024 / 1024:.1f} MB",
                        'kategorie': kategorie,
                        'geaendert': datetime.fromtimestamp(dateiinfo.st_mtime).isoformat()
                    })
        
        return jsonify({
            'success': True,
            'dokumente': dokumente
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/dokument/<path:dateiname>')
@login_required
def dokument_anzeigen(dateiname):
    """PDF-Dokument anzeigen"""
    try:
        # Sicherheitsprüfung
        if '..' in dateiname or dateiname.startswith('/'):
            abort(403)
        
        dateipfad = os.path.join(K14_DOCS_PATH, dateiname)
        
        if not os.path.exists(dateipfad):
            abort(404)
        
        # Zugriff protokollieren
        print(f"K14 Dokument aufgerufen: {dateiname} von Benutzer {request.remote_addr}")
        
        return send_file(dateipfad, mimetype='application/pdf')
        
    except Exception as e:
        print(f"Fehler beim Anzeigen des Dokuments: {str(e)}")
        abort(500)

@bp.route('/wartungsintervalle')
@login_required
def wartungsintervalle():
    """Wartungsintervalle Übersicht"""
    return render_template('k14/wartungsintervalle.html')

@bp.route('/patronenwechsel-anleitung')
@login_required
def patronenwechsel_anleitung():
    """Patronenwechsel Schritt-für-Schritt Anleitung"""
    return render_template('k14/patronenwechsel_anleitung.html')

@bp.route('/api/wartungsstatus')
@login_required
def api_wartungsstatus():
    """API: Aktueller Wartungsstatus"""
    try:
        # Wartungsintervall Status
        wartung_stats = Wartungsintervall.get_wartungsstatistiken()
        
        # Gesamt-Betriebszeit
        gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
        
        # Letzte Wartungen
        letzte_wartungen = Wartungsintervall.query.filter_by(
            name='Patronenwechsel'
        ).order_by(Wartungsintervall.start_datum.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'gesamt_betriebszeit': gesamt_stunden,
            'wartungsintervall': wartung_stats,
            'letzte_wartungen': [w.to_dict() for w in letzte_wartungen]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
