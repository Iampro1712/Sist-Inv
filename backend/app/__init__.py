from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from celery import Celery
import os

# Inicialización de extensiones
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def make_celery(app):
    """Crear instancia de Celery configurada con Flask"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        """Tarea que mantiene el contexto de la aplicación Flask"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def create_app(config_name='development'):
    """Factory para crear la aplicación Flask"""
    # Configurar directorios de templates y static
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    template_dir = os.path.join(base_dir, 'frontend', 'templates')
    static_dir = os.path.join(base_dir, 'frontend', 'static')

    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Cargar configuración
    from backend.config.config import config_dict
    app.config.from_object(config_dict[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Registrar blueprints
    from backend.app.resources.auth import auth_bp
    from backend.app.resources.productos import productos_bp
    from backend.app.resources.categorias import categorias_bp
    from backend.app.resources.movimientos import movimientos_bp
    from backend.app.resources.reportes import reportes_bp
    from backend.app.resources.alertas import alertas_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(productos_bp, url_prefix='/api/productos')
    app.register_blueprint(categorias_bp, url_prefix='/api/categorias')
    app.register_blueprint(movimientos_bp, url_prefix='/api/movimientos')
    app.register_blueprint(reportes_bp, url_prefix='/api/reportes')
    app.register_blueprint(alertas_bp, url_prefix='/api/alertas')
    
    return app
