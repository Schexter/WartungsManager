# 🐍 TECHNOLOGIE-ENTSCHEIDUNG: Python Web-Stack

## ✅ **FINALER TECHNOLOGIE-STACK**

### **Backend Framework**
- **Python 3.11** (Modern, stabil, excellent Performance)
- **Flask** oder **FastAPI** (Web-Framework Empfehlung)
- **SQLite** (Datenbank - perfekt für Start)
- **SQLAlchemy** (ORM für typsichere DB-Zugriffe)

### **Frontend Stack**
- **HTML5** (Semantic Markup)
- **CSS3** mit **Flexbox/Grid** (Touch-optimiert)
- **JavaScript (ES6+)** (Interaktivität)
- **Bootstrap 5** oder **Tailwind CSS** (Touch-friendly Components)

### **Touch-Optimierung**
- **Große Buttons** (min. 44px x 44px für Touch)
- **Responsive Design** (Mobile-First Approach)
- **Touch Gestures** (Swipe, Tap, Long-Press)
- **Visual Feedback** (Button States, Ripple Effects)

## 🏗️ **PYTHON PROJEKT-STRUKTUR**

```
WartungsManager/
├── app/
│   ├── __init__.py
│   ├── models/           # SQLAlchemy Models
│   ├── routes/           # Flask Routes/Endpoints
│   ├── services/         # Business Logic
│   ├── static/          # CSS, JS, Images
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/        # Jinja2 HTML Templates
│   └── utils/           # Helper Functions
├── database/
│   ├── migrations/      # DB Schema Changes
│   ├── seeddata/        # Initial Data
│   └── wartung.db      # SQLite Database File
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/
│   ├── development.py
│   ├── production.py
│   └── config.py
├── requirements.txt     # Python Dependencies
├── run.py              # Application Entry Point
└── wsgi.py            # Production WSGI
```

## 📱 **TOUCH-UI ANFORDERUNGEN**

### Button-Design:
- **Mindestgröße:** 44px x 44px (Apple), 48dp (Google)
- **Abstand:** Min. 8px zwischen Touch-Elementen
- **Visual States:** Normal, Hover, Active, Disabled
- **Feedback:** Haptic/Visual bei Touch

### Responsive Breakpoints:
- **Mobile:** 320px - 768px (Phone)
- **Tablet:** 768px - 1024px (iPad/Android Tablet)
- **Desktop:** 1024px+ (Monitor/Touch-Screen)

## 🚀 **PYTHON FRAMEWORK EMPFEHLUNG**

### **Option A: Flask (Empfohlen für Einfachheit)**
```python
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wartung.db'
db = SQLAlchemy(app)
```

### **Option B: FastAPI (Modern, API-First)**
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")
```

## 🔧 **DEVELOPMENT SETUP**

### Python Environment:
```bash
# Virtual Environment erstellen
python -m venv venv
venv\Scripts\activate  # Windows

# Dependencies installieren
pip install flask flask-sqlalchemy
pip install flask-migrate flask-wtf
pip install python-dotenv
```

### Empfohlene Libraries:
- **Flask-SQLAlchemy:** Database ORM
- **Flask-Migrate:** Database Migrations
- **Flask-WTF:** Forms & CSRF Protection
- **Jinja2:** Template Engine
- **python-dotenv:** Environment Variables
- **Werkzeug:** WSGI Utilities

## 📱 **TOUCH-OPTIMIERTE UI KOMPONENTEN**

### Haupt-Interface Layout:
```html
<!-- Große Touch-Buttons -->
<div class="touch-button-grid">
    <button class="btn-touch btn-start" onclick="startFuelling()">
        🟢 START FÜLLUNG
    </button>
    <button class="btn-touch btn-stop" onclick="stopFuelling()">
        🔴 STOP FÜLLUNG
    </button>
</div>

<!-- Status Display -->
<div class="status-display">
    <div class="timer-large">02:30:45</div>
    <div class="total-hours">Gesamt: 1.247h</div>
</div>
```

### CSS Touch-Optimierung:
```css
.btn-touch {
    min-height: 60px;
    min-width: 120px;
    font-size: 18px;
    border-radius: 12px;
    margin: 8px;
    transition: all 0.2s ease;
}

.btn-touch:active {
    transform: scale(0.95);
    background-color: #007bff;
}

/* Touch-friendly hover states */
@media (hover: hover) {
    .btn-touch:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
}
```

## 🌐 **NETZWERK KONFIGURATION**

### Flask Development Server:
```python
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',      # Alle Interfaces
        port=5000,           # Standard Port
        debug=True           # Development Mode
    )
```

### Production mit Gunicorn:
```bash
gunicorn --bind 192.168.1.100:5000 --workers 4 wsgi:app
```

## 📊 **DATENBANK SCHEMA (SQLite)**

### Models Beispiel:
```python
class Fuellvorgang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_zeit = db.Column(db.DateTime, nullable=False)
    end_zeit = db.Column(db.DateTime)
    operator = db.Column(db.String(100), nullable=False)
    dauer_minuten = db.Column(db.Integer)
    
class Wartung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    typ = db.Column(db.String(50), nullable=False)  # Filter, Öl
    datum = db.Column(db.DateTime, nullable=False)
    durchgefuehrt_von = db.Column(db.String(100))
    naechste_faellig = db.Column(db.DateTime)
```

## 🎨 **UI DESIGN PRINZIPIEN**

### Touch-First Design:
1. **Finger-freundlich:** Große Buttons, gute Abstände
2. **Visuelles Feedback:** Hover, Active, Focus States
3. **Einfache Navigation:** Klare Hierarchie, große Texte
4. **Fehlertoleranz:** Undo-Funktionen, Bestätigungen
5. **Offline-fähig:** Local Storage für kritische Daten

### Color Scheme (Touch-optimiert):
- **Primary:** #007bff (Touch-safe Blue)
- **Success:** #28a745 (Start-Button)
- **Danger:** #dc3545 (Stop-Button)
- **Warning:** #ffc107 (Wartung fällig)
- **Background:** #f8f9fa (High Contrast)

---

**Nächste Schritte:**
1. ✅ Python 3.11 Installation prüfen
2. ✅ Virtual Environment erstellen
3. ✅ Flask Projekt-Struktur anlegen
4. ✅ SQLite Datenbank initialisieren
5. ✅ Touch-optimierte HTML Templates erstellen
