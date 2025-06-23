#!/usr/bin/env python3
"""
Tests básicos para la API del Sistema de Inventario
"""

import pytest
import json

class TestAuth:
    """Tests de autenticación"""
    
    def test_register_user(self, client):
        """Test registro de usuario"""
        response = client.post('/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'new@test.com',
                'password': 'newpass123',
                'nombre': 'New',
                'apellido': 'User'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'usuario' in data
        assert data['usuario']['username'] == 'newuser'
    
    def test_login_user(self, client):
        """Test inicio de sesión"""
        # Primero registrar usuario
        client.post('/api/auth/register',
            json={
                'username': 'loginuser',
                'email': 'login@test.com',
                'password': 'loginpass123',
                'nombre': 'Login',
                'apellido': 'User'
            })
        
        # Luego iniciar sesión
        response = client.post('/api/auth/login',
            json={
                'username': 'loginuser',
                'password': 'loginpass123'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'usuario' in data
    
    def test_get_profile(self, client, auth_headers):
        """Test obtener perfil"""
        response = client.get('/api/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'testuser'

class TestCategorias:
    """Tests de categorías"""
    
    def test_create_categoria(self, client, auth_headers):
        """Test crear categoría"""
        response = client.post('/api/categorias',
            json={
                'nombre': 'Electrónicos',
                'descripcion': 'Productos electrónicos'
            },
            headers=auth_headers)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['categoria']['nombre'] == 'Electrónicos'

    def test_get_categorias(self, client, auth_headers, sample_categoria):
        """Test obtener categorías"""
        response = client.get('/api/categorias', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'categorias' in data
        assert len(data['categorias']) > 0

class TestProductos:
    """Tests de productos"""
    
    def test_create_producto(self, client, auth_headers, sample_categoria):
        """Test crear producto"""
        # Crear producto
        response = client.post('/api/productos',
            json={
                'codigo': 'TEST002',
                'nombre': 'Producto de Prueba',
                'categoria_id': sample_categoria['id'],
                'descripcion': 'Descripción de prueba',
                'stock_minimo': 10,
                'precio_compra': 100.00,
                'precio_venta': 150.00
            },
            headers=auth_headers)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['producto']['codigo'] == 'TEST002'
        assert data['producto']['nombre'] == 'Producto de Prueba'
    
    def test_get_productos(self, client, auth_headers):
        """Test obtener productos"""
        response = client.get('/api/productos', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'productos' in data
    
    def test_update_stock(self, client, auth_headers, sample_producto):
        """Test actualizar stock"""
        # Actualizar stock
        response = client.post(f'/api/productos/{sample_producto["id"]}/stock',
            json={
                'tipo': 'entrada',
                'cantidad': 50,
                'motivo': 'Compra inicial'
            },
            headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['producto']['stock_actual'] == 50

class TestMovimientos:
    """Tests de movimientos"""
    
    def test_get_movimientos(self, client, auth_headers):
        """Test obtener movimientos"""
        response = client.get('/api/movimientos', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'movimientos' in data
    
    def test_get_estadisticas_movimientos(self, client, auth_headers):
        """Test obtener estadísticas de movimientos"""
        response = client.get('/api/movimientos/estadisticas', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_movimientos' in data
        assert 'entradas' in data
        assert 'salidas' in data

class TestAlertas:
    """Tests de alertas"""
    
    def test_get_alertas(self, client, auth_headers):
        """Test obtener alertas"""
        response = client.get('/api/alertas', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'alertas' in data
    
    def test_generar_alertas(self, client, auth_headers):
        """Test generar alertas automáticas"""
        response = client.post('/api/alertas/generar', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'alertas_creadas' in data
    
    def test_get_estadisticas_alertas(self, client, auth_headers):
        """Test obtener estadísticas de alertas"""
        response = client.get('/api/alertas/estadisticas', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_alertas' in data
        assert 'alertas_activas' in data

class TestReportes:
    """Tests de reportes"""
    
    def test_reporte_inventario_json(self, client, auth_headers):
        """Test reporte de inventario en JSON"""
        response = client.get('/api/reportes/inventario?formato=json', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'fecha_generacion' in data
        assert 'resumen' in data
        assert 'productos' in data
    
    def test_reporte_movimientos_json(self, client, auth_headers):
        """Test reporte de movimientos en JSON"""
        response = client.get('/api/reportes/movimientos?formato=json', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'fecha_generacion' in data
        assert 'periodo' in data
        assert 'resumen' in data
        assert 'movimientos' in data

if __name__ == '__main__':
    pytest.main([__file__])
