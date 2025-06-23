from datetime import datetime, date, timedelta
from celery import Celery
from backend.app import create_app, db
from backend.app.models.producto import Producto
from backend.app.models.alerta import Alerta
from backend.app.models.usuario import Usuario
from flask_mail import Message, Mail

# Crear aplicación Flask para el contexto de Celery
app = create_app()
celery = Celery(app.import_name)
celery.conf.update(app.config)

class ContextTask(celery.Task):
    """Tarea que mantiene el contexto de la aplicación Flask"""
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

@celery.task
def generar_alertas_automaticas():
    """Tarea para generar alertas automáticas de stock bajo y vencimientos"""
    try:
        with app.app_context():
            alertas_creadas = 0
            
            # Obtener usuario admin para crear las alertas
            admin_user = Usuario.query.filter_by(rol='admin').first()
            if not admin_user:
                return {'error': 'No se encontró usuario administrador'}
            
            # Buscar productos con stock bajo o sin stock
            productos_stock_bajo = Producto.query.filter(
                Producto.stock_actual <= Producto.stock_minimo,
                Producto.activo == True
            ).all()
            
            for producto in productos_stock_bajo:
                # Verificar si ya existe una alerta activa para este producto
                alerta_existente = Alerta.query.filter_by(
                    producto_id=producto.id,
                    tipo='stock_bajo' if producto.stock_actual > 0 else 'sin_stock',
                    activa=True
                ).first()
                
                if not alerta_existente:
                    if producto.stock_actual == 0:
                        tipo = 'sin_stock'
                        titulo = f'Sin stock: {producto.nombre}'
                        mensaje = f'El producto {producto.codigo} - {producto.nombre} no tiene stock disponible.'
                        prioridad = 'critica'
                    else:
                        tipo = 'stock_bajo'
                        titulo = f'Stock bajo: {producto.nombre}'
                        mensaje = f'El producto {producto.codigo} - {producto.nombre} tiene stock bajo. Stock actual: {producto.stock_actual}, Stock mínimo: {producto.stock_minimo}'
                        prioridad = 'alta'
                    
                    alerta = Alerta(
                        producto_id=producto.id,
                        usuario_id=admin_user.id,
                        tipo=tipo,
                        titulo=titulo,
                        mensaje=mensaje,
                        prioridad=prioridad
                    )
                    
                    db.session.add(alerta)
                    alertas_creadas += 1
            
            # Buscar productos próximos a vencer (30 días)
            fecha_limite = date.today()
            fecha_limite_vencimiento = fecha_limite + timedelta(days=30)
            
            productos_por_vencer = Producto.query.filter(
                Producto.fecha_vencimiento.between(fecha_limite, fecha_limite_vencimiento),
                Producto.activo == True
            ).all()
            
            for producto in productos_por_vencer:
                # Verificar si ya existe una alerta activa para este producto
                alerta_existente = Alerta.query.filter_by(
                    producto_id=producto.id,
                    tipo='vencimiento',
                    activa=True
                ).first()
                
                if not alerta_existente:
                    dias_restantes = (producto.fecha_vencimiento - fecha_limite).days
                    
                    if dias_restantes <= 7:
                        prioridad = 'critica'
                    elif dias_restantes <= 15:
                        prioridad = 'alta'
                    else:
                        prioridad = 'media'
                    
                    alerta = Alerta(
                        producto_id=producto.id,
                        usuario_id=admin_user.id,
                        tipo='vencimiento',
                        titulo=f'Próximo a vencer: {producto.nombre}',
                        mensaje=f'El producto {producto.codigo} - {producto.nombre} vence en {dias_restantes} días (Fecha de vencimiento: {producto.fecha_vencimiento})',
                        prioridad=prioridad
                    )
                    
                    db.session.add(alerta)
                    alertas_creadas += 1
            
            # Buscar productos vencidos
            productos_vencidos = Producto.query.filter(
                Producto.fecha_vencimiento < fecha_limite,
                Producto.activo == True
            ).all()
            
            for producto in productos_vencidos:
                # Verificar si ya existe una alerta activa para este producto
                alerta_existente = Alerta.query.filter_by(
                    producto_id=producto.id,
                    tipo='vencido',
                    activa=True
                ).first()
                
                if not alerta_existente:
                    dias_vencido = (fecha_limite - producto.fecha_vencimiento).days
                    
                    alerta = Alerta(
                        producto_id=producto.id,
                        usuario_id=admin_user.id,
                        tipo='vencido',
                        titulo=f'Producto vencido: {producto.nombre}',
                        mensaje=f'El producto {producto.codigo} - {producto.nombre} está vencido desde hace {dias_vencido} días (Fecha de vencimiento: {producto.fecha_vencimiento})',
                        prioridad='critica'
                    )
                    
                    db.session.add(alerta)
                    alertas_creadas += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'alertas_creadas': alertas_creadas,
                'fecha_ejecucion': datetime.now().isoformat()
            }
            
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e),
            'fecha_ejecucion': datetime.now().isoformat()
        }

@celery.task
def enviar_notificacion_email(destinatario, asunto, mensaje):
    """Tarea para enviar notificaciones por email"""
    try:
        with app.app_context():
            mail = Mail(app)
            
            msg = Message(
                subject=asunto,
                recipients=[destinatario],
                body=mensaje,
                sender=app.config['MAIL_USERNAME']
            )
            
            mail.send(msg)
            
            return {
                'success': True,
                'destinatario': destinatario,
                'asunto': asunto,
                'fecha_envio': datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'destinatario': destinatario,
            'fecha_intento': datetime.now().isoformat()
        }

@celery.task
def limpiar_alertas_resueltas():
    """Tarea para limpiar alertas resueltas antiguas (más de 30 días)"""
    try:
        with app.app_context():
            fecha_limite = datetime.now() - timedelta(days=30)
            
            alertas_antiguas = Alerta.query.filter(
                Alerta.resuelta == True,
                Alerta.fecha_resolucion < fecha_limite
            ).all()
            
            alertas_eliminadas = len(alertas_antiguas)
            
            for alerta in alertas_antiguas:
                db.session.delete(alerta)
            
            db.session.commit()
            
            return {
                'success': True,
                'alertas_eliminadas': alertas_eliminadas,
                'fecha_ejecucion': datetime.now().isoformat()
            }
            
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e),
            'fecha_ejecucion': datetime.now().isoformat()
        }
