# Datenbank-Migration für Kompressor-System Erweiterung
# Erstellt alle neuen Tabellen für das erweiterte Kompressor-Management

from flask import current_app
from app import db
from app.models import KompressorBetrieb, Kunde, Flasche, BulkFuellvorgang, FlascheFuellvorgang
import logging

def upgrade():
    """Erstellt alle neuen Tabellen für das Kompressor-System"""
    
    logger = logging.getLogger(__name__)
    logger.info("Starte Datenbank-Migration für Kompressor-System...")
    
    try:
        # Alle Tabellen erstellen
        db.create_all()
        
        # Standard-Daten einfügen
        create_sample_data()
        
        logger.info("✅ Datenbank-Migration erfolgreich abgeschlossen")
        return True
        
    except Exception as e:
        logger.error(f"❌ Fehler bei Datenbank-Migration: {str(e)}")
        db.session.rollback()
        return False

def create_sample_data():
    """Erstellt Beispiel-Daten für Tests"""
    
    # Beispiel-Kunde erstellen (falls noch nicht vorhanden)
    beispiel_kunde = Kunde.query.filter_by(mitgliedsnummer='M-001').first()
    if not beispiel_kunde:
        beispiel_kunde = Kunde(
            mitgliedsnummer='M-001',
            vorname='Max',
            nachname='Mustermann',
            firma='Beispiel GmbH',
            email='max@beispiel.de',
            telefon='0123-456789',
            strasse='Musterstraße 1',
            plz='12345',
            ort='Musterstadt',
            mitgliedschaft_typ='Standard',
            notizen='Automatisch erstellter Beispiel-Kunde'
        )
        db.session.add(beispiel_kunde)
        db.session.flush()  # Damit wir die ID bekommen
        
        # Beispiel-Flasche für den Kunden erstellen
        beispiel_flasche = Flasche(
            flaschennummer='F-001',
            kunde_id=beispiel_kunde.id,
            groesse_liter=11.0,
            flaschen_typ='Standard',
            farbe='Schwarz',
            hersteller='Test-Hersteller',
            max_druck_bar=300,
            notizen='Automatisch erstellte Beispiel-Flasche'
        )
        db.session.add(beispiel_flasche)
    
    db.session.commit()

def verify_migration():
    """Überprüft ob Migration erfolgreich war"""
    
    try:
        # Prüfe ob alle Tabellen existieren
        tables_to_check = [
            'kompressor_betrieb',
            'kunden', 
            'flaschen',
            'bulk_fuellvorgaenge',
            'flasche_fuellvorgang'
        ]
        
        engine = db.engine
        existing_tables = engine.table_names()
        
        for table in tables_to_check:
            if table not in existing_tables:
                return False, f"Tabelle '{table}' wurde nicht erstellt"
        
        # Prüfe ob Beispiel-Daten existieren
        kunde_count = Kunde.query.count()
        if kunde_count == 0:
            return False, "Keine Beispiel-Daten erstellt"
        
        return True, "Migration erfolgreich verifiziert"
        
    except Exception as e:
        return False, f"Verifikation fehlgeschlagen: {str(e)}"

def rollback():
    """Macht Migration rückgängig (nur für Entwicklung!)"""
    
    logger = logging.getLogger(__name__)
    logger.warning("⚠️  ACHTUNG: Rollback wird ausgeführt - Alle Daten gehen verloren!")
    
    try:
        # Tabellen in umgekehrter Reihenfolge löschen (wegen Foreign Keys)
        tables_to_drop = [
            'flasche_fuellvorgang',
            'bulk_fuellvorgaenge', 
            'flaschen',
            'kunden',
            'kompressor_betrieb'
        ]
        
        for table in tables_to_drop:
            try:
                db.engine.execute(f'DROP TABLE IF EXISTS {table}')
                logger.info(f"Tabelle '{table}' gelöscht")
            except Exception as e:
                logger.warning(f"Fehler beim Löschen von '{table}': {str(e)}")
        
        logger.info("✅ Rollback abgeschlossen")
        return True
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Rollback: {str(e)}")
        return False

# CLI-Funktionen für Flask
def init_db_command():
    """Flask CLI Command für Migration"""
    
    print("🔄 Starte Kompressor-System Migration...")
    
    success = upgrade()
    if success:
        verification_success, message = verify_migration()
        if verification_success:
            print(f"✅ {message}")
        else:
            print(f"⚠️  Migration abgeschlossen, aber Verifikation fehlgeschlagen: {message}")
    else:
        print("❌ Migration fehlgeschlagen")
    
    return success

if __name__ == "__main__":
    # Direkte Ausführung für Tests
    print("Kompressor-System Migration")
    print("===========================")
    
    choice = input("Aktion wählen:\n1) Migration (upgrade)\n2) Rollback\n3) Verifikation\nEingabe: ")
    
    if choice == "1":
        init_db_command()
    elif choice == "2":
        confirm = input("⚠️  WARNUNG: Alle Daten gehen verloren! Fortfahren? (ja/nein): ")
        if confirm.lower() == 'ja':
            rollback()
        else:
            print("Rollback abgebrochen")
    elif choice == "3":
        success, message = verify_migration()
        print(f"{'✅' if success else '❌'} {message}")
    else:
        print("Ungültige Eingabe")
