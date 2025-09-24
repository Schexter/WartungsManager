# Protocol-Routes für Handbefüllung
from flask import Blueprint, render_template
from app.models import Handbefuellung

bp = Blueprint('protocol', __name__)

@bp.route('/')
def index():
    """Protokoll-Übersichtsseite"""
    return render_template('protocol/index.html')
