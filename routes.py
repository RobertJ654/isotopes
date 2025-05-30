from flask import Blueprint, render_template, request, redirect, url_for, flash # Importa flash
from extensions import db
from models import Patient, Measurement, Alert, Settings
from datetime import datetime, timedelta
import csv
from io import StringIO
import pandas as pd

print("Módulo routes.py importado.")

bp = Blueprint('main', __name__)

@bp.route('/')
def dashboard():
    patient = Patient.query.first()
    if not patient:
        flash("No hay ningún paciente registrado. Por favor, registre uno.", "warning")
        return redirect(url_for('main.patient_info')) # Redirige a la página de información del paciente para que lo cree

    latest = Measurement.query.order_by(Measurement.timestamp.desc()).first()
    cpm = latest.cpm if latest else 0 # Asegura que cpm sea 0 si no hay mediciones
    status = 'normal' if cpm < 30 else 'moderate' if cpm < 80 else 'critical'
    status_icon = '✅' if status == 'normal' else '⚠️' if status == 'moderate' else '❌'

    # Solo crear alerta si el paciente existe y el CPM es crítico
    if patient and cpm >= 80:
        alert = Alert(level=status, cpm=cpm, timestamp=datetime.utcnow(),
                      message="Critical radiation level detected!", patient_id=patient.id)
        db.session.add(alert)
        db.session.commit()

    return render_template('dashboard.html', patient=patient, latest=latest, cpm=cpm,
                           status=status, status_icon=status_icon)

@bp.route('/patient')
def patient_info():
    patient = Patient.query.first()
    if not patient:
        # Si no hay paciente, puedes renderizar una plantilla para crear uno
        # O, si patient_info.html puede manejar un paciente None, pasa None.
        # Por simplicidad, aquí puedes crear un paciente de ejemplo o redirigir a una página de creación.
        # Para este ejemplo, vamos a pasar None y asegurarnos de que la plantilla lo maneje.
        # En una app real, aquí podrías renderizar un formulario para crear un paciente.
        flash("No hay ningún paciente registrado. Por favor, cree uno.", "info")
        return render_template('patient_info.html', patient=None, isolation_days=0) # Pasa 0 o N/A para isolation_days

    isolation_days = 7 if patient.iodine_dose < 100 else 14
    return render_template('patient_info.html', patient=patient, isolation_days=isolation_days)

@bp.route('/monitoring')
def monitoring():
    patient = Patient.query.first()
    if not patient:
        flash("No hay ningún paciente registrado para monitorear.", "warning")
        return redirect(url_for('main.patient_info'))

    measurements = Measurement.query.filter_by(patient_id=patient.id).order_by(Measurement.timestamp.desc()).limit(24).all()
    daily_avg = sum(m.cpm for m in measurements) / len(measurements) if measurements else 0
    return render_template('monitoring.html', measurements=measurements, daily_avg=daily_avg)

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    patient = Patient.query.first()
    if not patient:
        flash("No hay ningún paciente registrado para configurar.", "warning")
        return redirect(url_for('main.patient_info'))

    settings = Settings.query.filter_by(patient_id=patient.id).first()
    if not settings:
        # Si no hay configuración para este paciente, crea una por defecto
        settings = Settings(patient_id=patient.id)
        db.session.add(settings)
        db.session.commit()
        flash("Configuración por defecto creada para el paciente.", "info")

    if request.method == 'POST':
        settings.wifi_ssid = request.form['ssid']
        settings.wifi_password = request.form['password']
        settings.alert_threshold_moderate = float(request.form['moderate'])
        settings.alert_threshold_critical = float(request.form['critical'])
        settings.notifications_enabled = 'notifications' in request.form
        settings.notification_type = request.form['notification_type']
        settings.measurement_frequency = int(request.form['frequency'])
        db.session.commit()
        flash("Configuración guardada exitosamente.", "success")
        return redirect(url_for('main.settings'))
    return render_template('settings.html', settings=settings)

@bp.route('/alerts')
def alerts():
    patient = Patient.query.first()
    if not patient:
        flash("No hay ningún paciente registrado para ver alertas.", "warning")
        return redirect(url_for('main.patient_info'))

    alerts = Alert.query.filter_by(patient_id=patient.id).order_by(Alert.timestamp.desc()).all()
    recommendations = [
        "Increase distance from family members.",
        "Improve room ventilation.",
        "Consult your doctor if levels remain elevated."
    ] if alerts and alerts[0].level == 'critical' else []
    return render_template('alerts.html', alerts=alerts, recommendations=recommendations)

@bp.route('/register_analysis')
def register_analysis():
    patient = Patient.query.first()
    if not patient:
        flash("No hay ningún paciente registrado para análisis.", "warning")
        return redirect(url_for('main.patient_info'))

    measurements = Measurement.query.filter_by(patient_id=patient.id).order_by(Measurement.timestamp).all()
    return render_template('register_analysis.html', measurements=measurements)

@bp.route('/export/csv')
def export_csv():
    patient = Patient.query.first()
    if not patient:
        flash("No hay ningún paciente registrado para exportar datos.", "warning")
        return redirect(url_for('main.patient_info'))

    measurements = Measurement.query.filter_by(patient_id=patient.id).all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Timestamp', 'CPM'])
    for m in measurements:
        writer.writerow([m.timestamp, m.cpm])
    output = si.getvalue()
    si.close()
    return send_file(
        StringIO(output),
        mimetype='text/csv',
        as_attachment=True,
        download_name='radiation_data.csv'
    )

@bp.route('/data', methods=['POST'])
def receive_data():
    patient = Patient.query.first()
    if not patient:
        # Si no hay paciente, no podemos asociar la medición.
        # Podrías loggear un error o devolver un estado HTTP diferente.
        return 'Error: No patient registered to receive data.', 400

    cpm = float(request.form['cpm'])
    measurement = Measurement(cpm=cpm, patient_id=patient.id)
    patient.cumulative_exposure += cpm
    db.session.add(measurement)
    db.session.commit()
    return 'Data received', 200
