"""
Configuración de pytest para el Sistema de Inventario
"""

import os
import sys
import pytest

# Agregar el directorio raíz al path de Python
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Configurar variables de entorno para testing
os.environ['FLASK_ENV'] = 'testing'
os.environ['DB_NAME'] = 'test_inventario_db'

@pytest.fixture(scope='session')
def app():
    """Crear aplicación de prueba"""
    from backend.app import create_app, db
    
    app = create_app('testing')
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        yield app
        # Limpiar después de las pruebas
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos CLI"""
    return app.test_cli_runner()

@pytest.fixture
def auth_token(client):
    """Token de autenticación para pruebas"""
    # Crear usuario de prueba
    response = client.post('/api/auth/register', 
        json={
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'testpass123',
            'nombre': 'Test',
            'apellido': 'User',
            'rol': 'admin'  # Dar permisos de admin para las pruebas
        })
    
    # Iniciar sesión
    response = client.post('/api/auth/login',
        json={
            'username': 'testuser',
            'password': 'testpass123'
        })
    
    if response.status_code == 200:
        import json
        data = json.loads(response.data)
        return data['access_token']
    else:
        pytest.fail(f"No se pudo obtener token de autenticación: {response.data}")

@pytest.fixture
def auth_headers(auth_token):
    """Headers de autenticación"""
    return {'Authorization': f'Bearer {auth_token}'}

@pytest.fixture
def sample_categoria(client, auth_headers):
    """Crear categoría de ejemplo para pruebas"""
    import time
    import json

    # Usar timestamp para hacer el nombre único
    timestamp = str(int(time.time() * 1000))
    nombre_categoria = f'Categoría Test {timestamp}'

    response = client.post('/api/categorias',
        json={
            'nombre': nombre_categoria,
            'descripcion': 'Categoría para pruebas'
        },
        headers=auth_headers)

    if response.status_code == 201:
        data = json.loads(response.data)
        return data['categoria']
    else:
        pytest.fail(f"No se pudo crear categoría de prueba: {response.data}")

@pytest.fixture
def sample_producto(client, auth_headers, sample_categoria):
    """Crear producto de ejemplo para pruebas"""
    import time
    import json

    # Usar timestamp para hacer el código único
    timestamp = str(int(time.time() * 1000))
    codigo_producto = f'TEST{timestamp}'

    response = client.post('/api/productos',
        json={
            'codigo': codigo_producto,
            'nombre': f'Producto Test {timestamp}',
            'categoria_id': sample_categoria['id'],
            'descripcion': 'Producto para pruebas',
            'stock_minimo': 10,
            'precio_compra': 100.00,
            'precio_venta': 150.00
        },
        headers=auth_headers)

    if response.status_code == 201:
        data = json.loads(response.data)
        return data['producto']
    else:
        pytest.fail(f"No se pudo crear producto de prueba: {response.data}")
