from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicializa las extensiones sin pasar la aplicación todavía.
# Se inicializarán con la aplicación en la función create_app().
db = SQLAlchemy()
migrate = Migrate()
