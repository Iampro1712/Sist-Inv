#!/usr/bin/env python3
"""
Script para probar la configuración de templates
"""

import os
from backend.app import create_app

# Crear aplicación
app = create_app('development')

# Verificar configuración de templates
print("🔍 Verificando configuración de templates...")
print(f"Template folder: {app.template_folder}")
print(f"Static folder: {app.static_folder}")

# Verificar que los directorios existen
template_path = os.path.abspath(app.template_folder)
static_path = os.path.abspath(app.static_folder)

print(f"Template path absoluto: {template_path}")
print(f"Static path absoluto: {static_path}")

print(f"Template folder existe: {os.path.exists(template_path)}")
print(f"Static folder existe: {os.path.exists(static_path)}")

# Listar archivos en template folder
if os.path.exists(template_path):
    print(f"Archivos en template folder:")
    for file in os.listdir(template_path):
        print(f"  - {file}")

# Probar cargar template
with app.app_context():
    try:
        from flask import render_template_string
        # Intentar cargar el template
        template_content = app.jinja_env.get_template('index.html')
        print("✅ Template index.html encontrado y cargado correctamente")
    except Exception as e:
        print(f"❌ Error cargando template: {e}")
        
        # Intentar encontrar el archivo manualmente
        index_path = os.path.join(template_path, 'index.html')
        print(f"Buscando index.html en: {index_path}")
        print(f"Archivo existe: {os.path.exists(index_path)}")
        
        if os.path.exists(index_path):
            print("El archivo existe pero Flask no lo puede encontrar")
            print("Verificando contenido del directorio padre:")
            parent_dir = os.path.dirname(template_path)
            print(f"Directorio padre: {parent_dir}")
            for item in os.listdir(parent_dir):
                item_path = os.path.join(parent_dir, item)
                if os.path.isdir(item_path):
                    print(f"  📁 {item}/")
                else:
                    print(f"  📄 {item}")
