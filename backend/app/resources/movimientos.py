from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.app.models.movimiento import Movimiento
from backend.app.models.producto import Producto
from backend.app.models.usuario import Usuario

movimientos_bp = Blueprint('movimientos', __name__)

@movimientos_bp.route('', methods=['GET'])
@jwt_required()
def get_movimientos():
    """Obtener historial de movimientos con filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        producto_id = request.args.get('producto_id', type=int)
        usuario_id = request.args.get('usuario_id', type=int)
        tipo = request.args.get('tipo')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        query = Movimiento.query
        
        # Aplicar filtros
        if producto_id:
            query = query.filter_by(producto_id=producto_id)
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        if fecha_desde:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Movimiento.fecha_movimiento >= fecha_desde_dt)
        
        if fecha_hasta:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Agregar 23:59:59 para incluir todo el día
            fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Movimiento.fecha_movimiento <= fecha_hasta_dt)
        
        # Ordenar por fecha descendente
        query = query.order_by(Movimiento.fecha_movimiento.desc())
        
        movimientos = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'movimientos': [movimiento.to_dict() for movimiento in movimientos.items],
            'total': movimientos.total,
            'pages': movimientos.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@movimientos_bp.route('/<int:movimiento_id>', methods=['GET'])
@jwt_required()
def get_movimiento(movimiento_id):
    """Obtener un movimiento específico"""
    try:
        movimiento = Movimiento.query.get(movimiento_id)
        
        if not movimiento:
            return jsonify({'error': 'Movimiento no encontrado'}), 404
        
        return jsonify(movimiento.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@movimientos_bp.route('/producto/<int:producto_id>', methods=['GET'])
@jwt_required()
def get_movimientos_producto(producto_id):
    """Obtener historial de movimientos de un producto específico"""
    try:
        producto = Producto.query.get(producto_id)
        
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        movimientos = Movimiento.query.filter_by(producto_id=producto_id)\
            .order_by(Movimiento.fecha_movimiento.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'producto': producto.to_dict(),
            'movimientos': [movimiento.to_dict() for movimiento in movimientos.items],
            'total': movimientos.total,
            'pages': movimientos.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@movimientos_bp.route('/estadisticas', methods=['GET'])
@jwt_required()
def get_estadisticas_movimientos():
    """Obtener estadísticas de movimientos"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        query = Movimiento.query
        
        # Aplicar filtros de fecha si se proporcionan
        if fecha_desde:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Movimiento.fecha_movimiento >= fecha_desde_dt)
        
        if fecha_hasta:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Movimiento.fecha_movimiento <= fecha_hasta_dt)
        
        # Contar movimientos por tipo
        total_entradas = query.filter_by(tipo='entrada').count()
        total_salidas = query.filter_by(tipo='salida').count()
        total_ajustes = query.filter_by(tipo='ajuste').count()
        
        # Calcular valores monetarios (solo si tienen precio_unitario)
        valor_entradas = db.session.query(db.func.sum(
            Movimiento.cantidad * Movimiento.precio_unitario
        )).filter(
            Movimiento.tipo == 'entrada',
            Movimiento.precio_unitario.isnot(None)
        )
        
        if fecha_desde:
            valor_entradas = valor_entradas.filter(
                Movimiento.fecha_movimiento >= fecha_desde_dt
            )
        if fecha_hasta:
            valor_entradas = valor_entradas.filter(
                Movimiento.fecha_movimiento <= fecha_hasta_dt
            )
        
        valor_entradas = valor_entradas.scalar() or 0
        
        valor_salidas = db.session.query(db.func.sum(
            Movimiento.cantidad * Movimiento.precio_unitario
        )).filter(
            Movimiento.tipo == 'salida',
            Movimiento.precio_unitario.isnot(None)
        )
        
        if fecha_desde:
            valor_salidas = valor_salidas.filter(
                Movimiento.fecha_movimiento >= fecha_desde_dt
            )
        if fecha_hasta:
            valor_salidas = valor_salidas.filter(
                Movimiento.fecha_movimiento <= fecha_hasta_dt
            )
        
        valor_salidas = valor_salidas.scalar() or 0
        
        return jsonify({
            'total_movimientos': total_entradas + total_salidas + total_ajustes,
            'entradas': {
                'cantidad': total_entradas,
                'valor': float(valor_entradas)
            },
            'salidas': {
                'cantidad': total_salidas,
                'valor': float(valor_salidas)
            },
            'ajustes': {
                'cantidad': total_ajustes
            },
            'periodo': {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
