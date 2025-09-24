# Füllvorgang Routes für WartungsManager
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from app import db
from app.models import Fuellvorgang

bp = Blueprint('fuelling', __name__)

@bp.route('/')
def index():
    """Füllvorgang Übersichtsseite"""
    aktiver_vorgang = Fuellvorgang.get_aktiver_fuellvorgang()
    return render_template('fuelling/index.html', aktiver_vorgang=aktiver_vorgang)

@bp.route('/start', methods=['POST'])
def start():
    """Neuen Füllvorgang starten"""
    operator = request.form.get('operator', 'Unbekannt')
    
    # Prüfen ob bereits ein Vorgang läuft
    aktiver_vorgang = Fuellvorgang.get_aktiver_fuellvorgang()
    if aktiver_vorgang:
        return jsonify({'error': 'Ein Füllvorgang läuft bereits'}), 400
    
    # Neuen Vorgang starten
    vorgang = Fuellvorgang(operator=operator)
    db.session.add(vorgang)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'vorgang': vorgang.to_dict()
    })

@bp.route('/stop', methods=['POST'])
def stop():
    """Aktiven Füllvorgang beenden"""
    aktiver_vorgang = Fuellvorgang.get_aktiver_fuellvorgang()
    
    if not aktiver_vorgang:
        return jsonify({'error': 'Kein aktiver Füllvorgang'}), 400
    
    # Vorgang beenden
    aktiver_vorgang.beenden()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'vorgang': aktiver_vorgang.to_dict()
    })
