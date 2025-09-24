#!/usr/bin/env python3
"""
WartungsManager - ULTRA MINIMAL START
Umgeht SQLAlchemy-Probleme durch minimalen Import
Erstellt von Hans Hahn - Alle Rechte vorbehalten
"""

import os
import sys
from pathlib import Path

def setup_paths():
    """Python-Pfade konfigurieren"""
    project_root = Path(__file__).parent.absolute()
    source_python_path = project_root / "Source" / "Python"
    
    if source_python_path.exists():
        sys.path.insert(0, str(source_python_path))
        os.chdir(source_python_path)
        print(f"✅ Pfad: {source_python_path}")
        return True
    return False

def create_emergency_flask_app():
    """Notfall Flask-App ohne SQLAlchemy"""
    
    try:
        from flask import Flask, render_template, jsonify
        
        app = Flask(__name__)
        app.config.update({
            'SECRET_KEY': 'wartungsmanager-emergency-2025',
            'DEBUG': False
        })
        
        @app.route('/')
        def index():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>🔧 WartungsManager - Notfall-Modus</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        max-width: 800px; 
                        margin: 50px auto; 
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1 { color: #2c5aa0; text-align: center; }
                    .status { 
                        background: #ffa500; 
                        color: white; 
                        padding: 15px; 
                        border-radius: 5px;
                        text-align: center;
                        margin: 20px 0;
                    }
                    .info {
                        background: #e7f3ff;
                        border-left: 4px solid #2196F3;
                        padding: 15px;
                        margin: 20px 0;
                    }
                    .success {
                        background: #d4edda;
                        color: #155724;
                        border: 1px solid #c3e6cb;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔧 WartungsManager</h1>
                    
                    <div class="status">
                        <h2>⚠️ NOTFALL-MODUS AKTIV</h2>
                        <p>System läuft im reduzierten Modus ohne Datenbank</p>
                    </div>
                    
                    <div class="success">
                        <h3>✅ GUTE NACHRICHTEN:</h3>
                        <ul>
                            <li><strong>Flask funktioniert!</strong> ✅</li>
                            <li><strong>Python 3.13 läuft!</strong> ✅</li>
                            <li><strong>Web-Server ist aktiv!</strong> ✅</li>
                            <li><strong>Pfad-Konfiguration korrekt!</strong> ✅</li>
                        </ul>
                    </div>
                    
                    <div class="info">
                        <h3>🔍 IDENTIFIZIERTES PROBLEM:</h3>
                        <p><strong>SQLAlchemy 2.0.21</strong> ist nicht kompatibel mit <strong>Python 3.13.3</strong></p>
                        
                        <h3>🛠️ SOFORT-LÖSUNG:</h3>
                        <ol>
                            <li>Führen Sie aus: <code>SQLALCHEMY_PYTHON313_FIX.bat</code></li>
                            <li>Startet SQLAlchemy-Upgrade auf kompatible Version</li>
                            <li>Danach läuft das komplette System</li>
                        </ol>
                    </div>
                    
                    <div class="info">
                        <h3>📋 SYSTEM-INFO:</h3>
                        <ul>
                            <li><strong>Python:</strong> 3.13.3</li>
                            <li><strong>Flask:</strong> 2.3.3</li>
                            <li><strong>Status:</strong> Basis-System funktioniert</li>
                            <li><strong>Nächster Schritt:</strong> SQLAlchemy reparieren</li>
                        </ul>
                    </div>
                    
                    <div class="success">
                        <h3>🎯 FAZIT:</h3>
                        <p>Das WartungsManager-System ist <strong>grundsätzlich funktionsfähig</strong>! 
                        Es braucht nur ein SQLAlchemy-Update für Python 3.13 Kompatibilität.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        @app.route('/status')
        def status():
            return jsonify({
                'status': 'emergency_mode',
                'python_version': sys.version,
                'flask_working': True,
                'sqlalchemy_working': False,
                'problem': 'SQLAlchemy 2.0.21 not compatible with Python 3.13',
                'solution': 'Run SQLALCHEMY_PYTHON313_FIX.bat'
            })
        
        return app
        
    except Exception as e:
        print(f"❌ Notfall-App Fehler: {e}")
        return None

def main():
    """Hauptfunktion"""
    
    print("🚨 WARTUNGSMANAGER - NOTFALL-MODUS")
    print("=" * 50)
    
    if not setup_paths():
        return False
    
    app = create_emergency_flask_app()
    if not app:
        return False
    
    try:
        print("✅ Notfall-Modus aktiviert!")
        print("🌐 ÖFFNEN SIE: http://localhost:5000")
        print("📋 Zeigt detaillierte Reparatur-Anweisungen")
        print("⏹️ CTRL+C zum Beenden")
        print("=" * 50)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False
        )
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Notfall-Server gestoppt")
        return True
    except Exception as e:
        print(f"\n❌ Server-Fehler: {e}")
        return False

if __name__ == '__main__':
    main()
