#!/usr/bin/env python3
"""
Wartungsmanager - MINIMAL START (Python 3.13 kompatibel)
Nur mit essentiellen Paketen - ohne problematische Dependencies
Erstellt von Hans Hahn - Alle Rechte vorbehalten
"""

import os
import sys
from pathlib import Path

def setup_minimal_paths():
    """Minimale Python-Pfad-Konfiguration"""
    
    project_root = Path(__file__).parent.absolute()
    source_python_path = project_root / "Source" / "Python"
    
    if source_python_path.exists():
        sys.path.insert(0, str(source_python_path))
        os.chdir(source_python_path)
        print(f"✅ Pfad konfiguriert: {source_python_path}")
        return True
    else:
        print(f"❌ Source/Python nicht gefunden: {source_python_path}")
        return False

def test_minimal_imports():
    """Test nur die essentiellen Imports"""
    
    print("\n🔍 Minimaler Import-Test...")
    
    # Flask testen
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask fehlt: {e}")
        return False
    
    # App-Modul testen
    try:
        import app
        print("✅ App-Modul gefunden")
    except ImportError as e:
        print(f"❌ App-Modul fehlt: {e}")
        return False
    
    # create_app testen
    try:
        from app import create_app
        print("✅ create_app verfügbar")
    except ImportError as e:
        print(f"❌ create_app fehlt: {e}")
        return False
    
    return True

def create_minimal_app():
    """Minimale App ohne problematische Features"""
    
    try:
        from app import create_app
        
        # App mit minimaler Konfiguration erstellen
        app = create_app()
        
        # Basis-Konfiguration
        app.config.update({
            'DEBUG': False,
            'TESTING': False,
            'SECRET_KEY': 'wartungsmanager-minimal-key-2025'
        })
        
        return app
        
    except Exception as e:
        print(f"❌ App-Erstellung fehlgeschlagen: {e}")
        return None

def run_minimal_server():
    """Minimaler Server ohne problematische Features"""
    
    print("🚀 WARTUNGSMANAGER - MINIMAL START")
    print("=" * 50)
    
    app = create_minimal_app()
    if not app:
        return False
    
    try:
        print("🌐 Server startet...")
        print("📱 Zugriff: http://localhost:5000")
        print("⏹️  CTRL+C zum Beenden")
        print("=" * 50)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Server gestoppt")
        return True
    except Exception as e:
        print(f"\n❌ Server-Fehler: {e}")
        return False

def main():
    """Hauptfunktion für minimalen Start"""
    
    print("🔧 WartungsManager - Minimal Start für Python 3.13")
    
    # Schritt 1: Pfade konfigurieren
    if not setup_minimal_paths():
        input("❌ Pfad-Konfiguration fehlgeschlagen. Enter zum Beenden...")
        return False
    
    # Schritt 2: Minimale Imports testen
    if not test_minimal_imports():
        print("\n💡 LÖSUNG: Führen Sie PYTHON313_REPARATUR.bat aus")
        input("❌ Import-Test fehlgeschlagen. Enter zum Beenden...")
        return False
    
    # Schritt 3: Server starten
    print("\n✅ Alle Tests bestanden - starte Server...")
    return run_minimal_server()

if __name__ == '__main__':
    success = main()
    if not success:
        input("\n❌ Fehler aufgetreten. Drücken Sie Enter zum Beenden...")
        sys.exit(1)
