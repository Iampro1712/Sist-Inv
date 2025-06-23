from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.app.models.producto import Producto
from backend.app.models.categoria import Categoria
from backend.app.models.usuario import Usuario
from backend.app.models.movimiento import Movimiento

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('', methods=['GET'])
@jwt_required()
def get_productos():
    """Obtener todos los productos con filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        categoria_id = request.args.get('categoria_id', type=int)
        activos_only = request.args.get('activos_only', 'true').lower() == 'true'
        stock_bajo = request.args.get('stock_bajo', 'false').lower() == 'true'
        vencidos = request.args.get('vencidos', 'false').lower() == 'true'
        search = request.args.get('search', '')
        
        query = Producto.query
        
        # Aplicar filtros
        if activos_only:
            query = query.filter_by(activo=True)
        
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        if stock_bajo:
            query = query.filter(Producto.stock_actual <= Producto.stock_minimo)
        
        if vencidos:
            query = query.filter(Producto.fecha_vencimiento < date.today())
        
        if search:
            query = query.filter(
                db.or_(
                    Producto.codigo.contains(search),
                    Producto.nombre.contains(search),
                    Producto.descripcion.contains(search)
                )
            )
        
        productos = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'productos': [producto.to_dict() for producto in productos.items],
            'total': productos.total,
            'pages': productos.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/<int:producto_id>', methods=['GET'])
@jwt_required()
def get_producto(producto_id):
    """Obtener un producto específico"""
    try:
        producto = Producto.query.get(producto_id)
        
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        return jsonify(producto.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@productos_bp.route('', methods=['POST'])
@jwt_required()
def create_producto():
    """Crear nuevo producto"""
    try:
        # Verificar permisos
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario or usuario.rol not in ['admin', 'manager']:
            return jsonify({'error': 'No tienes permisos para crear productos'}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['codigo', 'nombre', 'categoria_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Verificar si el código ya existe
        if Producto.query.filter_by(codigo=data['codigo']).first():
            return jsonify({'error': 'Ya existe un producto con ese código'}), 400
        
        # Verificar que la categoría existe
        categoria = Categoria.query.get(data['categoria_id'])
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        # Crear producto
        producto = Producto(
            codigo=data['codigo'],
            nombre=data['nombre'],
            categoria_id=data['categoria_id'],
            descripcion=data.get('descripcion'),
            stock_minimo=data.get('stock_minimo', 10),
            precio_compra=data.get('precio_compra'),
            precio_venta=data.get('precio_venta'),
            unidad_medida=data.get('unidad_medida', 'unidad'),
            ubicacion=data.get('ubicacion'),
            fecha_vencimiento=datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date() if data.get('fecha_vencimiento') else None,
            lote=data.get('lote')
        )
        
        db.session.add(producto)
        db.session.commit()
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'producto': producto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/<int:producto_id>', methods=['PUT'])
@jwt_required()
def update_producto(producto_id):
    """Actualizar producto"""
    try:
        # Verificar permisos
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)

        if not usuario or usuario.rol not in ['admin', 'manager']:
            return jsonify({'error': 'No tienes permisos para actualizar productos'}), 403

        producto = Producto.query.get(producto_id)

        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404

        data = request.get_json()

        # Actualizar campos
        if 'codigo' in data:
            # Verificar que el código no esté en uso por otro producto
            existing = Producto.query.filter_by(codigo=data['codigo']).first()
            if existing and existing.id != producto.id:
                return jsonify({'error': 'Ya existe un producto con ese código'}), 400
            producto.codigo = data['codigo']

        if 'nombre' in data:
            producto.nombre = data['nombre']

        if 'descripcion' in data:
            producto.descripcion = data['descripcion']

        if 'categoria_id' in data:
            categoria = Categoria.query.get(data['categoria_id'])
            if not categoria:
                return jsonify({'error': 'Categoría no encontrada'}), 404
            producto.categoria_id = data['categoria_id']

        if 'stock_minimo' in data:
            producto.stock_minimo = data['stock_minimo']

        if 'precio_compra' in data:
            producto.precio_compra = data['precio_compra']

        if 'precio_venta' in data:
            producto.precio_venta = data['precio_venta']

        if 'unidad_medida' in data:
            producto.unidad_medida = data['unidad_medida']

        if 'ubicacion' in data:
            producto.ubicacion = data['ubicacion']

        if 'fecha_vencimiento' in data:
            if data['fecha_vencimiento']:
                producto.fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
            else:
                producto.fecha_vencimiento = None

        if 'lote' in data:
            producto.lote = data['lote']

        if 'activo' in data:
            producto.activo = data['activo']

        db.session.commit()

        return jsonify({
            'message': 'Producto actualizado exitosamente',
            'producto': producto.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/<int:producto_id>/stock', methods=['POST'])
@jwt_required()
def actualizar_stock(producto_id):
    """Actualizar stock de producto (entrada, salida o ajuste)"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        producto = Producto.query.get(producto_id)

        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404

        data = request.get_json()

        # Validar datos requeridos
        if not data.get('tipo') or not data.get('cantidad'):
            return jsonify({'error': 'Tipo y cantidad son requeridos'}), 400

        tipo = data['tipo']
        cantidad = int(data['cantidad'])

        if tipo not in ['entrada', 'salida', 'ajuste']:
            return jsonify({'error': 'Tipo debe ser: entrada, salida o ajuste'}), 400

        if cantidad <= 0 and tipo != 'ajuste':
            return jsonify({'error': 'Cantidad debe ser mayor a 0'}), 400

        # Verificar stock suficiente para salidas
        if tipo == 'salida' and producto.stock_actual < cantidad:
            return jsonify({'error': 'Stock insuficiente'}), 400

        # Guardar stock anterior
        stock_anterior = producto.stock_actual

        # Crear movimiento
        movimiento = Movimiento(
            producto_id=producto.id,
            usuario_id=usuario.id,
            tipo=tipo,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            precio_unitario=data.get('precio_unitario'),
            motivo=data.get('motivo'),
            referencia=data.get('referencia'),
            observaciones=data.get('observaciones')
        )

        # Actualizar stock del producto
        producto.stock_actual = movimiento.stock_posterior

        db.session.add(movimiento)
        db.session.commit()

        return jsonify({
            'message': 'Stock actualizado exitosamente',
            'producto': producto.to_dict(),
            'movimiento': movimiento.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
