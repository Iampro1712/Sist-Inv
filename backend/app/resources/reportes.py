from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.app.models.producto import Producto
from backend.app.models.movimiento import Movimiento
from backend.app.models.categoria import Categoria
from backend.app.models.usuario import Usuario
import pandas as pd
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/inventario', methods=['GET'])
@jwt_required()
def reporte_inventario():
    """Generar reporte de inventario actual"""
    try:
        categoria_id = request.args.get('categoria_id', type=int)
        formato = request.args.get('formato', 'json')  # json, excel, pdf
        
        query = Producto.query.filter_by(activo=True)
        
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        productos = query.all()
        
        # Calcular totales
        total_productos = len(productos)
        valor_total_inventario = sum(producto.valor_inventario for producto in productos)
        productos_stock_bajo = sum(1 for producto in productos if producto.necesita_restock)
        productos_sin_stock = sum(1 for producto in productos if producto.stock_actual == 0)
        
        data = {
            'fecha_generacion': datetime.now().isoformat(),
            'resumen': {
                'total_productos': total_productos,
                'valor_total_inventario': valor_total_inventario,
                'productos_stock_bajo': productos_stock_bajo,
                'productos_sin_stock': productos_sin_stock
            },
            'productos': [producto.to_dict() for producto in productos]
        }
        
        if formato == 'json':
            return jsonify(data), 200
        
        elif formato == 'excel':
            # Crear DataFrame
            df_productos = pd.DataFrame([producto.to_dict() for producto in productos])
            
            # Crear archivo Excel en memoria
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_productos.to_excel(writer, sheet_name='Inventario', index=False)
                
                # Crear hoja de resumen
                df_resumen = pd.DataFrame([data['resumen']])
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
        
        elif formato == 'pdf':
            # Crear PDF en memoria
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title = Paragraph("Reporte de Inventario", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Fecha
            fecha = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
            story.append(fecha)
            story.append(Spacer(1, 12))
            
            # Resumen
            resumen_data = [
                ['Métrica', 'Valor'],
                ['Total de productos', str(data['resumen']['total_productos'])],
                ['Valor total del inventario', f"${data['resumen']['valor_total_inventario']:,.2f}"],
                ['Productos con stock bajo', str(data['resumen']['productos_stock_bajo'])],
                ['Productos sin stock', str(data['resumen']['productos_sin_stock'])]
            ]
            
            resumen_table = Table(resumen_data)
            resumen_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(resumen_table)
            story.append(Spacer(1, 20))
            
            # Tabla de productos (solo los primeros 50 para evitar PDFs muy grandes)
            productos_limitados = productos[:50]
            productos_data = [['Código', 'Nombre', 'Categoría', 'Stock', 'Precio', 'Valor']]
            
            for producto in productos_limitados:
                productos_data.append([
                    producto.codigo,
                    producto.nombre[:30] + '...' if len(producto.nombre) > 30 else producto.nombre,
                    producto.categoria.nombre if producto.categoria else 'N/A',
                    str(producto.stock_actual),
                    f"${producto.precio_compra or 0:.2f}",
                    f"${producto.valor_inventario:.2f}"
                ])
            
            productos_table = Table(productos_data)
            productos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(productos_table)
            
            if len(productos) > 50:
                nota = Paragraph(f"Nota: Se muestran los primeros 50 productos de {len(productos)} total.", styles['Normal'])
                story.append(Spacer(1, 12))
                story.append(nota)
            
            doc.build(story)
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )
        
        else:
            return jsonify({'error': 'Formato no soportado. Use: json, excel, pdf'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reportes_bp.route('/movimientos', methods=['GET'])
@jwt_required()
def reporte_movimientos():
    """Generar reporte de movimientos de stock"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        producto_id = request.args.get('producto_id', type=int)
        tipo = request.args.get('tipo')
        formato = request.args.get('formato', 'json')
        
        # Fechas por defecto (último mes)
        if not fecha_desde:
            fecha_desde = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not fecha_hasta:
            fecha_hasta = date.today().strftime('%Y-%m-%d')
        
        query = Movimiento.query
        
        # Aplicar filtros
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        
        query = query.filter(
            Movimiento.fecha_movimiento.between(fecha_desde_dt, fecha_hasta_dt)
        )
        
        if producto_id:
            query = query.filter_by(producto_id=producto_id)
        
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        movimientos = query.order_by(Movimiento.fecha_movimiento.desc()).all()
        
        # Calcular estadísticas
        total_entradas = sum(1 for m in movimientos if m.tipo == 'entrada')
        total_salidas = sum(1 for m in movimientos if m.tipo == 'salida')
        total_ajustes = sum(1 for m in movimientos if m.tipo == 'ajuste')
        
        valor_entradas = sum(m.valor_total for m in movimientos if m.tipo == 'entrada' and m.precio_unitario)
        valor_salidas = sum(m.valor_total for m in movimientos if m.tipo == 'salida' and m.precio_unitario)
        
        data = {
            'fecha_generacion': datetime.now().isoformat(),
            'periodo': {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta
            },
            'resumen': {
                'total_movimientos': len(movimientos),
                'entradas': {
                    'cantidad': total_entradas,
                    'valor': valor_entradas
                },
                'salidas': {
                    'cantidad': total_salidas,
                    'valor': valor_salidas
                },
                'ajustes': {
                    'cantidad': total_ajustes
                }
            },
            'movimientos': [movimiento.to_dict() for movimiento in movimientos]
        }
        
        if formato == 'json':
            return jsonify(data), 200
        
        elif formato == 'excel':
            df_movimientos = pd.DataFrame([movimiento.to_dict() for movimiento in movimientos])
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_movimientos.to_excel(writer, sheet_name='Movimientos', index=False)
                
                df_resumen = pd.DataFrame([data['resumen']])
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'movimientos_{fecha_desde}_{fecha_hasta}.xlsx'
            )
        
        else:
            return jsonify({'error': 'Formato no soportado. Use: json, excel'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
