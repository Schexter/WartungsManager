"""
Einfache Route für Admin-Zugang
Ergänzt die bestehenden Routes um einen direkten Admin-Zugang
"""

from flask import Blueprint, render_template

# Blueprint für einfachen Admin-Zugang
simple_admin_bp = Blueprint('simple_admin', __name__)

@simple_admin_bp.route('/admin-access')
def admin_access():
    """Einfache Admin-Access-Seite"""
    return """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>WartungsManager - Admin-Zugang</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c5aa0; text-align: center; }
        .admin-links { display: grid; gap: 15px; margin-top: 30px; }
        .admin-link { display: block; padding: 15px; background: #3498db; color: white; text-decoration: none; text-align: center; border-radius: 5px; font-size: 16px; }
        .admin-link:hover { background: #2980b9; color: white; text-decoration: none; }
        .status { background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0; }
        .shelly-config { background: #f0f8f0; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 WartungsManager Admin-Zugang</h1>
        
        <div class="status">
            <h3>System-Status</h3>
            <p>✅ <strong>Server läuft:</strong> http://localhost:5000</p>
            <p>✅ <strong>Admin-Interface:</strong> Aktiviert</p>
            <p>✅ <strong>Shelly-API:</strong> Verfügbar</p>
            <p>⚠️ <strong>Shelly:</strong> Noch nicht konfiguriert</p>
        </div>
        
        <div class="shelly-config">
            <h3>🔌 Shelly-Kompressor-Steuerung</h3>
            <p><strong>Universelle Lösung für alle Shelly-Modelle:</strong></p>
            <ul>
                <li>Shelly 1 (Basis-Relais)</li>
                <li>Shelly 1PM (mit Leistungsmessung)</li>
                <li>Shelly Plus 1 (Gen2)</li>
                <li>Shelly Plus 1PM (Gen2 + Leistung)</li>
            </ul>
            <p><strong>Setup in 3 Schritten:</strong></p>
            <ol>
                <li>IP-Adresse des Shelly herausfinden</li>
                <li>Shelly-Modell auswählen</li>
                <li>Verbindung testen und speichern</li>
            </ol>
        </div>
        
        <div class="admin-links">
            <a href="/admin" class="admin-link">🎛️ Admin Dashboard</a>
            <a href="/api/shelly/config" class="admin-link">⚙️ Shelly-Konfiguration (JSON)</a>
            <a href="/" class="admin-link">🏠 Zurück zum WartungsManager</a>
        </div>
        
        <div class="status">
            <h3>Shelly-Konfiguration per API</h3>
            <p><strong>IP-Adresse setzen:</strong></p>
            <code>POST /api/shelly/config<br>
            {"ip_address": "192.168.1.100", "model": "Shelly1PM", "enabled": true}
            </code>
            
            <p><strong>Kompressor einschalten:</strong></p>
            <code>POST /api/shelly/kompressor/einschalten</code>
            
            <p><strong>Status abfragen:</strong></p>
            <code>GET /api/shelly/kompressor/status</code>
        </div>
    </div>
    
    <script>
        // Status alle 10 Sekunden aktualisieren
        setInterval(async () => {
            try {
                const response = await fetch('/api/shelly/config');
                const data = await response.json();
                
                if (data.success && data.config.enabled) {
                    document.querySelector('.status p:last-child').innerHTML = 
                        '✅ <strong>Shelly:</strong> Konfiguriert (' + data.config.model + ' - ' + data.config.ip_address + ')';
                }
            } catch (error) {
                console.log('Shelly-Status nicht verfügbar');
            }
        }, 10000);
    </script>
</body>
</html>"""

@simple_admin_bp.route('/shelly-quick-setup')
def shelly_quick_setup():
    """Schnelle Shelly-Einrichtung"""
    return """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>Shelly-Schnellsetup</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        input, select, button { width: 100%; padding: 10px; margin: 5px 0; border-radius: 4px; border: 1px solid #ddd; }
        button { background: #3498db; color: white; cursor: pointer; font-size: 16px; }
        button:hover { background: #2980b9; }
        .result { margin: 15px 0; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔌 Shelly-Schnellsetup</h2>
        
        <label>IP-Adresse:</label>
        <input type="text" id="ip" placeholder="192.168.1.100" value="192.168.1.100">
        
        <label>Shelly-Modell:</label>
        <select id="model">
            <option value="Shelly1">Shelly 1 (Basis)</option>
            <option value="Shelly1PM" selected>Shelly 1PM (+ Leistung)</option>
            <option value="ShellyPlus1">Shelly Plus 1 (Gen2)</option>
            <option value="ShellyPlus1PM">Shelly Plus 1PM (Gen2 + Leistung)</option>
        </select>
        
        <button onclick="testConnection()">Verbindung testen</button>
        <button onclick="saveConfig()">Konfiguration speichern</button>
        
        <div id="result"></div>
        
        <hr>
        <h3>Kompressor-Steuerung</h3>
        <button onclick="turnOn()">Kompressor EINSCHALTEN</button>
        <button onclick="turnOff()">Kompressor AUSSCHALTEN</button>
        <button onclick="getStatus()">Status abfragen</button>
    </div>
    
    <script>
        const resultDiv = document.getElementById('result');
        
        function showResult(message, isSuccess) {
            resultDiv.className = 'result ' + (isSuccess ? 'success' : 'error');
            resultDiv.innerHTML = message;
        }
        
        async function testConnection() {
            const ip = document.getElementById('ip').value;
            const model = document.getElementById('model').value;
            
            try {
                const response = await fetch('/api/shelly/test-connection', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ip_address: ip, model: model})
                });
                
                const result = await response.json();
                showResult(
                    result.success ? '✅ Verbindung erfolgreich!' : '❌ ' + result.error,
                    result.success
                );
            } catch (error) {
                showResult('❌ Test fehlgeschlagen: ' + error.message, false);
            }
        }
        
        async function saveConfig() {
            const config = {
                enabled: true,
                ip_address: document.getElementById('ip').value,
                model: document.getElementById('model').value
            };
            
            try {
                const response = await fetch('/api/shelly/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(config)
                });
                
                const result = await response.json();
                showResult(
                    result.success ? '✅ Konfiguration gespeichert!' : '❌ ' + result.error,
                    result.success
                );
            } catch (error) {
                showResult('❌ Speichern fehlgeschlagen: ' + error.message, false);
            }
        }
        
        async function turnOn() {
            try {
                const response = await fetch('/api/shelly/kompressor/einschalten', {method: 'POST'});
                const result = await response.json();
                showResult(
                    result.success ? '✅ Kompressor eingeschaltet!' : '❌ ' + result.error,
                    result.success
                );
            } catch (error) {
                showResult('❌ Einschalten fehlgeschlagen: ' + error.message, false);
            }
        }
        
        async function turnOff() {
            try {
                const response = await fetch('/api/shelly/kompressor/ausschalten', {method: 'POST'});
                const result = await response.json();
                showResult(
                    result.success ? '✅ Kompressor ausgeschaltet!' : '❌ ' + result.error,
                    result.success
                );
            } catch (error) {
                showResult('❌ Ausschalten fehlgeschlagen: ' + error.message, false);
            }
        }
        
        async function getStatus() {
            try {
                const response = await fetch('/api/shelly/kompressor/status');
                const result = await response.json();
                
                if (result.success) {
                    const status = result.data;
                    showResult(
                        `📊 Status: ${status.online ? 'Online' : 'Offline'}<br>` +
                        `🔌 Relais: ${status.relay_on ? 'EIN' : 'AUS'}<br>` +
                        `⚡ Leistung: ${status.power || 0} W`,
                        true
                    );
                } else {
                    showResult('❌ Status-Fehler: ' + (result.error || 'Unbekannt'), false);
                }
            } catch (error) {
                showResult('❌ Status-Abfrage fehlgeschlagen: ' + error.message, false);
            }
        }
    </script>
</body>
</html>"""

# Erstellt von Hans Hahn - Alle Rechte vorbehalten
