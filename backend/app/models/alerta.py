from datetime import datetime
from backend.app import db

class Alerta(db.Model):
    __tablename__ = 'alertas'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    tipo = db.Column(db.Enum('stock_bajo', 'vencimiento', 'vencido', 'sin_stock'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    
    # Estado de la alerta
    activa = db.Column(db.Boolean, default=True)
    leida = db.Column(db.Boolean, default=False)
    resuelta = db.Column(db.Boolean, default=False)
    
    # Fechas
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_lectura = db.Column(db.DateTime)
    fecha_resolucion = db.Column(db.DateTime)
    
    # Prioridad
    prioridad = db.Column(db.Enum('baja', 'media', 'alta', 'critica'), default='media')
    
    def __init__(self, producto_id, usuario_id, tipo, titulo, mensaje, prioridad='media'):
        self.producto_id = producto_id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.titulo = titulo
        self.mensaje = mensaje
        self.prioridad = prioridad
    
    def marcar_como_leida(self):
        """Marcar alerta como leída"""
        self.leida = True
        self.fecha_lectura = datetime.utcnow()
    
    def resolver(self):
        """Resolver alerta"""
        self.resuelta = True
        self.activa = False
        self.fecha_resolucion = datetime.utcnow()
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'producto_codigo': self.producto.codigo if self.producto else None,
            'producto_nombre': self.producto.nombre if self.producto else None,
            'usuario_id': self.usuario_id,
            'creado_por': f"{self.creado_por.nombre} {self.creado_por.apellido}" if self.creado_por else None,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'activa': self.activa,
            'leida': self.leida,
            'resuelta': self.resuelta,
            'prioridad': self.prioridad,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_lectura': self.fecha_lectura.isoformat() if self.fecha_lectura else None,
            'fecha_resolucion': self.fecha_resolucion.isoformat() if self.fecha_resolucion else None
        }
    
    def __repr__(self):
        return f'<Alerta {self.tipo} - {self.titulo}>'
