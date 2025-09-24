"""
Hauptrouten für WartungsManager
Grundlegende Navigation und Startseite
"""

from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Startseite"""
    return render_template('dashboard.html')

@main_bp.route('/health')
def health():
    """Health Check Endpoint"""
    return {"status": "ok", "message": "WartungsManager läuft"}

@main_bp.route('/info')
def system_info():
    """System-Informationen"""
    import platform
    import sys
    from pathlib import Path
    
    return {
        "system": "WartungsManager",
        "status": "running",
        "python_version": sys.version,
        "platform": platform.platform(),
        "working_directory": str(Path.cwd())
    }

@main_bp.route('/shelly-setup')
@main_bp.route('/shelly-setup/')
def shelly_setup():
    """Shelly IoT Konfiguration"""
    return render_template('shelly_setup.html')

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard mit allen Funktionen"""
    return render_template('dashboard.html')

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
