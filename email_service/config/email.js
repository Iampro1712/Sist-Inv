const nodemailer = require('nodemailer');
const logger = require('../utils/logger');

// Configuración del transporter de nodemailer
const createTransporter = () => {
  const config = {
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.SMTP_PORT) || 587,
    secure: process.env.SMTP_SECURE === 'true', // true para 465, false para otros puertos
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  };

  const transporter = nodemailer.createTransporter(config);

  // Verificar la configuración
  transporter.verify((error, success) => {
    if (error) {
      logger.error('Error en configuración SMTP:', error);
    } else {
      logger.info('Servidor SMTP listo para enviar emails');
    }
  });

  return transporter;
};

// Plantillas de email
const emailTemplates = {
  stockBajo: (producto, stockActual, stockMinimo) => ({
    subject: `🚨 Alerta: Stock bajo - ${producto.nombre}`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
          <h2 style="margin: 0;">⚠️ Alerta de Stock Bajo</h2>
        </div>
        
        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
          <h3>Producto: ${producto.nombre}</h3>
          <p><strong>Código:</strong> ${producto.codigo}</p>
          <p><strong>Stock actual:</strong> ${stockActual} unidades</p>
          <p><strong>Stock mínimo:</strong> ${stockMinimo} unidades</p>
          <p><strong>Categoría:</strong> ${producto.categoria || 'N/A'}</p>
          
          <div style="background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <strong>Acción requerida:</strong> Es necesario reabastecer este producto lo antes posible.
          </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px;">
          <p>Sistema de Gestión de Inventario</p>
          <p>Generado automáticamente el ${new Date().toLocaleString()}</p>
        </div>
      </div>
    `,
    text: `
      ALERTA: Stock bajo - ${producto.nombre}
      
      Producto: ${producto.nombre}
      Código: ${producto.codigo}
      Stock actual: ${stockActual} unidades
      Stock mínimo: ${stockMinimo} unidades
      Categoría: ${producto.categoria || 'N/A'}
      
      Acción requerida: Es necesario reabastecer este producto lo antes posible.
      
      Sistema de Gestión de Inventario
      Generado automáticamente el ${new Date().toLocaleString()}
    `
  }),

  vencimiento: (producto, diasRestantes, fechaVencimiento) => ({
    subject: `⏰ Alerta: Producto próximo a vencer - ${producto.nombre}`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #fff3cd; color: #856404; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
          <h2 style="margin: 0;">⏰ Alerta de Vencimiento</h2>
        </div>
        
        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
          <h3>Producto: ${producto.nombre}</h3>
          <p><strong>Código:</strong> ${producto.codigo}</p>
          <p><strong>Días restantes:</strong> ${diasRestantes} días</p>
          <p><strong>Fecha de vencimiento:</strong> ${fechaVencimiento}</p>
          <p><strong>Stock actual:</strong> ${producto.stock || 'N/A'} unidades</p>
          <p><strong>Categoría:</strong> ${producto.categoria || 'N/A'}</p>
          
          <div style="background-color: ${diasRestantes <= 7 ? '#f8d7da' : '#d1ecf1'}; color: ${diasRestantes <= 7 ? '#721c24' : '#0c5460'}; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <strong>Acción requerida:</strong> ${diasRestantes <= 7 ? 'URGENTE - ' : ''}Revisar el producto y tomar las medidas necesarias antes del vencimiento.
          </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px;">
          <p>Sistema de Gestión de Inventario</p>
          <p>Generado automáticamente el ${new Date().toLocaleString()}</p>
        </div>
      </div>
    `,
    text: `
      ALERTA: Producto próximo a vencer - ${producto.nombre}
      
      Producto: ${producto.nombre}
      Código: ${producto.codigo}
      Días restantes: ${diasRestantes} días
      Fecha de vencimiento: ${fechaVencimiento}
      Stock actual: ${producto.stock || 'N/A'} unidades
      Categoría: ${producto.categoria || 'N/A'}
      
      Acción requerida: ${diasRestantes <= 7 ? 'URGENTE - ' : ''}Revisar el producto y tomar las medidas necesarias antes del vencimiento.
      
      Sistema de Gestión de Inventario
      Generado automáticamente el ${new Date().toLocaleString()}
    `
  }),

  reporteInventario: (resumen, fechaGeneracion) => ({
    subject: `📊 Reporte de Inventario - ${new Date(fechaGeneracion).toLocaleDateString()}`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #d4edda; color: #155724; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
          <h2 style="margin: 0;">📊 Reporte de Inventario</h2>
        </div>
        
        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
          <h3>Resumen del Inventario</h3>
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #e9ecef;">
              <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Total de productos</strong></td>
              <td style="padding: 10px; border: 1px solid #dee2e6;">${resumen.total_productos}</td>
            </tr>
            <tr>
              <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Valor total del inventario</strong></td>
              <td style="padding: 10px; border: 1px solid #dee2e6;">$${resumen.valor_total_inventario?.toLocaleString() || '0'}</td>
            </tr>
            <tr style="background-color: #e9ecef;">
              <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Productos con stock bajo</strong></td>
              <td style="padding: 10px; border: 1px solid #dee2e6;">${resumen.productos_stock_bajo}</td>
            </tr>
            <tr>
              <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Productos sin stock</strong></td>
              <td style="padding: 10px; border: 1px solid #dee2e6;">${resumen.productos_sin_stock}</td>
            </tr>
          </table>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px;">
          <p>Sistema de Gestión de Inventario</p>
          <p>Generado el ${new Date(fechaGeneracion).toLocaleString()}</p>
        </div>
      </div>
    `,
    text: `
      REPORTE DE INVENTARIO - ${new Date(fechaGeneracion).toLocaleDateString()}
      
      Resumen del Inventario:
      - Total de productos: ${resumen.total_productos}
      - Valor total del inventario: $${resumen.valor_total_inventario?.toLocaleString() || '0'}
      - Productos con stock bajo: ${resumen.productos_stock_bajo}
      - Productos sin stock: ${resumen.productos_sin_stock}
      
      Sistema de Gestión de Inventario
      Generado el ${new Date(fechaGeneracion).toLocaleString()}
    `
  })
};

module.exports = {
  createTransporter,
  emailTemplates
};
