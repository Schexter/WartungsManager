"""
Füllmanager Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, BooleanField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Optional


class FuellmanagerForm(FlaskForm):
    """Form für Füllmanager Annahme"""
    kunde_id = SelectField('Kunde', coerce=int, validators=[DataRequired()])
    flasche_id = SelectField('Flasche', coerce=int, validators=[DataRequired()])
    
    # Prüfung
    visuelle_pruefung = BooleanField('Visuelle Prüfung durchgeführt')
    tuev_geprueft = BooleanField('TÜV-Prüfung gültig')
    ventil_zustand = SelectField('Ventilzustand', 
                                choices=[('OK', 'OK'), ('Wartung', 'Wartung erforderlich'), ('Defekt', 'Defekt')],
                                default='OK')
    annahme_notizen = TextAreaField('Anmerkungen', validators=[Optional()])
    
    # Füllparameter
    restdruck_bar = FloatField('Restdruck (bar)', 
                              validators=[DataRequired(), NumberRange(min=0, max=300)],
                              default=0)
    zieldruck_bar = FloatField('Zieldruck (bar)', 
                              validators=[DataRequired(), NumberRange(min=0, max=300)],
                              default=220)
    
    # Gasgemisch
    sauerstoff_prozent = FloatField('Sauerstoff (%)', 
                                   validators=[DataRequired(), NumberRange(min=0, max=100)],
                                   default=21)
    helium_prozent = FloatField('Helium (%)', 
                               validators=[DataRequired(), NumberRange(min=0, max=100)],
                               default=0)
    stickstoff_prozent = FloatField('Stickstoff (%)', 
                                   validators=[DataRequired(), NumberRange(min=0, max=100)],
                                   default=79)
