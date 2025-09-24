"""
Füllmanager Routes - Verwaltung des gesamten Füllprozesses
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
# Flask-Login ist nicht installiert, daher Mock-Funktionen
def login_required(f):
    return f

class MockUser:
    id = 1
    username = 'operator'

current_user = MockUser()

from flask_wtf.csrf import generate_csrf
from datetime import datetime, date
from app import db
from app.models.fuellmanager import FuellManager, FuellManagerSignatur, FuellVorgangErweitert
from app.models.fuellmanager.preiskonfiguration import GasPreisKonfiguration
from app.models.kunden import Kunde
from app.models.flaschen import Flasche
from app.forms.fuelling import FuellmanagerForm

bp = Blueprint('fuellmanager', __name__, url_prefix='/fuellmanager')


@bp.route('/')
@login_required
def index():
    """Füllmanager Übersicht"""
    # Aktive Füllvorgänge
    aktive_fuellungen = FuellManager.query.filter(
        FuellManager.status.in_(['angenommen', 'in_fuellung'])
    ).order_by(FuellManager.erstellt_am.desc()).all()
    
    # Heutige abgeschlossene Füllvorgänge
    heute_start = datetime.combine(date.today(), datetime.min.time())
    heutige_fuellungen = FuellManager.query.filter(
        FuellManager.status == 'abgeschlossen',
        FuellManager.erstellt_am >= heute_start
    ).order_by(FuellManager.uebergabe_zeit.desc()).all()
    
    return render_template('fuellmanager/index.html',
                         aktive_fuellungen=aktive_fuellungen,
                         heutige_fuellungen=heutige_fuellungen)


@bp.route('/neue-annahme', methods=['GET', 'POST'])
@login_required
def neue_annahme():
    """Neue Flasche annehmen"""
    if request.method == 'POST':
        try:
            # Erstelle neuen Füllvorgang
            fuellvorgang = FuellManager(
                kunde_id=request.form.get('kunde_id'),
                flasche_id=request.form.get('flasche_id'),
                operator_id=current_user.id,
                visuelle_pruefung=request.form.get('visuelle_pruefung') == 'on',
                tuev_geprueft=request.form.get('tuev_geprueft') == 'on',
                ventil_zustand=request.form.get('ventil_zustand'),
                annahme_notizen=request.form.get('annahme_notizen'),
                restdruck_bar=float(request.form.get('restdruck_bar', 0)),
                zieldruck_bar=float(request.form.get('zieldruck_bar', 220)),
                sauerstoff_prozent=float(request.form.get('sauerstoff_prozent', 21)),
                helium_prozent=float(request.form.get('helium_prozent', 0)),
                stickstoff_prozent=float(request.form.get('stickstoff_prozent', 79))
            )
            
            # Auftragsnummer generieren
            fuellvorgang.generiere_auftragsnummer()
            
            # Preise berechnen
            fuellvorgang.berechne_preise()
            
            # Tauchparameter berechnen
            fuellvorgang.berechne_tauchparameter()
            
            db.session.add(fuellvorgang)
            
            # Ereignis protokollieren
            ereignis = FuellVorgangErweitert(
                fuellmanager_id=fuellvorgang.id,
                ereignis_typ='annahme',
                operator_id=current_user.id,
                details=f"Flasche angenommen. Visuelle Prüfung: {fuellvorgang.visuelle_pruefung}, TÜV: {fuellvorgang.tuev_geprueft}"
            )
            db.session.add(ereignis)
            
            db.session.commit()
            
            flash(f'Füllvorgang {fuellvorgang.auftragsnummer} erfolgreich angelegt!', 'success')
            return redirect(url_for('fuellmanager.details', id=fuellvorgang.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Anlegen des Füllvorgangs: {str(e)}', 'danger')
    
    # Lade alle aktiven Kunden
    kunden = Kunde.query.filter_by(ist_aktiv=True).order_by(Kunde.nachname, Kunde.vorname).all()
    
    return render_template('fuellmanager/annahme.html', 
                         kunden=kunden,
                         csrf_token=generate_csrf)


@bp.route('/details/<int:id>')
@login_required
def details(id):
    """Füllvorgang Details anzeigen"""
    fuellvorgang = FuellManager.query.get_or_404(id)
    return render_template('fuellmanager/details.html', 
                         fuellvorgang=fuellvorgang,
                         csrf_token=generate_csrf)


@bp.route('/start-fuellung/<int:id>', methods=['POST'])
@login_required
def start_fuellung(id):
    """Füllvorgang starten"""
    fuellvorgang = FuellManager.query.get_or_404(id)
    
    if fuellvorgang.status != 'angenommen':
        flash('Füllvorgang kann nicht gestartet werden!', 'danger')
        return redirect(url_for('fuellmanager.details', id=id))
    
    try:
        fuellvorgang.start_fuellung()
        
        # Ereignis protokollieren
        ereignis = FuellVorgangErweitert(
            fuellmanager_id=fuellvorgang.id,
            ereignis_typ='fuellstart',
            operator_id=current_user.id,
            details=f"Füllung gestartet"
        )
        db.session.add(ereignis)
        db.session.commit()
        
        flash('Füllvorgang gestartet!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Starten: {str(e)}', 'danger')
    
    return redirect(url_for('fuellmanager.details', id=id))


@bp.route('/beende-fuellung/<int:id>', methods=['POST'])
@login_required
def beende_fuellung(id):
    """Füllvorgang beenden"""
    fuellvorgang = FuellManager.query.get_or_404(id)
    
    if fuellvorgang.status != 'in_fuellung':
        flash('Füllvorgang kann nicht beendet werden!', 'danger')
        return redirect(url_for('fuellmanager.details', id=id))
    
    try:
        enddruck = float(request.form.get('tatsaechlicher_enddruck', fuellvorgang.zieldruck_bar))
        notizen = request.form.get('fuell_notizen')
        
        fuellvorgang.beende_fuellung(enddruck)
        if notizen:
            fuellvorgang.fuell_notizen = notizen
        
        # Ereignis protokollieren
        ereignis = FuellVorgangErweitert(
            fuellmanager_id=fuellvorgang.id,
            ereignis_typ='fuellende',
            operator_id=current_user.id,
            details=f"Füllung beendet. Enddruck: {enddruck} bar"
        )
        db.session.add(ereignis)
        db.session.commit()
        
        flash('Füllvorgang beendet! Bitte Unterschriften erfassen.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Beenden: {str(e)}', 'danger')
    
    return redirect(url_for('fuellmanager.details', id=id))


@bp.route('/speichere-unterschrift/<int:id>', methods=['POST'])
@login_required
def speichere_unterschrift(id):
    """Unterschriften speichern und Vorgang abschließen"""
    fuellvorgang = FuellManager.query.get_or_404(id)
    
    if fuellvorgang.status == 'abgeschlossen':
        flash('Füllvorgang bereits abgeschlossen!', 'info')
        return redirect(url_for('fuellmanager.details', id=id))
    
    try:
        # Kundenunterschrift speichern
        kunden_signatur = request.form.get('kunden_signatur')
        if kunden_signatur:
            kunde_sig = FuellManagerSignatur(
                fuellmanager_id=fuellvorgang.id,
                signatur_typ='kunde',
                signatur_daten=kunden_signatur,
                unterschrieben_von=fuellvorgang.kunde.vollname,
                device_info=request.headers.get('User-Agent'),
                ip_adresse=request.remote_addr
            )
            db.session.add(kunde_sig)
        
        # Mitarbeiterunterschrift speichern
        mitarbeiter_signatur = request.form.get('mitarbeiter_signatur')
        if mitarbeiter_signatur:
            mitarbeiter_sig = FuellManagerSignatur(
                fuellmanager_id=fuellvorgang.id,
                signatur_typ='mitarbeiter',
                signatur_daten=mitarbeiter_signatur,
                unterschrieben_von=current_user.username,
                device_info=request.headers.get('User-Agent'),
                ip_adresse=request.remote_addr
            )
            db.session.add(mitarbeiter_sig)
        
        # Vorgang abschließen
        fuellvorgang.abschliessen()
        
        # Ereignis protokollieren
        ereignis = FuellVorgangErweitert(
            fuellmanager_id=fuellvorgang.id,
            ereignis_typ='uebergabe',
            operator_id=current_user.id,
            details=f"Füllvorgang abgeschlossen. Unterschriften erfasst."
        )
        db.session.add(ereignis)
        
        db.session.commit()
        
        flash('Füllvorgang erfolgreich abgeschlossen!', 'success')
        return redirect(url_for('fuellmanager.details', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Speichern der Unterschriften: {str(e)}', 'danger')
        return redirect(url_for('fuellmanager.details', id=id))


@bp.route('/drucken/<int:id>')
@login_required
def drucken(id):
    """Füllbeleg drucken"""
    fuellvorgang = FuellManager.query.get_or_404(id)
    return render_template('fuellmanager/drucken.html', 
                         fuellvorgang=fuellvorgang,
                         datetime=datetime)


# API Endpoints für AJAX
@bp.route('/api/kunden/<int:kunde_id>/flaschen')
@login_required
def api_kunden_flaschen(kunde_id):
    """API: Flaschen eines Kunden abrufen"""
    kunde = Kunde.query.get_or_404(kunde_id)
    flaschen = Flasche.query.filter_by(
        kunde_id=kunde_id,
        ist_aktiv=True
    ).order_by(Flasche.flasche_nummer).all()
    
    return jsonify({
        'flaschen': [f.to_dict(include_besitzer=False) for f in flaschen]
    })


@bp.route('/api/flaschen/<int:flasche_id>')
@login_required
def api_flasche_details(flasche_id):
    """API: Flaschendetails abrufen"""
    flasche = Flasche.query.get_or_404(flasche_id)
    return jsonify(flasche.to_dict(include_besitzer=True))


@bp.route('/api/fuellvorgang/<int:id>/status')
@login_required
def api_fuellvorgang_status(id):
    """API: Status eines Füllvorgangs"""
    fuellvorgang = FuellManager.query.get_or_404(id)
    return jsonify({
        'id': fuellvorgang.id,
        'status': fuellvorgang.status,
        'dauer_minuten': (
            (datetime.utcnow() - fuellvorgang.fuellstart_zeit).total_seconds() / 60
            if fuellvorgang.fuellstart_zeit and fuellvorgang.status == 'in_fuellung'
            else None
        )
    })


@bp.route('/preise')
@login_required
def preise():
    """Preiskonfiguration anzeigen"""
    # Initialisiere Standard-Preise falls noch nicht vorhanden
    GasPreisKonfiguration.initialisiere_standard_preise()
    
    # Hole aktuelle Preise
    aktuelle_preise = {}
    for gas_typ in ['helium', 'sauerstoff', 'luft']:
        config = GasPreisKonfiguration.query.filter_by(
            gas_typ=gas_typ,
            ist_aktiv=True
        ).order_by(GasPreisKonfiguration.gueltig_ab.desc()).first()
        
        aktuelle_preise[gas_typ] = {
            'preis': config.preis_pro_bar_liter if config else 0.0,
            'seit': config.gueltig_ab if config else None
        }
    
    # Hole Preishistorie
    historie = GasPreisKonfiguration.query.order_by(
        GasPreisKonfiguration.gueltig_ab.desc()
    ).limit(50).all()
    
    return render_template('fuellmanager/preise.html',
                         preise=aktuelle_preise,
                         historie=historie,
                         csrf_token=generate_csrf)


@bp.route('/update-preise', methods=['POST'])
@login_required
def update_preise():
    """Preise aktualisieren"""
    try:
        # Neue Preise aus dem Formular
        neue_preise = {
            'helium': float(request.form.get('preis_helium', 0)),
            'sauerstoff': float(request.form.get('preis_sauerstoff', 0)),
            'luft': float(request.form.get('preis_luft', 0))
        }
        
        # Aktualisiere jeden Preis
        for gas_typ, neuer_preis in neue_preise.items():
            if neuer_preis > 0:
                GasPreisKonfiguration.setze_preis(
                    gas_typ=gas_typ,
                    neuer_preis=neuer_preis,
                    erstellt_von=current_user.username
                )
        
        flash('Preise erfolgreich aktualisiert!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Aktualisieren der Preise: {str(e)}', 'danger')
    
    return redirect(url_for('fuellmanager.preise'))


@bp.route('/api/gaspreise')
@login_required
def api_gaspreise():
    """API: Aktuelle Gaspreise abrufen"""
    preise = GasPreisKonfiguration.get_aktuelle_preise()
    return jsonify({'preise': preise})
