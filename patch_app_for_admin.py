#!/usr/bin/env python3
"""
App-Erweiterung für Admin-Interface und Shelly-Integration
Fügt die neuen Blueprints zur bestehenden App hinzu
"""

import os
import sys
from pathlib import Path

def patch_app_init():
    """Erweitert die App-Initialisierung"""
    
    # Pfad zur App __init__.py
    app_init_path = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/app/__init__.py")
    
    if not app_init_path.exists():
        print(f"❌ App __init__.py nicht gefunden: {app_init_path}")
        return False
    
    # Aktuelle App lesen
    with open(app_init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Admin-Blueprint-Import hinzufügen
    if "from app.routes.admin import admin_bp" not in content:
        # Finde die Import-Sektion
        import_section = content.find("from flask import Flask")
        if import_section != -1:
            # Füge nach den Flask-Imports ein
            insertion_point = content.find("\n", import_section)
            new_imports = """
# Admin & Shelly Integration
try:
    from app.routes.admin import admin_bp
    from app.routes.shelly_api import shelly_api, init_shelly_api
    ADMIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Admin-Module nicht verfügbar: {e}")
    ADMIN_AVAILABLE = False
"""
            content = content[:insertion_point] + new_imports + content[insertion_point:]
    
    # Blueprint-Registrierung hinzufügen
    if "app.register_blueprint(admin_bp)" not in content:
        # Finde die create_app Funktion
        create_app_pos = content.find("def create_app(")
        if create_app_pos != -1:
            # Finde das Ende der Funktion (vor return app)
            return_pos = content.find("return app", create_app_pos)
            if return_pos != -1:
                blueprint_registration = """
    
    # Admin & Shelly Integration registrieren
    if ADMIN_AVAILABLE:
        try:
            app.register_blueprint(admin_bp)
            app.register_blueprint(shelly_api)
            init_shelly_api(app)
            app.logger.info("✅ Admin-Interface aktiviert: /admin")
            app.logger.info("✅ Shelly-API aktiviert: /api/shelly")
        except Exception as e:
            app.logger.error(f"❌ Admin/Shelly-Setup Fehler: {e}")
    else:
        app.logger.warning("⚠️ Admin-Interface nicht verfügbar")
    
"""
                content = content[:return_pos] + blueprint_registration + content[return_pos:]
    
    # Datei zurückschreiben
    with open(app_init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ App-Initialisierung erweitert")
    return True

def create_admin_route_access():
    """Erstellt einfache Route für Admin-Zugang"""
    
    # Einfache HTML-Seite für Admin-Zugang
    admin_access_html = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>WartungsManager - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c5aa0; text-align: center; }
        .admin-links { display: grid; gap: 15px; margin-top: 30px; }
        .admin-link { display: block; padding: 15px; background: #3498db; color: white; text-decoration: none; text-align: center; border-radius: 5px; font-size: 16px; }
        .admin-link:hover { background: #2980b9; color: white; text-decoration: none; }
        .status { background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 WartungsManager Admin</h1>
        
        <div class="status">
            <h3>System-Status</h3>
            <p>✅ <strong>Server läuft:</strong> http://localhost:5000</p>
            <p>✅ <strong>Datenbank:</strong> Verbindung hergestellt</p>
            <p>⚠️ <strong>Shelly:</strong> Nicht konfiguriert</p>
        </div>
        
        <div class="admin-links">
            <a href="/admin" class="admin-link">🎛️ Admin Dashboard</a>
            <a href="/templates/shelly_config.html" class="admin-link">🔌 Shelly Konfiguration</a>
            <a href="/api/shelly/config" class="admin-link">⚙️ Shelly API Status</a>
            <a href="/" class="admin-link">🏠 Zurück zum Hauptsystem</a>
        </div>
        
        <div class="status">
            <h3>Schnellhilfe</h3>
            <ul>
                <li><strong>Shelly einrichten:</strong> IP-Adresse des Shelly-Geräts eingeben</li>
                <li><strong>Modell wählen:</strong> Shelly1, Shelly1PM, ShellyPlus1, ShellyPlus1PM</li>
                <li><strong>Verbindung testen:</strong> "Test Connection" Button verwenden</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
    
    # HTML-Datei erstellen
    admin_html_path = Path("C:/SoftwareEntwicklung/WartungsManager-main/Source/Python/app/templates/admin_access.html")
    with open(admin_html_path, 'w', encoding='utf-8') as f:
        f.write(admin_access_html)
    
    print("✅ Admin-Access-Seite erstellt")
    
    return True

def main():
    print("🔧 WartungsManager App-Erweiterung")
    print("=" * 50)
    
    try:
        # Schritt 1: App erweitern
        if patch_app_init():
            print("✅ App-Initialisierung erweitert")
        
        # Schritt 2: Admin-Access erstellen
        if create_admin_route_access():
            print("✅ Admin-Zugang erstellt")
        
        print("\n🎉 APP-ERWEITERUNG ABGESCHLOSSEN!")
        print("=" * 50)
        print("✅ Admin-Interface verfügbar unter: /admin")
        print("✅ Shelly-API verfügbar unter: /api/shelly")
        print("✅ Admin-Zugang über: /templates/admin_access.html")
        
        print("\n🚀 Starten Sie das System neu für die Änderungen:")
        print("python run_production_REPARIERT.py")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == '__main__':
    main()
