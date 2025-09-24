# SQLAlchemy Model für Benutzer-Verwaltung
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """
    Model für Benutzer-Verwaltung
    
    Erfasst:
    - Benutzer-Authentifizierung
    - Rollen und Berechtigungen
    - Login-Aktivitäten
    """
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Benutzer-Details
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Persönliche Informationen
    vorname = db.Column(db.String(50), nullable=True)
    nachname = db.Column(db.String(50), nullable=True)
    
    # Rollen und Berechtigungen
    role = db.Column(db.String(20), default='operator')  # operator, techniker, admin
    is_active = db.Column(db.Boolean, default=True)
    
    # Login-Tracking
    last_login = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
    def set_password(self, password):
        """Setzt gehashtes Passwort"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Prüft Passwort"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def vollname(self):
        """Gibt Vollname zurück"""
        if self.vorname and self.nachname:
            return f"{self.vorname} {self.nachname}"
        return self.username
    
    @property
    def kann_wartung(self):
        """Prüft ob Benutzer Wartungen durchführen kann"""
        return self.role in ['techniker', 'admin']
    
    @property
    def kann_admin(self):
        """Prüft ob Benutzer Admin-Rechte hat"""
        return self.role == 'admin'
    
    def login_registrieren(self):
        """Registriert erfolgreichen Login"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_aktive_benutzer():
        """Gibt alle aktiven Benutzer zurück"""
        return User.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_benutzer_by_role(role):
        """Gibt Benutzer nach Rolle zurück"""
        return User.query.filter_by(role=role, is_active=True).all()
    
    def to_dict(self, include_sensitive=False):
        """Konvertiert Model zu Dictionary (für JSON API)"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'vorname': self.vorname,
            'nachname': self.nachname,
            'vollname': self.vollname,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'kann_wartung': self.kann_wartung,
            'kann_admin': self.kann_admin
        }
        
        if include_sensitive:
            data['email'] = self.email
        
        return data

# Default Users für Initial Setup
def create_default_users():
    """Erstellt Standard-Benutzer falls nicht vorhanden"""
    
    # Admin User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@wartungsmanager.local',
            vorname='System',
            nachname='Administrator',
            role='admin'
        )
        admin.set_password('admin123')  # TODO: In Production ändern!
        db.session.add(admin)
    
    # Techniker User
    techniker = User.query.filter_by(username='techniker').first()
    if not techniker:
        techniker = User(
            username='techniker',
            email='techniker@wartungsmanager.local',
            vorname='Max',
            nachname='Techniker',
            role='techniker'
        )
        techniker.set_password('tech123')
        db.session.add(techniker)
    
    # Operator User
    operator = User.query.filter_by(username='operator').first()
    if not operator:
        operator = User(
            username='operator',
            email='operator@wartungsmanager.local',
            vorname='Maria',
            nachname='Operator',
            role='operator'
        )
        operator.set_password('op123')
        db.session.add(operator)
    
    db.session.commit()
    return {'admin': admin, 'techniker': techniker, 'operator': operator}
