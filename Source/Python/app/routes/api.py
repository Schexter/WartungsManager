# API Routes für WartungsManager
from flask import Blueprint, jsonify
from app.models import Fuellvorgang, Wartung, Handbefuellung

bp = Blueprint('api', __name__)

@bp.route('/status')
def status():
    """System-Status API"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0'
    })
