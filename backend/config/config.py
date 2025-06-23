import os
from decouple import config

class Config:
    """Configuración base"""
    SECRET_KEY = config('SECRET_KEY', default='dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', default='jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    
    # Configuración de email
    MAIL_SERVER = config('MAIL_SERVER', default='smtp.gmail.com')
    MAIL_PORT = config('MAIL_PORT', default=587, cast=int)
    MAIL_USE_TLS = config('MAIL_USE_TLS', default=True, cast=bool)
    MAIL_USERNAME = config('MAIL_USERNAME', default='')
    MAIL_PASSWORD = config('MAIL_PASSWORD', default='')
    
    # Configuración de Celery
    CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
    
    # Configuración de alertas
    STOCK_MINIMO_DEFAULT = config('STOCK_MINIMO_DEFAULT', default=10, cast=int)
    DIAS_VENCIMIENTO_ALERTA = config('DIAS_VENCIMIENTO_ALERTA', default=30, cast=int)

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{config('DB_USER', default='root')}:"
        f"{config('DB_PASSWORD', default='')}@"
        f"{config('DB_HOST', default='localhost')}:"
        f"{config('DB_PORT', default=3306, cast=int)}/"
        f"{config('DB_NAME', default='inventario_db')}"
    )

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{config('DB_USER', default='root')}:"
        f"{config('DB_PASSWORD', default='')}@"
        f"{config('DB_HOST', default='localhost')}:"
        f"{config('DB_PORT', default=3306, cast=int)}/"
        f"{config('DB_NAME', default='inventario_db')}"
    )

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
