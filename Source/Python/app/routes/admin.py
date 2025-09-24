"""
Admin-Routes für WartungsManager
Einstellungen, Konfiguration und System-Management
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.config.shelly_config import ShellyKonfiguration
import logging

# Blueprint für Admin-Interface
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def index():
    """Admin Dashboard"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/settings')
def settings():
    """System-Einstellungen"""
    return render_template('admin/settings.html')

@admin_bp.route('/shelly-config')
def shelly_config():
    """Shelly-Konfiguration Interface"""
    return render_template('shelly_config.html')

@admin_bp.route('/system-info')
def system_info():
    """System-Informationen anzeigen"""
    
    import sys
    import platform
    from pathlib import Path
    
    # System-Info sammeln
    system_data = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'hostname': platform.node()
    }
    
    # Pfad-Info
    current_path = Path.cwd()
    db_path = current_path / "../../database/wartungsmanager.db"
    
    path_data = {
        'working_directory': str(current_path),
        'database_path': str(db_path.resolve()),
        'database_exists': db_path.exists(),
        'database_size': db_path.stat().st_size if db_path.exists() else 0
    }
    
    return jsonify({
        'system': system_data,
        'paths': path_data
    })

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
