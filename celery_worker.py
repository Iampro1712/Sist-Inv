#!/usr/bin/env python3
"""
Worker de Celery para el Sistema de Inventario
"""

import os
from backend.app import create_app, make_celery

# Crear aplicación Flask
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Crear instancia de Celery
celery = make_celery(app)

# Importar tareas
from backend.app.tasks.alertas_tasks import (
    generar_alertas_automaticas,
    enviar_notificacion_email,
    limpiar_alertas_resueltas
)

# Configurar tareas periódicas
from celery.schedules import crontab

celery.conf.beat_schedule = {
    # Generar alertas cada hora
    'generar-alertas-automaticas': {
        'task': 'backend.app.tasks.alertas_tasks.generar_alertas_automaticas',
        'schedule': crontab(minute=0),  # Cada hora en punto
    },
    # Limpiar alertas resueltas cada día a las 2 AM
    'limpiar-alertas-resueltas': {
        'task': 'backend.app.tasks.alertas_tasks.limpiar_alertas_resueltas',
        'schedule': crontab(hour=2, minute=0),  # Todos los días a las 2:00 AM
    },
}

celery.conf.timezone = 'UTC'

if __name__ == '__main__':
    celery.start()
