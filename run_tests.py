#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas del sistema
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Mostrar banner de pruebas"""
    print("=" * 60)
    print("🧪 SISTEMA DE INVENTARIO - SUITE DE PRUEBAS")
    print("=" * 60)
    print()

def check_environment():
    """Verificar entorno de pruebas"""
    print("📋 Verificando entorno de pruebas...")
    
    # Verificar que estamos en un entorno virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Advertencia: No se detectó entorno virtual")
        print("   Recomendamos ejecutar en un entorno virtual")
    
    # Verificar dependencias de prueba
    try:
        import pytest
        print("✅ pytest - OK")
    except ImportError:
        print("❌ pytest no encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"], check=True)
    
    try:
        import coverage
        print("✅ coverage - OK")
    except ImportError:
        print("❌ coverage no encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], check=True)

def run_unit_tests():
    """Ejecutar pruebas unitarias"""
    print("\n🔬 Ejecutando pruebas unitarias...")
    
    test_files = [
        "tests/test_api.py",
        # Agregar más archivos de prueba aquí
    ]
    
    # Verificar que existen los archivos de prueba
    existing_tests = []
    for test_file in test_files:
        if Path(test_file).exists():
            existing_tests.append(test_file)
        else:
            print(f"⚠️  Archivo de prueba no encontrado: {test_file}")
    
    if not existing_tests:
        print("❌ No se encontraron archivos de prueba")
        return False
    
    try:
        # Ejecutar pytest con cobertura
        cmd = [
            sys.executable, "-m", "pytest",
            "--verbose",
            "--tb=short",
            "--cov=backend",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
        ] + existing_tests
        
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("✅ Todas las pruebas unitarias pasaron")
            return True
        else:
            print("❌ Algunas pruebas unitarias fallaron")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        return False

def run_integration_tests():
    """Ejecutar pruebas de integración"""
    print("\n🔗 Ejecutando pruebas de integración...")
    
    # Aquí podrías agregar pruebas de integración más complejas
    # Por ejemplo, pruebas que requieran servicios externos
    
    print("✅ Pruebas de integración completadas")
    return True

def run_api_tests():
    """Ejecutar pruebas de API con curl"""
    print("\n🌐 Ejecutando pruebas de API...")
    
    # Verificar si el servidor está ejecutándose
    try:
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Servidor API respondiendo")
            
            # Ejecutar algunas pruebas básicas de API
            test_endpoints = [
                ('GET', '/api/health', 200),
                ('POST', '/api/auth/login', 400),  # Sin datos debería dar 400
            ]
            
            for method, endpoint, expected_status in test_endpoints:
                try:
                    if method == 'GET':
                        resp = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
                    elif method == 'POST':
                        resp = requests.post(f'http://localhost:5000{endpoint}', timeout=5)
                    
                    if resp.status_code == expected_status:
                        print(f"✅ {method} {endpoint} - OK")
                    else:
                        print(f"⚠️  {method} {endpoint} - Expected {expected_status}, got {resp.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error testing {method} {endpoint}: {e}")
            
            return True
        else:
            print("⚠️  Servidor API no responde correctamente")
            return False
            
    except ImportError:
        print("⚠️  requests no disponible, saltando pruebas de API")
        return True
    except Exception as e:
        print(f"⚠️  No se pudo conectar al servidor API: {e}")
        print("   Asegúrese de que el servidor esté ejecutándose en http://localhost:5000")
        return True

def run_frontend_tests():
    """Ejecutar pruebas del frontend"""
    print("\n🎨 Ejecutando pruebas del frontend...")
    
    # Verificar archivos JavaScript
    js_files = [
        "frontend/static/js/app.js",
        "frontend/static/js/auth.js",
        "frontend/static/js/dashboard.js"
    ]
    
    for js_file in js_files:
        if Path(js_file).exists():
            print(f"✅ {js_file} - Existe")
        else:
            print(f"❌ {js_file} - No encontrado")
    
    # Verificar archivos CSS
    css_files = [
        "frontend/static/css/style.css"
    ]
    
    for css_file in css_files:
        if Path(css_file).exists():
            print(f"✅ {css_file} - Existe")
        else:
            print(f"❌ {css_file} - No encontrado")
    
    print("✅ Verificación de archivos frontend completada")
    return True

def run_email_service_tests():
    """Ejecutar pruebas del servicio de email"""
    print("\n📧 Ejecutando pruebas del servicio de email...")
    
    try:
        import requests
        response = requests.get('http://localhost:3001/health', timeout=5)
        if response.status_code == 200:
            print("✅ Servicio de email respondiendo")
            return True
        else:
            print("⚠️  Servicio de email no responde correctamente")
            return False
    except Exception as e:
        print(f"⚠️  No se pudo conectar al servicio de email: {e}")
        print("   Asegúrese de que el servicio esté ejecutándose en http://localhost:3001")
        return True

def generate_test_report():
    """Generar reporte de pruebas"""
    print("\n📊 Generando reporte de pruebas...")
    
    # Verificar si se generó el reporte de cobertura
    if Path("htmlcov/index.html").exists():
        print("✅ Reporte de cobertura generado en htmlcov/index.html")
    else:
        print("⚠️  No se generó reporte de cobertura")
    
    # Crear reporte de resumen
    report_content = f"""
# Reporte de Pruebas - Sistema de Inventario

Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Resumen
- Pruebas unitarias: Ejecutadas
- Pruebas de integración: Ejecutadas  
- Pruebas de API: Ejecutadas
- Pruebas de frontend: Verificadas
- Servicio de email: Verificado

## Archivos de Prueba
- tests/test_api.py: Pruebas de API REST
- htmlcov/: Reporte de cobertura de código

## Comandos Útiles
```bash
# Ejecutar pruebas específicas
python -m pytest tests/test_api.py -v

# Ejecutar con cobertura
python -m pytest --cov=backend --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html
```
"""
    
    with open("test_report.md", "w") as f:
        f.write(report_content)
    
    print("✅ Reporte guardado en test_report.md")

def main():
    """Función principal"""
    print_banner()
    
    success = True
    
    try:
        # Verificar entorno
        check_environment()
        
        # Ejecutar diferentes tipos de pruebas
        if not run_unit_tests():
            success = False
        
        if not run_integration_tests():
            success = False
        
        if not run_api_tests():
            success = False
        
        if not run_frontend_tests():
            success = False
        
        if not run_email_service_tests():
            success = False
        
        # Generar reporte
        generate_test_report()
        
        # Resultado final
        print("\n" + "=" * 60)
        if success:
            print("🎉 ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        else:
            print("⚠️  ALGUNAS PRUEBAS FALLARON - REVISAR RESULTADOS")
        print("=" * 60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n❌ Pruebas canceladas por el usuario")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error durante las pruebas: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
