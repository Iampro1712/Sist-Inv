#!/usr/bin/env python3
"""
Script de configuración e instalación del Sistema de Inventario
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Mostrar banner del sistema"""
    print("=" * 60)
    print("🚀 SISTEMA DE GESTIÓN DE INVENTARIO")
    print("   Configuración e Instalación Automática")
    print("=" * 60)
    print()

def check_python_version():
    """Verificar versión de Python"""
    print("📋 Verificando versión de Python...")
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} - OK")

def check_dependencies():
    """Verificar dependencias del sistema"""
    print("\n📋 Verificando dependencias del sistema...")
    
    # Verificar MySQL
    try:
        subprocess.run(["mysql", "--version"], check=True, capture_output=True)
        print("✅ MySQL - OK")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  MySQL no encontrado. Instale MySQL Server")
        print("   Ubuntu/Debian: sudo apt install mysql-server")
        print("   CentOS/RHEL: sudo yum install mysql-server")
        print("   macOS: brew install mysql")
    
    # Verificar Redis
    try:
        subprocess.run(["redis-server", "--version"], check=True, capture_output=True)
        print("✅ Redis - OK")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Redis no encontrado. Instale Redis Server")
        print("   Ubuntu/Debian: sudo apt install redis-server")
        print("   CentOS/RHEL: sudo yum install redis")
        print("   macOS: brew install redis")
    
    # Verificar Node.js
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✅ Node.js - OK")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Node.js no encontrado. Instale Node.js")
        print("   Descargue desde: https://nodejs.org/")

def create_virtual_environment():
    """Crear entorno virtual de Python"""
    print("\n🐍 Configurando entorno virtual de Python...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Entorno virtual ya existe")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Entorno virtual creado")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando entorno virtual: {e}")
        sys.exit(1)

def install_python_dependencies():
    """Instalar dependencias de Python"""
    print("\n📦 Instalando dependencias de Python...")
    
    # Determinar el ejecutable de pip en el entorno virtual
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # Unix/Linux/macOS
        pip_path = Path("venv/bin/pip")
    
    try:
        # Actualizar pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # Instalar dependencias
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencias de Python instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def install_node_dependencies():
    """Instalar dependencias de Node.js"""
    print("\n📦 Instalando dependencias de Node.js...")
    
    email_service_path = Path("email_service")
    if not email_service_path.exists():
        print("⚠️  Directorio email_service no encontrado")
        return
    
    try:
        subprocess.run(["npm", "install"], cwd=email_service_path, check=True)
        print("✅ Dependencias de Node.js instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias de Node.js: {e}")

def setup_environment_files():
    """Configurar archivos de entorno"""
    print("\n⚙️  Configurando archivos de entorno...")
    
    # Copiar .env.example a .env si no existe
    env_files = [
        (".env.example", ".env"),
        ("email_service/.env.example", "email_service/.env")
    ]
    
    for example_file, env_file in env_files:
        example_path = Path(example_file)
        env_path = Path(env_file)
        
        if example_path.exists() and not env_path.exists():
            shutil.copy(example_path, env_path)
            print(f"✅ Creado {env_file}")
        elif env_path.exists():
            print(f"✅ {env_file} ya existe")

def create_database():
    """Crear base de datos"""
    print("\n🗄️  Configurando base de datos...")
    
    # Determinar el ejecutable de Python en el entorno virtual
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python")
    else:  # Unix/Linux/macOS
        python_path = Path("venv/bin/python")
    
    try:
        # Inicializar base de datos
        subprocess.run([str(python_path), "app.py", "init-db"], check=True)
        print("✅ Base de datos inicializada")
        
        # Crear usuario administrador
        subprocess.run([str(python_path), "app.py", "create-admin"], check=True)
        print("✅ Usuario administrador creado")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error configurando base de datos: {e}")
        print("   Asegúrese de que MySQL esté ejecutándose y configurado correctamente")

def create_startup_scripts():
    """Crear scripts de inicio"""
    print("\n📝 Creando scripts de inicio...")
    
    # Script para iniciar el servidor Flask
    flask_script = """#!/bin/bash
# Script para iniciar el servidor Flask
source venv/bin/activate
export FLASK_ENV=development
python app.py
"""
    
    # Script para iniciar Celery Worker
    celery_script = """#!/bin/bash
# Script para iniciar Celery Worker
source venv/bin/activate
python celery_worker.py worker --loglevel=info
"""
    
    # Script para iniciar Celery Beat
    beat_script = """#!/bin/bash
# Script para iniciar Celery Beat
source venv/bin/activate
python celery_worker.py beat --loglevel=info
"""
    
    # Script para iniciar el servicio de email
    email_script = """#!/bin/bash
# Script para iniciar el servicio de email
cd email_service
npm start
"""
    
    scripts = [
        ("start_flask.sh", flask_script),
        ("start_celery.sh", celery_script),
        ("start_beat.sh", beat_script),
        ("start_email.sh", email_script)
    ]
    
    for script_name, script_content in scripts:
        script_path = Path(script_name)
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Hacer ejecutable en sistemas Unix
        if os.name != 'nt':
            os.chmod(script_path, 0o755)
        
        print(f"✅ Creado {script_name}")

def print_final_instructions():
    """Mostrar instrucciones finales"""
    print("\n" + "=" * 60)
    print("🎉 ¡INSTALACIÓN COMPLETADA!")
    print("=" * 60)
    print()
    print("📋 PRÓXIMOS PASOS:")
    print()
    print("1. Configurar archivos .env:")
    print("   - Edite .env con sus credenciales de MySQL")
    print("   - Edite email_service/.env con sus credenciales SMTP")
    print()
    print("2. Iniciar servicios:")
    print("   - Redis: sudo systemctl start redis")
    print("   - MySQL: sudo systemctl start mysql")
    print()
    print("3. Ejecutar la aplicación:")
    print("   - Servidor Flask: ./start_flask.sh")
    print("   - Celery Worker: ./start_celery.sh")
    print("   - Celery Beat: ./start_beat.sh")
    print("   - Servicio Email: ./start_email.sh")
    print()
    print("4. Acceder a la aplicación:")
    print("   - URL: http://localhost:5000")
    print("   - Usuario: admin")
    print("   - Contraseña: admin123")
    print()
    print("📚 DOCUMENTACIÓN:")
    print("   - README.md para más información")
    print("   - docs/ para documentación detallada")
    print()
    print("=" * 60)

def main():
    """Función principal"""
    print_banner()
    
    try:
        check_python_version()
        check_dependencies()
        create_virtual_environment()
        install_python_dependencies()
        install_node_dependencies()
        setup_environment_files()
        create_database()
        create_startup_scripts()
        print_final_instructions()
        
    except KeyboardInterrupt:
        print("\n\n❌ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error durante la instalación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
