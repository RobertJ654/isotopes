import os
from flask import Flask, Blueprint
from config import Config
from extensions import db, migrate
from datetime import date, datetime

def create_app():
    """
    Función de fábrica para crear la instancia de la aplicación Flask.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from models import Patient, Measurement, Alert, Settings

    with app.app_context():
        db.create_all()

        # Crear un paciente por defecto si no existe ninguno
        if Patient.query.count() == 0:
            print("No se encontraron pacientes. Creando un paciente por defecto...")
            default_patient = Patient(
                name="Paciente Demo",
                treatment_date=date(2023, 1, 15), # Cambié el año para que las fechas de mediciones no sean futuras
                iodine_dose=120.0,
                cumulative_exposure=0.0
            )
            db.session.add(default_patient)
            db.session.commit()
            print(f"Paciente por defecto '{default_patient.name}' creado con ID: {default_patient.id}")

            # Opcional: Añadir algunas mediciones iniciales para el paciente por defecto
            if Measurement.query.count() == 0:
                print("No se encontraron mediciones. Creando mediciones por defecto...")
                for i in range(5):
                    measurement = Measurement(
                        cpm=25.0 + i * 5, # Ejemplo de CPM
                        timestamp=datetime.utcnow() - timedelta(hours=(5-i)),
                        patient_id=default_patient.id
                    )
                    db.session.add(measurement)
                db.session.commit()
                print("Mediciones por defecto creadas.")

    main_blueprint = Blueprint('main', __name__)
    print(f"Blueprint 'main' creado en {__name__}.")

    from routes import register_routes
    register_routes(main_blueprint)

    app.register_blueprint(main_blueprint)
    print("Blueprint 'main' registrado con la aplicación.")

    # Context processor para hacer 'datetime' disponible en todas las plantillas
    @app.context_processor
    def inject_datetime():
        return dict(datetime=datetime)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
