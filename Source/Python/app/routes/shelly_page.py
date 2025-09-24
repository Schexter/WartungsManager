"""
Shelly-Seiten Route für direkten Zugriff
"""
from flask import Blueprint, render_template

# Blueprint für direkte Shelly-Seite (ohne /api)
shelly_page_bp = Blueprint('shelly_page', __name__)

@shelly_page_bp.route('/shelly')
def shelly():
    """Shelly-Verwaltungsseite"""
    return render_template('shelly.html')

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
