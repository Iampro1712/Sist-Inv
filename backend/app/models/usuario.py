from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from backend.app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.Enum('admin', 'manager', 'empleado'), default='empleado')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    # Relaciones
    movimientos = db.relationship('Movimiento', backref='usuario', lazy=True)
    alertas_creadas = db.relationship('Alerta', backref='creado_por', lazy=True)
    
    def __init__(self, username, email, password, nombre, apellido, rol='empleado'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.nombre = nombre
        self.apellido = apellido
        self.rol = rol
    
    def set_password(self, password):
        """Establecer password hasheado"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None
        }
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
