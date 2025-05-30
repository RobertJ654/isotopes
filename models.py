from extensions import db
from datetime import datetime

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    treatment_date = db.Column(db.Date, nullable=False)
    iodine_dose = db.Column(db.Float, nullable=False)   # in mCi
    cumulative_exposure = db.Column(db.Float, default=0.0) # Asegurado el valor por defecto

    # Relación con Mediciones y Alertas
    measurements = db.relationship('Measurement', backref='patient', lazy=True)
    alerts = db.relationship('Alert', backref='patient', lazy=True)
    settings = db.relationship('Settings', backref='patient', uselist=False, lazy=True) # Un paciente tiene una configuración

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpm = db.Column(db.Float, nullable=False)   # Counts per minute
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)   # 'normal', 'moderate', 'critical'
    cpm = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.String(200), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wifi_ssid = db.Column(db.String(50))
    wifi_password = db.Column(db.String(50))
    alert_threshold_moderate = db.Column(db.Float, default=30.0)
    alert_threshold_critical = db.Column(db.Float, default=80.0)
    notifications_enabled = db.Column(db.Boolean, default=True)
    notification_type = db.Column(db.String(50), default='email')   # 'email', 'sms', 'push'
    measurement_frequency = db.Column(db.Integer, default=5)   # in minutes
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True) # Un paciente solo tiene 1 entrada de configuración
