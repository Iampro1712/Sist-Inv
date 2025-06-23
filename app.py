#!/usr/bin/env python3
"""
Sistema de Gestión de Inventario
Aplicación principal Flask
"""

import os
from flask import Flask, render_template, jsonify
from backend.app import create_app, db, make_celery
from backend.app.models import Usuario, Categoria, Producto, Movimiento, Alerta

# Crear aplicación Flask
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Crear instancia de Celery
celery = make_celery(app)

@app.route('/')
def index():
    """Página principal del sistema"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Página de login"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    return render_template('index.html')

@app.route('/productos')
def productos():
    """Página de productos"""
    return render_template('productos.html')

@app.route('/productos/nuevo')
def nuevo_producto():
    """Página para crear nuevo producto"""
    return render_template('producto_form.html')

@app.route('/categorias')
def categorias():
    """Página de categorías"""
    return render_template('categorias.html')

@app.route('/movimientos')
def movimientos():
    """Página de movimientos"""
    return render_template('movimientos.html')

@app.route('/alertas')
def alertas():
    """Página de alertas"""
    return render_template('alertas.html')

@app.route('/reportes/<tipo>')
def reportes(tipo):
    """Páginas de reportes"""
    return render_template('reportes.html', tipo=tipo)

@app.route('/api/health')
def health_check():
    """Endpoint de verificación de salud"""
    return jsonify({
        'status': 'ok',
        'message': 'Sistema de Inventario funcionando correctamente',
        'version': '1.0.0'
    })

@app.shell_context_processor
def make_shell_context():
    """Contexto para Flask shell"""
    return {
        'db': db,
        'Usuario': Usuario,
        'Categoria': Categoria,
        'Producto': Producto,
        'Movimiento': Movimiento,
        'Alerta': Alerta
    }

@app.cli.command()
def init_db():
    """Inicializar base de datos"""
    db.create_all()
    print("Base de datos inicializada correctamente")

@app.cli.command()
def create_admin():
    """Crear usuario administrador por defecto"""
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            email='admin@inventario.com',
            password='admin123',
            nombre='Administrador',
            apellido='Sistema',
            rol='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario administrador creado: admin/admin123")
    else:
        print("Usuario administrador ya existe")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
