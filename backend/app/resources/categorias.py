from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.app.models.categoria import Categoria
from backend.app.models.usuario import Usuario

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('', methods=['GET'])
@jwt_required()
def get_categorias():
    """Obtener todas las categorías"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        activas_only = request.args.get('activas_only', 'true').lower() == 'true'
        
        query = Categoria.query
        
        if activas_only:
            query = query.filter_by(activa=True)
        
        categorias = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'categorias': [categoria.to_dict() for categoria in categorias.items],
            'total': categorias.total,
            'pages': categorias.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/<int:categoria_id>', methods=['GET'])
@jwt_required()
def get_categoria(categoria_id):
    """Obtener una categoría específica"""
    try:
        categoria = Categoria.query.get(categoria_id)
        
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        return jsonify(categoria.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('', methods=['POST'])
@jwt_required()
def create_categoria():
    """Crear nueva categoría"""
    try:
        # Verificar permisos (solo admin y manager)
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario or usuario.rol not in ['admin', 'manager']:
            return jsonify({'error': 'No tienes permisos para crear categorías'}), 403
        
        data = request.get_json()
        
        if not data.get('nombre'):
            return jsonify({'error': 'Nombre es requerido'}), 400
        
        # Verificar si la categoría ya existe
        if Categoria.query.filter_by(nombre=data['nombre']).first():
            return jsonify({'error': 'Ya existe una categoría con ese nombre'}), 400
        
        categoria = Categoria(
            nombre=data['nombre'],
            descripcion=data.get('descripcion')
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoría creada exitosamente',
            'categoria': categoria.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/<int:categoria_id>', methods=['PUT'])
@jwt_required()
def update_categoria(categoria_id):
    """Actualizar categoría"""
    try:
        # Verificar permisos
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario or usuario.rol not in ['admin', 'manager']:
            return jsonify({'error': 'No tienes permisos para actualizar categorías'}), 403
        
        categoria = Categoria.query.get(categoria_id)
        
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'nombre' in data:
            # Verificar que el nombre no esté en uso por otra categoría
            existing = Categoria.query.filter_by(nombre=data['nombre']).first()
            if existing and existing.id != categoria.id:
                return jsonify({'error': 'Ya existe una categoría con ese nombre'}), 400
            categoria.nombre = data['nombre']
        
        if 'descripcion' in data:
            categoria.descripcion = data['descripcion']
        
        if 'activa' in data:
            categoria.activa = data['activa']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Categoría actualizada exitosamente',
            'categoria': categoria.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
@jwt_required()
def delete_categoria(categoria_id):
    """Eliminar categoría (soft delete)"""
    try:
        # Verificar permisos (solo admin)
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario or usuario.rol != 'admin':
            return jsonify({'error': 'No tienes permisos para eliminar categorías'}), 403
        
        categoria = Categoria.query.get(categoria_id)
        
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        # Verificar si tiene productos asociados
        if categoria.productos:
            return jsonify({
                'error': 'No se puede eliminar la categoría porque tiene productos asociados'
            }), 400
        
        # Soft delete
        categoria.activa = False
        db.session.commit()
        
        return jsonify({'message': 'Categoría eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
