"""
Kompressor UI Routes
"""
from flask import Blueprint, render_template

bp = Blueprint('kompressor', __name__, url_prefix='/kompressor')

@bp.route('/')
def index():
    return render_template('kompressor/index.html')