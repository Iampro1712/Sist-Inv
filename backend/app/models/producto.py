from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Numeric
from backend.app import db

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Stock y precios
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=10)
    precio_compra = db.Column(Numeric(10, 2))
    precio_venta = db.Column(Numeric(10, 2))
    
    # Información adicional
    unidad_medida = db.Column(db.String(20), default='unidad')  # unidad, kg, litro, etc.
    ubicacion = db.Column(db.String(100))  # Ubicación física en almacén
    fecha_vencimiento = db.Column(db.Date)
    lote = db.Column(db.String(50))
    
    # Metadatos
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    movimientos = db.relationship('Movimiento', backref='producto', lazy=True)
    alertas = db.relationship('Alerta', backref='producto', lazy=True)
    
    def __init__(self, codigo, nombre, categoria_id, descripcion=None, 
                 stock_minimo=10, precio_compra=None, precio_venta=None,
                 unidad_medida='unidad', ubicacion=None, fecha_vencimiento=None, lote=None):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria_id = categoria_id
        self.descripcion = descripcion
        self.stock_minimo = stock_minimo
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.unidad_medida = unidad_medida
        self.ubicacion = ubicacion
        self.fecha_vencimiento = fecha_vencimiento
        self.lote = lote
    
    @property
    def necesita_restock(self):
        """Verificar si el producto necesita restock"""
        return self.stock_actual <= self.stock_minimo
    
    @property
    def dias_para_vencer(self):
        """Calcular días hasta vencimiento"""
        if not self.fecha_vencimiento:
            return None
        return (self.fecha_vencimiento - date.today()).days
    
    @property
    def esta_vencido(self):
        """Verificar si el producto está vencido"""
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento < date.today()
    
    @property
    def valor_inventario(self):
        """Calcular valor total del inventario para este producto"""
        if self.precio_compra:
            return float(self.precio_compra) * self.stock_actual
        return 0
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria_id': self.categoria_id,
            'categoria_nombre': self.categoria.nombre if self.categoria else None,
            'stock_actual': self.stock_actual,
            'stock_minimo': self.stock_minimo,
            'precio_compra': float(self.precio_compra) if self.precio_compra else None,
            'precio_venta': float(self.precio_venta) if self.precio_venta else None,
            'unidad_medida': self.unidad_medida,
            'ubicacion': self.ubicacion,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'lote': self.lote,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'necesita_restock': self.necesita_restock,
            'dias_para_vencer': self.dias_para_vencer,
            'esta_vencido': self.esta_vencido,
            'valor_inventario': self.valor_inventario
        }
    
    def __repr__(self):
        return f'<Producto {self.codigo} - {self.nombre}>'
