from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from extensions import db
from models import Patient, Measurement, Alert, Settings
from datetime import datetime, timedelta, date # Importa date para la creación de pacientes
import csv
from io import StringIO
import pandas as pd

print("Módulo routes.py importado.")

def register_routes(bp):
    """
    Registra todas las rutas en el Blueprint proporcionado.
    """
    @bp.route('/')
    def dashboard():
        patient = Patient.query.first()
        if not patient:
            flash("No hay ningún paciente registrado. ¡Crea uno para empezar!", "info")
            return redirect(url_for('main.add_patient'))

        latest = Measurement.query.filter_by(patient_id=patient.id).order_by(Measurement.timestamp.desc()).first()
        cpm = latest.cpm if latest else 0
        
        # Obtener umbrales de configuración o usar valores por defecto
        settings = Settings.query.filter_by(patient_id=patient.id).first()
        moderate_threshold = settings.alert_threshold_moderate if settings else 30.0
        critical_threshold = settings.alert_threshold_critical if settings else 80.0

        status = 'normal'
        status_icon = '✅'
        if cpm >= critical_threshold:
            status = 'critical'
            status_icon = '❌'
        elif cpm >= moderate_threshold:
            status = 'moderate'
            status_icon = '⚠️'

        # Lógica para crear alertas si el CPM es crítico (evitando duplicados)
        if patient and cpm >= critical_threshold:
            # Comprueba si ya existe una alerta crítica reciente (ej. en los últimos 5 minutos)
            last_alert = Alert.query.filter_by(patient_id=patient.id, level='critical').order_by(Alert.timestamp.desc()).first()
            if not last_alert or (datetime.utcnow() - last_alert.timestamp).total_seconds() > 300: # Alerta cada 5 minutos
                alert = Alert(level=status, cpm=cpm, timestamp=datetime.utcnow(),
                              message="¡Nivel de radiación crítico detectado!", patient_id=patient.id)
                db.session.add(alert)
                db.session.commit()
                flash("¡Alerta crítica registrada! Por favor, revisa la sección de Alertas.", "danger")
        elif patient and cpm >= moderate_threshold: # También alertar si es moderado
            last_alert = Alert.query.filter_by(patient_id=patient.id, level='moderate').order_by(Alert.timestamp.desc()).first()
            if not last_alert or (datetime.utcnow() - last_alert.timestamp).total_seconds() > 300: # Alerta cada 5 minutos
                alert = Alert(level=status, cpm=cpm, timestamp=datetime.utcnow(),
                              message="Nivel de radiación moderado detectado.", patient_id=patient.id)
                db.session.add(alert)
                db.session.commit()
                flash("Alerta moderada registrada. Monitoree de cerca.", "warning")


        # Obtener las últimas X mediciones para el gráfico de tendencias del dashboard
        # Ajusta el límite según la densidad de datos que quieras mostrar
        measurements_for_chart = Measurement.query.filter_by(patient_id=patient.id).order_by(Measurement.timestamp.desc()).limit(30).all()
        measurements_for_chart.reverse() # Para que el gráfico empiece con el dato más antiguo a la izquierda

        return render_template('dashboard.html', patient=patient, latest=latest, cpm=cpm,
                               status=status, status_icon=status_icon, 
                               measurements=measurements_for_chart, # Pasa las mediciones para el gráfico
                               moderate_threshold=moderate_threshold,
                               critical_threshold=critical_threshold)


    @bp.route('/patient')
    def patient_info():
        patient = Patient.query.first() # Asumiendo que siempre trabajamos con el primer paciente
        if not patient:
            flash("No hay ningún paciente registrado. Por favor, crea uno para ver su información.", "info")
            return redirect(url_for('main.add_patient'))
        
        isolation_days = 7 if patient.iodine_dose < 100 else 14
        return render_template('patient_info.html', patient=patient, isolation_days=isolation_days)

    @bp.route('/patients') # Nueva ruta para listar todos los pacientes
    def list_patients():
        patients = Patient.query.all()
        if not patients:
            flash("No hay pacientes registrados aún.", "info")
            return redirect(url_for('main.add_patient')) # Redirige a añadir si no hay ninguno
        return render_template('patients.html', patients=patients)


    @bp.route('/monitoring')
    def monitoring():
        patient = Patient.query.first()
        if not patient:
            flash("No hay ningún paciente registrado para monitorear.", "warning")
            return redirect(url_for('main.add_patient'))

        # Obtener todas las mediciones para la tabla
        all_measurements = Measurement.query.filter_by(patient_id=patient.id).order_by(Measurement.timestamp.desc()).all()
        
        # Calcular promedio diario con mediciones de las últimas 24 horas
        one_day_ago = datetime.utcnow() - timedelta(hours=24)
        recent_measurements = Measurement.query.filter_by(patient_id=patient.id).filter(Measurement.timestamp >= one_day_ago).all()
        daily_avg = sum(m.cpm for m in recent_measurements) / len(recent_measurements) if recent_measurements else 0
        
        # Asegúrate de que las mediciones para el gráfico estén en orden cronológico
        measurements_for_chart = Measurement.query.filter_by(patient_id=patient.id).order_by(Measurement.timestamp).limit(100).all()


        return render_template('monitoring.html', 
                               patient=patient, # Pasa el paciente para el encabezado
                               measurements=all_measurements, # Para la tabla
                               daily_avg=daily_avg, 
                               measurements_for_chart=measurements_for_chart) # Para el gráfico

    @bp.route('/settings', methods=['GET', 'POST'])
    def settings():
        patient = Patient.query.first()
        if not patient:
            flash("No hay ningún paciente registrado para configurar.", "warning")
            return redirect(url_for('main.add_patient'))

        settings = Settings.query.filter_by(patient_id=patient.id).first()
        if not settings:
            # Crea una configuración por defecto si no existe
            settings = Settings(patient_id=patient.id)
            db.session.add(settings)
            db.session.commit()
            flash("Configuración por defecto creada para el paciente.", "info")

        if request.method == 'POST':
            settings.wifi_ssid = request.form.get('ssid', '')
            settings.wifi_password = request.form.get('password', '')
            
            settings.alert_threshold_moderate = float(request.form.get('moderate', 30.0))
            settings.alert_threshold_critical = float(request.form.get('critical', 80.0))
            settings.notifications_enabled = 'notifications' in request.form
            settings.notification_type = request.form.get('notification_type', 'Email')
            settings.measurement_frequency = int(request.form.get('frequency', 60))
            
            db.session.commit()
            flash("Configuración guardada exitosamente.", "success")
            return redirect(url_for('main.settings'))
        return render_template('settings.html', patient=patient, settings=settings) # Pasa el paciente

    @bp.route('/alerts')
    def alerts():
        patient = Patient.query.first()
        if not patient:
            flash("No hay ningún paciente registrado para ver alertas.", "warning")
            return redirect(url_for('main.add_patient'))

        alerts = Alert.query.filter_by(patient_id=patient.id).order_by(Alert.timestamp.desc()).all()
        
        recommendations = []
        if alerts and alerts[0].level == 'critical':
            recommendations = [
                "Aumente la distancia con los miembros de la familia, especialmente niños y embarazadas.",
                "Mejore la ventilación de la habitación abriendo ventanas.",
                "Limite el tiempo en espacios públicos y evite aglomeraciones.",
                "Consulte a su médico si los niveles de radiación permanecen elevados."
            ]
        elif alerts and alerts[0].level == 'moderate':
             recommendations = [
                "Mantenga una buena higiene personal (lavado de manos frecuente).",
                "Evite compartir utensilios de cocina o artículos de tocador.",
                "Monitoree los niveles de radiación con más frecuencia."
            ]

        return render_template('alerts.html', patient=patient, alerts=alerts, recommendations=recommendations)

    @bp.route('/register_analysis')
    def register_analysis():
        patient = Patient.query.first()
        if not patient:
            flash("No hay ningún paciente registrado para análisis.", "warning")
            return redirect(url_for('main.add_patient'))

        measurements = Measurement.query.filter_by(patient_id=patient.id).order_by(Measurement.timestamp).all()
        return render_template('register_analysis.html', patient=patient, measurements=measurements)

    @bp.route('/export/csv')
    def export_csv():
        patient = Patient.query.first()
        if not patient:
            flash("No hay ningún paciente registrado para exportar datos.", "warning")
            return redirect(url_for('main.add_patient'))

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
            return 'Error: No patient registered to receive data.', 400

        try:
            cpm = float(request.form['cpm'])
            measurement = Measurement(cpm=cpm, timestamp=datetime.utcnow(), patient_id=patient.id)
            patient.cumulative_exposure += cpm
            db.session.add(measurement)
            db.session.commit()
            return 'Data received', 200
        except KeyError:
            return 'Error: Missing CPM data.', 400
        except ValueError:
            return 'Error: Invalid CPM value.', 400

    @bp.route('/add_patient', methods=['GET', 'POST'])
    def add_patient():
        if request.method == 'POST':
            name = request.form.get('name')
            treatment_date_str = request.form.get('treatment_date')
            iodine_dose = request.form.get('iodine_dose')

            if not name or not treatment_date_str or not iodine_dose:
                flash("Todos los campos son obligatorios.", "error")
                return render_template('add_patient.html')

            try:
                treatment_date = datetime.strptime(treatment_date_str, '%Y-%m-%d').date()
                iodine_dose = float(iodine_dose)
            except ValueError:
                flash("Formato de fecha inválido (AAAA-MM-DD) o dosis de yodo no válida.", "error")
                return render_template('add_patient.html')
            
            # Si quieres permitir múltiples pacientes, ¡necesitas una interfaz para seleccionarlos!
            # Por ahora, si ya hay un paciente, se asume que este es el principal.
            # Si quieres que solo haya un paciente, podrías borrar el anterior o actualizarlo.
            # Para este ejemplo, simplemente añadiremos uno nuevo.
            
            new_patient = Patient(name=name, treatment_date=treatment_date, iodine_dose=iodine_dose, cumulative_exposure=0.0)
            db.session.add(new_patient)
            db.session.commit()

            # Asegúrate de crear una configuración por defecto para el nuevo paciente si no existe
            settings = Settings.query.filter_by(patient_id=new_patient.id).first()
            if not settings:
                default_settings = Settings(patient_id=new_patient.id)
                db.session.add(default_settings)
                db.session.commit()

            flash(f"Paciente '{name}' agregado exitosamente.", "success")
            return redirect(url_for('main.patient_info')) # Redirige a la información del paciente
        return render_template('add_patient.html')
