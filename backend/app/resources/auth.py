from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.app import db
from backend.app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticar usuario y generar token JWT"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username y password son requeridos'}), 400
        
        usuario = Usuario.query.filter_by(username=data['username']).first()
        
        if not usuario or not usuario.check_password(data['password']):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not usuario.activo:
            return jsonify({'error': 'Usuario inactivo'}), 401
        
        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        
        # Crear token JWT
        access_token = create_access_token(identity=str(usuario.id))
        
        return jsonify({
            'access_token': access_token,
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['username', 'email', 'password', 'nombre', 'apellido']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username ya existe'}), 400
        
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email ya existe'}), 400
        
        # Crear nuevo usuario
        usuario = Usuario(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            rol=data.get('rol', 'empleado')
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'usuario': usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtener perfil del usuario autenticado"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify(usuario.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario autenticado"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'nombre' in data:
            usuario.nombre = data['nombre']
        if 'apellido' in data:
            usuario.apellido = data['apellido']
        if 'email' in data:
            # Verificar que el email no esté en uso por otro usuario
            existing_user = Usuario.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != usuario.id:
                return jsonify({'error': 'Email ya está en uso'}), 400
            usuario.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Cambiar contraseña del usuario autenticado"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Contraseña actual y nueva son requeridas'}), 400
        
        if not usuario.check_password(data['current_password']):
            return jsonify({'error': 'Contraseña actual incorrecta'}), 400
        
        usuario.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
