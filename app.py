import os
from flask import Flask
from config import Config
from extensions import db, migrate
from datetime import date # Importa date para la fecha de tratamiento

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from models import Patient, Measurement, Alert, Settings # Importa los modelos aquí

    with app.app_context():
        db.create_all() # Asegura que las tablas existan

        # --- Añadir un paciente por defecto si no existe ninguno ---
        if Patient.query.count() == 0:
            print("No se encontraron pacientes. Creando un paciente por defecto...")
            default_patient = Patient(
                name="Paciente Demo",
                treatment_date=date(2025, 1, 15), # Ejemplo de fecha
                iodine_dose=120.0 # Ejemplo de dosis
            )
            db.session.add(default_patient)
            db.session.commit()
            print(f"Paciente por defecto '{default_patient.name}' creado con ID: {default_patient.id}")
            # Opcional: Añadir algunas mediciones iniciales para el paciente por defecto
            # from models import Measurement
            # from datetime import datetime, timedelta
            # if Measurement.query.count() == 0:
            #     print("No se encontraron mediciones. Creando mediciones por defecto...")
            #     for i in range(5):
            #         measurement = Measurement(
            #             cpm=50.0 + i * 2, # Ejemplo de CPM
            #             timestamp=datetime.utcnow() - timedelta(minutes=(5-i)),
            #             patient_id=default_patient.id
            #         )
            #         db.session.add(measurement)
            #     db.session.commit()
            #     print("Mediciones por defecto creadas.")
        # -----------------------------------------------------------

    from routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)
    print("Blueprint 'main' registrado con la aplicación.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
