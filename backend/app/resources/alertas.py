from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.app.models.alerta import Alerta
from backend.app.models.producto import Producto
from backend.app.models.usuario import Usuario

alertas_bp = Blueprint('alertas', __name__)

@alertas_bp.route('', methods=['GET'])
@jwt_required()
def get_alertas():
    """Obtener todas las alertas con filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        activas_only = request.args.get('activas_only', 'true').lower() == 'true'
        no_leidas_only = request.args.get('no_leidas_only', 'false').lower() == 'true'
        tipo = request.args.get('tipo')
        prioridad = request.args.get('prioridad')
        
        query = Alerta.query
        
        # Aplicar filtros
        if activas_only:
            query = query.filter_by(activa=True)
        
        if no_leidas_only:
            query = query.filter_by(leida=False)
        
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        if prioridad:
            query = query.filter_by(prioridad=prioridad)
        
        # Ordenar por fecha de creación descendente
        query = query.order_by(Alerta.fecha_creacion.desc())
        
        alertas = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'alertas': [alerta.to_dict() for alerta in alertas.items],
            'total': alertas.total,
            'pages': alertas.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alertas_bp.route('/<int:alerta_id>', methods=['GET'])
@jwt_required()
def get_alerta(alerta_id):
    """Obtener una alerta específica"""
    try:
        alerta = Alerta.query.get(alerta_id)
        
        if not alerta:
            return jsonify({'error': 'Alerta no encontrada'}), 404
        
        return jsonify(alerta.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alertas_bp.route('/<int:alerta_id>/leer', methods=['POST'])
@jwt_required()
def marcar_como_leida(alerta_id):
    """Marcar alerta como leída"""
    try:
        alerta = Alerta.query.get(alerta_id)
        
        if not alerta:
            return jsonify({'error': 'Alerta no encontrada'}), 404
        
        alerta.marcar_como_leida()
        db.session.commit()
        
        return jsonify({
            'message': 'Alerta marcada como leída',
            'alerta': alerta.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alertas_bp.route('/<int:alerta_id>/resolver', methods=['POST'])
@jwt_required()
def resolver_alerta(alerta_id):
    """Resolver alerta"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario or usuario.rol not in ['admin', 'manager']:
            return jsonify({'error': 'No tienes permisos para resolver alertas'}), 403
        
        alerta = Alerta.query.get(alerta_id)
        
        if not alerta:
            return jsonify({'error': 'Alerta no encontrada'}), 404
        
        alerta.resolver()
        db.session.commit()
        
        return jsonify({
            'message': 'Alerta resuelta exitosamente',
            'alerta': alerta.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alertas_bp.route('/generar', methods=['POST'])
@jwt_required()
def generar_alertas():
    """Generar alertas automáticas para stock bajo y productos vencidos"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario or usuario.rol not in ['admin', 'manager']:
            return jsonify({'error': 'No tienes permisos para generar alertas'}), 403
        
        alertas_creadas = []
        
        # Buscar productos con stock bajo
        productos_stock_bajo = Producto.query.filter(
            Producto.stock_actual <= Producto.stock_minimo,
            Producto.activo == True
        ).all()
        
        for producto in productos_stock_bajo:
            # Verificar si ya existe una alerta activa para este producto
            alerta_existente = Alerta.query.filter_by(
                producto_id=producto.id,
                tipo='stock_bajo',
                activa=True
            ).first()
            
            if not alerta_existente:
                if producto.stock_actual == 0:
                    tipo = 'sin_stock'
                    titulo = f'Sin stock: {producto.nombre}'
                    mensaje = f'El producto {producto.codigo} - {producto.nombre} no tiene stock disponible.'
                    prioridad = 'critica'
                else:
                    tipo = 'stock_bajo'
                    titulo = f'Stock bajo: {producto.nombre}'
                    mensaje = f'El producto {producto.codigo} - {producto.nombre} tiene stock bajo. Stock actual: {producto.stock_actual}, Stock mínimo: {producto.stock_minimo}'
                    prioridad = 'alta'
                
                alerta = Alerta(
                    producto_id=producto.id,
                    usuario_id=usuario.id,
                    tipo=tipo,
                    titulo=titulo,
                    mensaje=mensaje,
                    prioridad=prioridad
                )
                
                db.session.add(alerta)
                alertas_creadas.append(alerta)
        
        # Buscar productos próximos a vencer (30 días)
        fecha_limite = date.today()
        from datetime import timedelta
        fecha_limite_vencimiento = fecha_limite + timedelta(days=30)
        
        productos_por_vencer = Producto.query.filter(
            Producto.fecha_vencimiento.between(fecha_limite, fecha_limite_vencimiento),
            Producto.activo == True
        ).all()
        
        for producto in productos_por_vencer:
            # Verificar si ya existe una alerta activa para este producto
            alerta_existente = Alerta.query.filter_by(
                producto_id=producto.id,
                tipo='vencimiento',
                activa=True
            ).first()
            
            if not alerta_existente:
                dias_restantes = (producto.fecha_vencimiento - fecha_limite).days
                
                if dias_restantes <= 7:
                    prioridad = 'critica'
                elif dias_restantes <= 15:
                    prioridad = 'alta'
                else:
                    prioridad = 'media'
                
                alerta = Alerta(
                    producto_id=producto.id,
                    usuario_id=usuario.id,
                    tipo='vencimiento',
                    titulo=f'Próximo a vencer: {producto.nombre}',
                    mensaje=f'El producto {producto.codigo} - {producto.nombre} vence en {dias_restantes} días (Fecha de vencimiento: {producto.fecha_vencimiento})',
                    prioridad=prioridad
                )
                
                db.session.add(alerta)
                alertas_creadas.append(alerta)
        
        # Buscar productos vencidos
        productos_vencidos = Producto.query.filter(
            Producto.fecha_vencimiento < fecha_limite,
            Producto.activo == True
        ).all()
        
        for producto in productos_vencidos:
            # Verificar si ya existe una alerta activa para este producto
            alerta_existente = Alerta.query.filter_by(
                producto_id=producto.id,
                tipo='vencido',
                activa=True
            ).first()
            
            if not alerta_existente:
                dias_vencido = (fecha_limite - producto.fecha_vencimiento).days
                
                alerta = Alerta(
                    producto_id=producto.id,
                    usuario_id=usuario.id,
                    tipo='vencido',
                    titulo=f'Producto vencido: {producto.nombre}',
                    mensaje=f'El producto {producto.codigo} - {producto.nombre} está vencido desde hace {dias_vencido} días (Fecha de vencimiento: {producto.fecha_vencimiento})',
                    prioridad='critica'
                )
                
                db.session.add(alerta)
                alertas_creadas.append(alerta)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Se generaron {len(alertas_creadas)} nuevas alertas',
            'alertas_creadas': len(alertas_creadas),
            'alertas': [alerta.to_dict() for alerta in alertas_creadas]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alertas_bp.route('/estadisticas', methods=['GET'])
@jwt_required()
def get_estadisticas_alertas():
    """Obtener estadísticas de alertas"""
    try:
        total_alertas = Alerta.query.count()
        alertas_activas = Alerta.query.filter_by(activa=True).count()
        alertas_no_leidas = Alerta.query.filter_by(leida=False, activa=True).count()
        
        # Contar por tipo
        stock_bajo = Alerta.query.filter_by(tipo='stock_bajo', activa=True).count()
        sin_stock = Alerta.query.filter_by(tipo='sin_stock', activa=True).count()
        vencimiento = Alerta.query.filter_by(tipo='vencimiento', activa=True).count()
        vencidos = Alerta.query.filter_by(tipo='vencido', activa=True).count()
        
        # Contar por prioridad
        criticas = Alerta.query.filter_by(prioridad='critica', activa=True).count()
        altas = Alerta.query.filter_by(prioridad='alta', activa=True).count()
        medias = Alerta.query.filter_by(prioridad='media', activa=True).count()
        bajas = Alerta.query.filter_by(prioridad='baja', activa=True).count()
        
        return jsonify({
            'total_alertas': total_alertas,
            'alertas_activas': alertas_activas,
            'alertas_no_leidas': alertas_no_leidas,
            'por_tipo': {
                'stock_bajo': stock_bajo,
                'sin_stock': sin_stock,
                'vencimiento': vencimiento,
                'vencidos': vencidos
            },
            'por_prioridad': {
                'critica': criticas,
                'alta': altas,
                'media': medias,
                'baja': bajas
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
