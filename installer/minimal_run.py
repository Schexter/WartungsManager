#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARTUNGSMANAGER - MINIMAL FUNKTIONSFÄHIGE VERSION
Bombensichere Flask-Anwendung für Kassensystem
"""

from flask import Flask, render_template_string, request, jsonify
import sqlite3
import os
from datetime import datetime
import json

# Flask-App initialisieren
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Magicfactory15!_BOMBENSICHER_2025'

# Datenbank-Pfad
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'wartungsmanager.db')

def init_database():
    """Initialisiert die SQLite-Datenbank mit grundlegenden Tabellen"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Grundlegende Tabellen erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kompressor_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            is_running BOOLEAN DEFAULT FALSE,
            start_time DATETIME,
            stop_time DATETIME,
            total_hours REAL DEFAULT 0.0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wartung_protokoll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum DATETIME DEFAULT CURRENT_TIMESTAMP,
            typ TEXT NOT NULL,
            beschreibung TEXT,
            benutzer TEXT DEFAULT 'System',
            betriebsstunden REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patronenwechsel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum DATETIME DEFAULT CURRENT_TIMESTAMP,
            chargen_nr TEXT,
            betriebsstunden REAL,
            benutzer TEXT DEFAULT 'System'
        )
    ''')
    
    # Initialer Status einfügen falls leer
    cursor.execute('SELECT COUNT(*) FROM kompressor_status')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO kompressor_status (is_running, total_hours) 
            VALUES (FALSE, 0.0)
        ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Erstellt Datenbankverbindung"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# HTML-Template für die Hauptseite
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 Wartungsmanager - Kassensystem</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .touch-btn { min-height: 60px; font-size: 1.2rem; margin: 10px 0; }
        .status-card { border-left: 5px solid #28a745; }
        .running { border-left-color: #dc3545 !important; background-color: #ffe6e6; }
        .stopped { border-left-color: #28a745 !important; background-color: #e6ffe6; }
        .btn-large { padding: 15px 30px; font-size: 1.3rem; }
        body { background-color: #f8f9fa; padding-top: 20px; }
        .container { max-width: 1200px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">🔧 Wartungsmanager</h1>
                <p class="text-center text-muted">Kassensystem - Touch-optimierte Bedienung</p>
            </div>
        </div>

        <!-- Status-Karte -->
        <div class="row mb-4">
            <div class="col-md-8 mx-auto">
                <div class="card status-card {{ 'running' if status.is_running else 'stopped' }}">
                    <div class="card-body text-center">
                        <h3>
                            {% if status.is_running %}
                                🔴 Kompressor LÄUFT
                            {% else %}
                                🟢 Kompressor GESTOPPT
                            {% endif %}
                        </h3>
                        <p class="mb-2"><strong>Gesamte Betriebsstunden:</strong> {{ "%.1f"|format(status.total_hours) }} h</p>
                        <p class="mb-0"><small>Letztes Update: {{ status.last_updated }}</small></p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Steuerung -->
        <div class="row mb-4">
            <div class="col-md-6 mx-auto">
                <div class="d-grid gap-3">
                    {% if status.is_running %}
                        <button class="btn btn-danger btn-large touch-btn" onclick="stopKompressor()">
                            ⏹️ KOMPRESSOR STOPPEN
                        </button>
                    {% else %}
                        <button class="btn btn-success btn-large touch-btn" onclick="startKompressor()">
                            ▶️ KOMPRESSOR STARTEN
                        </button>
                    {% endif %}
                    
                    <button class="btn btn-warning btn-large touch-btn" onclick="addPatronenwechsel()">
                        🔄 PATRONENWECHSEL EINTRAGEN
                    </button>
                    
                    <button class="btn btn-info btn-large touch-btn" onclick="showProtokoll()">
                        📋 PROTOKOLL ANZEIGEN
                    </button>
                </div>
            </div>
        </div>

        <!-- Protokoll-Bereich -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>📋 Aktuelle Einträge</h5>
                    </div>
                    <div class="card-body">
                        <div id="protokoll-liste">
                            {% for entry in protokoll %}
                            <div class="border-bottom py-2">
                                <strong>{{ entry.datum }}</strong> - {{ entry.typ }}<br>
                                <small class="text-muted">{{ entry.beschreibung }}</small>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- System-Info -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6>ℹ️ System-Information</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <strong>🐍 Python:</strong> {{ python_version }}
                            </div>
                            <div class="col-md-4">
                                <strong>🌐 Flask:</strong> {{ flask_version }}
                            </div>
                            <div class="col-md-4">
                                <strong>💾 Datenbank:</strong> SQLite
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-md-6">
                                <strong>📡 Server:</strong> http://localhost:5000
                            </div>
                            <div class="col-md-6">
                                <strong>📱 Netzwerk:</strong> http://{{ request.host }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast für Benachrichtigungen -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div id="notification-toast" class="toast" role="alert">
            <div class="toast-body" id="toast-message">
                Nachricht
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showToast(message, type = 'success') {
            const toast = document.getElementById('notification-toast');
            const toastMessage = document.getElementById('toast-message');
            
            toast.className = `toast bg-${type === 'success' ? 'success' : 'danger'} text-white`;
            toastMessage.textContent = message;
            
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }

        function startKompressor() {
            fetch('/api/kompressor/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('Kompressor gestartet!');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showToast('Fehler beim Starten: ' + data.message, 'error');
                    }
                })
                .catch(error => showToast('Netzwerk-Fehler', 'error'));
        }

        function stopKompressor() {
            fetch('/api/kompressor/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('Kompressor gestoppt!');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showToast('Fehler beim Stoppen: ' + data.message, 'error');
                    }
                })
                .catch(error => showToast('Netzwerk-Fehler', 'error'));
        }

        function addPatronenwechsel() {
            const chargenNr = prompt('Chargen-Nummer eingeben:');
            if (chargenNr) {
                fetch('/api/patronenwechsel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ chargen_nr: chargenNr })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('Patronenwechsel eingetragen!');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showToast('Fehler: ' + data.message, 'error');
                    }
                })
                .catch(error => showToast('Netzwerk-Fehler', 'error'));
            }
        }

        function showProtokoll() {
            // Scrollen zum Protokoll-Bereich
            document.querySelector('.card').scrollIntoView({ behavior: 'smooth' });
        }

        // Auto-Refresh alle 30 Sekunden
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Status-Update ohne vollständiges Neuladen
                    console.log('Status aktualisiert:', data);
                });
        }, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Hauptseite"""
    try:
        conn = get_db_connection()
        
        # Aktueller Status
        status = conn.execute('SELECT * FROM kompressor_status ORDER BY id DESC LIMIT 1').fetchone()
        
        # Protokoll-Einträge (letzte 10)
        protokoll = conn.execute('''
            SELECT datum, typ, beschreibung, benutzer 
            FROM wartung_protokoll 
            ORDER BY datum DESC 
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        # System-Informationen
        import sys
        import flask
        
        return render_template_string(MAIN_TEMPLATE, 
            status=status,
            protokoll=protokoll,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            flask_version=flask.__version__
        )
        
    except Exception as e:
        return f"<h1>Datenbankfehler</h1><p>{str(e)}</p><p>Bitte Datenbank neu initialisieren.</p>", 500

@app.route('/api/status')
def api_status():
    """API: Aktueller Status"""
    try:
        conn = get_db_connection()
        status = conn.execute('SELECT * FROM kompressor_status ORDER BY id DESC LIMIT 1').fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'is_running': status['is_running'],
            'total_hours': status['total_hours'],
            'last_updated': status['last_updated']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/kompressor/start', methods=['POST'])
def api_start_kompressor():
    """API: Kompressor starten"""
    try:
        conn = get_db_connection()
        
        # Status auf "läuft" setzen
        conn.execute('''
            UPDATE kompressor_status 
            SET is_running = TRUE, start_time = ?, last_updated = ?
            WHERE id = (SELECT MAX(id) FROM kompressor_status)
        ''', (datetime.now(), datetime.now()))
        
        # Protokoll-Eintrag
        conn.execute('''
            INSERT INTO wartung_protokoll (typ, beschreibung, benutzer)
            VALUES (?, ?, ?)
        ''', ('Kompressor Start', 'Kompressor wurde gestartet', 'Web-Interface'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Kompressor gestartet'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/kompressor/stop', methods=['POST'])
def api_stop_kompressor():
    """API: Kompressor stoppen"""
    try:
        conn = get_db_connection()
        
        # Aktuellen Status holen
        status = conn.execute('SELECT * FROM kompressor_status ORDER BY id DESC LIMIT 1').fetchone()
        
        # Laufzeit berechnen falls gestartet
        runtime_hours = 0.0
        if status['is_running'] and status['start_time']:
            start = datetime.fromisoformat(status['start_time'])
            runtime_hours = (datetime.now() - start).total_seconds() / 3600
        
        # Status auf "gestoppt" setzen und Gesamtstunden aktualisieren
        new_total = status['total_hours'] + runtime_hours
        conn.execute('''
            UPDATE kompressor_status 
            SET is_running = FALSE, stop_time = ?, total_hours = ?, last_updated = ?
            WHERE id = (SELECT MAX(id) FROM kompressor_status)
        ''', (datetime.now(), new_total, datetime.now()))
        
        # Protokoll-Eintrag
        conn.execute('''
            INSERT INTO wartung_protokoll (typ, beschreibung, benutzer, betriebsstunden)
            VALUES (?, ?, ?, ?)
        ''', ('Kompressor Stop', f'Kompressor gestoppt. Laufzeit: {runtime_hours:.1f}h', 'Web-Interface', new_total))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Kompressor gestoppt. Laufzeit: {runtime_hours:.1f}h'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/patronenwechsel', methods=['POST'])
def api_patronenwechsel():
    """API: Patronenwechsel eintragen"""
    try:
        data = request.get_json()
        chargen_nr = data.get('chargen_nr', '')
        
        conn = get_db_connection()
        
        # Aktuelle Betriebsstunden holen
        status = conn.execute('SELECT total_hours FROM kompressor_status ORDER BY id DESC LIMIT 1').fetchone()
        betriebsstunden = status['total_hours'] if status else 0.0
        
        # Patronenwechsel eintragen
        conn.execute('''
            INSERT INTO patronenwechsel (chargen_nr, betriebsstunden, benutzer)
            VALUES (?, ?, ?)
        ''', (chargen_nr, betriebsstunden, 'Web-Interface'))
        
        # Protokoll-Eintrag
        conn.execute('''
            INSERT INTO wartung_protokoll (typ, beschreibung, benutzer, betriebsstunden)
            VALUES (?, ?, ?, ?)
        ''', ('Patronenwechsel', f'Patrone gewechselt. Chargen-Nr: {chargen_nr}', 'Web-Interface', betriebsstunden))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Patronenwechsel eingetragen: {chargen_nr}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/health')
def health_check():
    """Health-Check für Monitoring"""
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1').fetchone()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'ok'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    print("🔧 WARTUNGSMANAGER - INITIALISIERUNG")
    print("=" * 50)
    
    try:
        # Datenbank initialisieren
        print("💾 Initialisiere Datenbank...")
        init_database()
        print("✅ Datenbank bereit")
        
        # Server-Informationen
        print(f"🐍 Python: {os.sys.version.split()[0]}")
        
        import flask
        print(f"🌐 Flask: {flask.__version__}")
        print(f"💾 Datenbank: {DB_PATH}")
        print("=" * 50)
        print("🚀 STARTE WARTUNGSMANAGER...")
        print()
        print("📱 ZUGRIFFSMÖGLICHKEITEN:")
        print("   Lokal:    http://localhost:5000")
        print("   Netzwerk: http://[DIESE-IP]:5000")
        print()
        print("⏹️  STOPPEN: Strg+C")
        print("=" * 50)
        
        # Flask-Server starten
        app.run(
            host='0.0.0.0',  # Alle Interfaces
            port=5000,       # Standard-Port
            debug=False,     # Produktions-Modus
            threaded=True    # Multi-Threading
        )
        
    except Exception as e:
        print(f"❌ FEHLER BEIM STARTEN: {e}")
        print()
        print("TROUBLESHOOTING:")
        print("1. Python korrekt installiert?")
        print("2. Flask installiert? (pip install flask)")
        print("3. Port 5000 frei?")
        print("4. Firewall-Freigabe vorhanden?")
        input("\nDrücken Sie Enter zum Beenden...")
