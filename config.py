class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///radiation_monitor.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key-here'