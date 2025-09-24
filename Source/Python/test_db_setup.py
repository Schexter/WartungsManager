import os
import sys

# Flask App für Testing
from app import create_app, db

app = create_app()

with app.app_context():
    print("🔧 Database-Tabellen erstellen...")
    try:
        db.create_all()
        print("✅ Tabellen erfolgreich erstellt!")
        
        # Importiere Models für Sicherheit
        from app.models.flaschen import Flasche
        from app.models.kunden import Kunde
        from app.models.warteliste import WartelisteEintrag
        
        print("✅ Models erfolgreich importiert!")
        print("🎯 System ist bereit!")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
