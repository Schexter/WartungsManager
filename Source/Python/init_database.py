from app import create_app, db

print("Datenbank-Initialisierung startet...")

# App erstellen
app = create_app()

with app.app_context():
    try:
        # Alle Tabellen erstellen
        db.create_all()
        print("Alle Tabellen erfolgreich erstellt!")

        # Test-Verbindung
        result = db.session.execute(db.text("SELECT 1"))
        print("Datenbank-Verbindung erfolgreich getestet!")

        print("Datenbank-Setup abgeschlossen!")

    except Exception as e:
        print(f"FEHLER beim Datenbank-Setup: {e}")
        print("Tipp: Pruefen Sie Dateiberechtigungen im database-Ordner")