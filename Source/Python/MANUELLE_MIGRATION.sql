-- MANUELLE SQL-MIGRATION für erweiterte Flaschen-Rückverfolgbarkeit
-- Falls automatische Migration fehlschlägt

-- 1. Backup erstellen (außerhalb SQL)
-- Kopieren Sie database/wartungsmanager.db zu wartungsmanager.db.backup

-- 2. Neue Spalten hinzufügen
ALTER TABLE flaschen ADD COLUMN interne_flaschennummer_auto BOOLEAN DEFAULT FALSE;
ALTER TABLE flaschen ADD COLUMN barcode_typ VARCHAR(20) DEFAULT 'CODE128';
ALTER TABLE flaschen ADD COLUMN letzte_pruefung_protokoll TEXT;
ALTER TABLE flaschen ADD COLUMN pruefung_benachrichtigt BOOLEAN DEFAULT FALSE;
ALTER TABLE flaschen ADD COLUMN pruefung_benachrichtigung_datum DATE;
ALTER TABLE flaschen ADD COLUMN flaschen_gewicht_kg REAL;
ALTER TABLE flaschen ADD COLUMN ventil_typ VARCHAR(50);
ALTER TABLE flaschen ADD COLUMN ursprungsland VARCHAR(50);
ALTER TABLE flaschen ADD COLUMN kaufdatum DATE;
ALTER TABLE flaschen ADD COLUMN garantie_bis DATE;
ALTER TABLE flaschen ADD COLUMN externe_referenzen TEXT;

-- 3. Indizes für Performance erstellen
CREATE INDEX IF NOT EXISTS idx_flaschen_barcode_typ ON flaschen(barcode, barcode_typ);
CREATE INDEX IF NOT EXISTS idx_flaschen_pruefung_status ON flaschen(naechste_pruefung, pruefung_benachrichtigt);

-- 4. Bestehende Flaschen aktualisieren
UPDATE flaschen 
SET interne_flaschennummer_auto = TRUE,
    barcode_typ = 'CODE128'
WHERE interne_flaschennummer_auto IS NULL;

-- 5. Validierung
SELECT COUNT(*) as total_flaschen FROM flaschen;
PRAGMA table_info(flaschen);

-- FERTIG: Die Datenbank ist nun für erweiterte Rückverfolgbarkeit bereit!
