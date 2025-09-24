# WartungsManager - Python-Anwendung

Dieses Verzeichnis enthält die Python-basierte Flask-Anwendung für den WartungsManager.

## Inbetriebnahme

### 1. Abhängigkeiten installieren

Stellen Sie sicher, dass alle erforderlichen Pakete installiert sind. Führen Sie dazu den folgenden Befehl im Hauptverzeichnis des Projekts aus:

```bash
pip install -r Source/Python/requirements.txt
```

### 2. Datenbank initialisieren

Bevor Sie die Anwendung zum ersten Mal starten, muss die Datenbank initialisiert werden. Dies erstellt die notwendigen Tabellen und legt Standardbenutzer an.

```bash
flask --app Source.Python.run:app init-db
```
*Hinweis: Der `flask`-Befehl erfordert, dass das `Flask`-Paket in Ihrer Umgebung installiert ist.*

### 3. Anwendung starten

Nach der Initialisierung können Sie den Entwicklungsserver starten:

```bash
python Source/Python/run.py
```

Die Anwendung ist nun unter den folgenden Adressen erreichbar:
*   **Lokal:** [http://localhost:5000](http://localhost:5000)
*   **Im Netzwerk:** `http://<IHRE-LOKALE-IP-ADRESSE>:5000`

### Standard-Logins

*   **Admin:** `admin` / `admin123`
*   **Techniker:** `techniker` / `tech123`
*   **Operator:** `operator` / `op123`

**WICHTIG:** Ändern Sie diese Standardpasswörter in einer Produktivumgebung!