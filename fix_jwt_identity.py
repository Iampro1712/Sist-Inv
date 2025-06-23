#!/usr/bin/env python3
"""
Script para corregir get_jwt_identity() en todos los archivos
"""

import os
import re
from pathlib import Path

def fix_jwt_identity_in_file(file_path):
    """Corregir get_jwt_identity() en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón para encontrar líneas con get_jwt_identity()
        pattern = r'(\s+)usuario_id = get_jwt_identity\(\)'
        replacement = r'\1usuario_id = int(get_jwt_identity())'
        
        # Realizar el reemplazo
        new_content = re.sub(pattern, replacement, content)
        
        # Solo escribir si hay cambios
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Corregido: {file_path}")
            return True
        else:
            print(f"⏭️  Sin cambios: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 Corrigiendo get_jwt_identity() en archivos de recursos...")
    
    # Directorio de recursos
    resources_dir = Path("backend/app/resources")
    
    if not resources_dir.exists():
        print(f"❌ Directorio no encontrado: {resources_dir}")
        return
    
    # Buscar archivos Python
    python_files = list(resources_dir.glob("*.py"))
    
    if not python_files:
        print("❌ No se encontraron archivos Python en el directorio de recursos")
        return
    
    fixed_count = 0
    
    for file_path in python_files:
        if file_path.name == "__init__.py":
            continue
            
        if fix_jwt_identity_in_file(file_path):
            fixed_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"   Archivos procesados: {len(python_files) - 1}")  # -1 por __init__.py
    print(f"   Archivos corregidos: {fixed_count}")
    print("✅ Proceso completado")

if __name__ == "__main__":
    main()
