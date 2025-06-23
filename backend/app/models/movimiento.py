from datetime import datetime
from sqlalchemy import Numeric
from backend.app import db

class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    tipo = db.Column(db.Enum('entrada', 'salida', 'ajuste'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(Numeric(10, 2))
    
    # Información adicional
    motivo = db.Column(db.String(200))  # Venta, compra, devolución, ajuste, etc.
    referencia = db.Column(db.String(100))  # Número de factura, orden, etc.
    observaciones = db.Column(db.Text)
    
    # Stock antes y después del movimiento
    stock_anterior = db.Column(db.Integer, nullable=False)
    stock_posterior = db.Column(db.Integer, nullable=False)
    
    fecha_movimiento = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, producto_id, usuario_id, tipo, cantidad, stock_anterior, 
                 precio_unitario=None, motivo=None, referencia=None, observaciones=None):
        self.producto_id = producto_id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.cantidad = cantidad
        self.stock_anterior = stock_anterior
        self.precio_unitario = precio_unitario
        self.motivo = motivo
        self.referencia = referencia
        self.observaciones = observaciones
        
        # Calcular stock posterior según el tipo de movimiento
        if tipo == 'entrada':
            self.stock_posterior = stock_anterior + cantidad
        elif tipo == 'salida':
            self.stock_posterior = stock_anterior - cantidad
        else:  # ajuste
            self.stock_posterior = cantidad  # En ajuste, cantidad es el nuevo stock
    
    @property
    def valor_total(self):
        """Calcular valor total del movimiento"""
        if self.precio_unitario:
            return float(self.precio_unitario) * self.cantidad
        return 0
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'producto_codigo': self.producto.codigo if self.producto else None,
            'producto_nombre': self.producto.nombre if self.producto else None,
            'usuario_id': self.usuario_id,
            'usuario_nombre': f"{self.usuario.nombre} {self.usuario.apellido}" if self.usuario else None,
            'tipo': self.tipo,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else None,
            'valor_total': self.valor_total,
            'motivo': self.motivo,
            'referencia': self.referencia,
            'observaciones': self.observaciones,
            'stock_anterior': self.stock_anterior,
            'stock_posterior': self.stock_posterior,
            'fecha_movimiento': self.fecha_movimiento.isoformat() if self.fecha_movimiento else None
        }
    
    def __repr__(self):
        return f'<Movimiento {self.tipo} - {self.cantidad} - {self.producto.codigo if self.producto else "N/A"}>'
