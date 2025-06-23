from datetime import datetime
from backend.app import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    productos = db.relationship('Producto', backref='categoria', lazy=True)
    
    def __init__(self, nombre, descripcion=None):
        self.nombre = nombre
        self.descripcion = descripcion
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'total_productos': len(self.productos) if self.productos else 0
        }
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'
