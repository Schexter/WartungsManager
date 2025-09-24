# 🛠 KOMPRESSOR-PROBLEME BEHEBEN
# Schritt 1: Aktuellen aktiven Kompressor-Eintrag korrigieren
# Schritt 2: Wartungsintervall-System implementieren

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app import create_app, db
from app.models.kompressor import KompressorBetrieb
from app.services.wartungsintervall_service import WartungsintervallService

def fix_kompressor_timer():
    """Behebt den Timer-Bug (02:00:08 Problem)"""
    
    app = create_app()
    with app.app_context():
        print("🔍 Suche aktiven Kompressor...")
        
        aktiver_kompressor = KompressorBetrieb.get_aktiver_kompressor()
        
        if aktiver_kompressor:
            alte_startzeit = aktiver_kompressor.start_zeit
            aktuelle_zeit = datetime.utcnow()
            differenz = aktuelle_zeit - alte_startzeit
            stunden = differenz.total_seconds() / 3600
            
            print(f"✅ Aktiver Kompressor gefunden:")
            print(f"   ID: {aktiver_kompressor.id}")
            print(f"   Füller: {aktiver_kompressor.fueller}")
            print(f"   Alte Start-Zeit: {alte_startzeit}")
            print(f"   Laufzeit: {stunden:.2f} Stunden")
            
            antwort = input(f"\n🔧 Timer auf 00:00:00 setzen? (ja/nein): ").lower()
            
            if antwort in ['ja', 'j', 'yes', 'y']:
                # Start-Zeit auf jetzt setzen
                aktiver_kompressor.start_zeit = aktuelle_zeit
                aktiver_kompressor.notizen = aktiver_kompressor.notizen or ""
                aktiver_kompressor.notizen += f"\nTimer korrigiert: Alte Laufzeit {stunden:.2f}h gespeichert"
                
                db.session.commit()
                
                print("✅ Timer korrigiert! Kompressor startet jetzt bei 00:00:00")
                return True
            else:
                print("❌ Timer-Korrektur abgebrochen")
                return False
        else:
            print("ℹ️ Kein aktiver Kompressor gefunden - Timer ist bereits korrekt")
            return True

def check_total_hours():
    """Prüft und korrigiert die Gesamt-Betriebsstunden"""
    
    app = create_app()
    with app.app_context():
        print("📊 Prüfe Gesamt-Betriebsstunden...")
        
        # Aktuelle Berechnung
        gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
        print(f"   Berechnet aus DB: {gesamt_stunden}h")
        
        # Sollwert: 246h
        ziel_stunden = 246.0
        print(f"   Sollwert (Kompressor): {ziel_stunden}h")
        
        if abs(gesamt_stunden - ziel_stunden) > 1.0:  # Mehr als 1h Differenz
            print(f"⚠️ Differenz: {ziel_stunden - gesamt_stunden:.1f}h")
            
            antwort = input(f"🔧 Gesamt-Betriebszeit auf {ziel_stunden}h korrigieren? (ja/nein): ").lower()
            
            if antwort in ['ja', 'j', 'yes', 'y']:
                # Korrektur-Eintrag erstellen
                korrektur_minuten = (ziel_stunden - gesamt_stunden) * 60
                
                korrektur_eintrag = KompressorBetrieb(
                    fueller="SYSTEM",
                    start_zeit=datetime.utcnow() - timedelta(minutes=korrektur_minuten),
                    end_zeit=datetime.utcnow(),
                    betriebsdauer_minuten=int(korrektur_minuten),
                    status='beendet',
                    oel_getestet=False,
                    notizen=f"Korrektur-Eintrag: Gesamt-Betriebszeit auf {ziel_stunden}h korrigiert"
                )
                
                db.session.add(korrektur_eintrag)
                db.session.commit()
                
                print(f"✅ Gesamt-Betriebszeit korrigiert: {ziel_stunden}h")
                return True
            else:
                print("❌ Korrektur abgebrochen")
                return False
        else:
            print("✅ Gesamt-Betriebsstunden sind korrekt")
            return True

def setup_wartungsintervall_system():
    """Initialisiert das Wartungsintervall-System"""
    
    app = create_app()
    with app.app_context():
        print("🔧 Initialisiere Wartungsintervall-System...")
        
        # Aktuelle Gesamt-Betriebszeit
        gesamt_stunden = KompressorBetrieb.get_gesamt_betriebsstunden()
        print(f"   Gesamt-Betriebszeit: {gesamt_stunden}h")
        
        # Standard-Wartungsintervall erstellen falls nicht vorhanden
        result = WartungsintervallService.erstelle_standard_wartungsintervall(gesamt_stunden)
        
        if result['success']:
            print(f"✅ {result['message']}")
            if 'intervall' in result:
                intervall = result['intervall']
                print(f"   Wartungsintervall: alle {intervall['wartungsintervall_stunden']}h")
                print(f"   Nächste Wartung bei: {intervall['naechste_wartung_bei']}h")
            return True
        else:
            print(f"❌ Fehler: {result['error']}")
            return False

if __name__ == "__main__":
    print("🔧 KOMPRESSOR-REPARATUR TOOL")
    print("=" * 50)
    
    print("\n1. Timer-Bug beheben (02:00:08 → 00:00:00)")
    timer_ok = fix_kompressor_timer()
    
    print("\n2. Gesamt-Betriebsstunden prüfen (246h)")
    stunden_ok = check_total_hours()
    
    print("\n3. Wartungsintervall-System initialisieren")
    wartung_ok = setup_wartungsintervall_system()
    
    print("\n🎯 Reparatur abgeschlossen!")
    if timer_ok and stunden_ok and wartung_ok:
        print("   ✅ Alle Systeme erfolgreich repariert")
    else:
        print("   ⚠️ Einige Probleme konnten nicht behoben werden")
    
    print("   → Server neu starten empfohlen")
    print("   → Dashboard testen: Timer sollte bei 00:00:00 beginnen")
    print("   → Wartungsinterface: Wartungsintervall-Reset verfügbar")
