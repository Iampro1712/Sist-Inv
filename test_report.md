
# Reporte de Pruebas - Sistema de Inventario

Fecha: 2025-06-23 11:52:14

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
