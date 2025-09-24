#!/usr/bin/env python3
"""
Migration für erweiterte Flaschen-Rückverfolgbarkeit ausführen
"""

import sys
import os

# Aktuelles Projektverzeichnis hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app import create_app, db
from app.models.flaschen import Flasche
import importlib.util

def migration_ausführen():
    """Führt die Migration 0011 für erweiterte Flaschen-Rückverfolgbarkeit aus"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Starte Migration für erweiterte Flaschen-Rückverfolgbarkeit...")
        
        try:
            # Migration-Modul laden
            spec = importlib.util.spec_from_file_location(
                "migration_0011", 
                "migrations/versions/0011_erweiterte_flaschen_rueckverfolgung.py"
            )
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            
            # Migration ausführen
            print("📝 Führe Migration 0011 aus...")
            migration_module.upgrade()
            
            print("✅ Migration erfolgreich abgeschlossen!")
            
            # Test: Neue Felder prüfen
            print("🔍 Teste neue Felder...")
            
            # Hole eine beliebige Flasche zum Testen
            test_flasche = Flasche.query.first()
            if test_flasche:
                print(f"📋 Test-Flasche: {test_flasche.flasche_nummer}")
                
                # Teste neue Felder
                if hasattr(test_flasche, 'interne_flaschennummer_auto'):
                    print("✓ Neue Felder erfolgreich hinzugefügt")
                    
                    # Teste erweiterte to_dict Methode
                    flasche_dict = test_flasche.to_dict(include_extended=True)
                    print(f"✓ Erweiterte Serialisierung funktioniert: {len(flasche_dict)} Felder")
                    
                else:
                    print("⚠️  Einige neue Felder wurden möglicherweise nicht hinzugefügt")
            else:
                print("ℹ️  Keine Flaschen zum Testen gefunden")
            
            print("\n🎉 Erweiterte Flaschen-Rückverfolgbarkeit ist bereit!")
            print("📋 Neue Features:")
            print("   • Automatische interne Flaschennummer-Generierung")
            print("   • Erweiterte Bauartzulassung-Verwaltung")
            print("   • Prüfungshistorie und -Benachrichtigungen")
            print("   • Barcode-Optimierungen")
            print("   • Externe System-Integration")
            print("   • Rückverfolgbarkeit und Zertifizierung")
            
        except Exception as e:
            print(f"❌ Fehler bei Migration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    if migration_ausführen():
        print("\n✅ Migration erfolgreich abgeschlossen!")
        exit(0)
    else:
        print("\n❌ Migration fehlgeschlagen!")
        exit(1)
