const express = require('express');
const Joi = require('joi');
const { createTransporter, emailTemplates } = require('../config/email');
const logger = require('../utils/logger');

const router = express.Router();

// Esquemas de validación
const sendEmailSchema = Joi.object({
  to: Joi.alternatives().try(
    Joi.string().email().required(),
    Joi.array().items(Joi.string().email()).min(1).required()
  ),
  subject: Joi.string().required(),
  text: Joi.string(),
  html: Joi.string(),
  template: Joi.string().valid('stockBajo', 'vencimiento', 'reporteInventario'),
  templateData: Joi.object()
}).or('text', 'html', 'template');

// Endpoint para enviar email personalizado
router.post('/send', async (req, res) => {
  try {
    // Validar datos de entrada
    const { error, value } = sendEmailSchema.validate(req.body);
    if (error) {
      return res.status(400).json({
        error: 'Datos inválidos',
        details: error.details.map(d => d.message)
      });
    }

    const { to, subject, text, html, template, templateData } = value;
    const transporter = createTransporter();

    let emailContent = { subject, text, html };

    // Si se especifica una plantilla, usarla
    if (template && templateData) {
      switch (template) {
        case 'stockBajo':
          emailContent = emailTemplates.stockBajo(
            templateData.producto,
            templateData.stockActual,
            templateData.stockMinimo
          );
          break;
        case 'vencimiento':
          emailContent = emailTemplates.vencimiento(
            templateData.producto,
            templateData.diasRestantes,
            templateData.fechaVencimiento
          );
          break;
        case 'reporteInventario':
          emailContent = emailTemplates.reporteInventario(
            templateData.resumen,
            templateData.fechaGeneracion
          );
          break;
        default:
          return res.status(400).json({
            error: 'Plantilla no válida'
          });
      }
    }

    // Configurar el email
    const mailOptions = {
      from: process.env.SMTP_USER,
      to: Array.isArray(to) ? to.join(', ') : to,
      subject: emailContent.subject,
      text: emailContent.text,
      html: emailContent.html
    };

    // Enviar el email
    const info = await transporter.sendMail(mailOptions);

    logger.info('Email enviado exitosamente', {
      messageId: info.messageId,
      to: mailOptions.to,
      subject: mailOptions.subject
    });

    res.json({
      success: true,
      message: 'Email enviado exitosamente',
      messageId: info.messageId,
      to: mailOptions.to
    });

  } catch (error) {
    logger.error('Error enviando email:', error);
    res.status(500).json({
      error: 'Error enviando email',
      message: error.message
    });
  }
});

// Endpoint para enviar alerta de stock bajo
router.post('/alert/stock-bajo', async (req, res) => {
  try {
    const schema = Joi.object({
      to: Joi.alternatives().try(
        Joi.string().email().required(),
        Joi.array().items(Joi.string().email()).min(1).required()
      ),
      producto: Joi.object({
        nombre: Joi.string().required(),
        codigo: Joi.string().required(),
        categoria: Joi.string()
      }).required(),
      stockActual: Joi.number().integer().min(0).required(),
      stockMinimo: Joi.number().integer().min(0).required()
    });

    const { error, value } = schema.validate(req.body);
    if (error) {
      return res.status(400).json({
        error: 'Datos inválidos',
        details: error.details.map(d => d.message)
      });
    }

    const { to, producto, stockActual, stockMinimo } = value;
    const transporter = createTransporter();

    const emailContent = emailTemplates.stockBajo(producto, stockActual, stockMinimo);

    const mailOptions = {
      from: process.env.SMTP_USER,
      to: Array.isArray(to) ? to.join(', ') : to,
      subject: emailContent.subject,
      text: emailContent.text,
      html: emailContent.html
    };

    const info = await transporter.sendMail(mailOptions);

    logger.info('Alerta de stock bajo enviada', {
      messageId: info.messageId,
      producto: producto.codigo,
      to: mailOptions.to
    });

    res.json({
      success: true,
      message: 'Alerta de stock bajo enviada exitosamente',
      messageId: info.messageId
    });

  } catch (error) {
    logger.error('Error enviando alerta de stock bajo:', error);
    res.status(500).json({
      error: 'Error enviando alerta',
      message: error.message
    });
  }
});

// Endpoint para enviar alerta de vencimiento
router.post('/alert/vencimiento', async (req, res) => {
  try {
    const schema = Joi.object({
      to: Joi.alternatives().try(
        Joi.string().email().required(),
        Joi.array().items(Joi.string().email()).min(1).required()
      ),
      producto: Joi.object({
        nombre: Joi.string().required(),
        codigo: Joi.string().required(),
        categoria: Joi.string(),
        stock: Joi.number().integer().min(0)
      }).required(),
      diasRestantes: Joi.number().integer().required(),
      fechaVencimiento: Joi.string().required()
    });

    const { error, value } = schema.validate(req.body);
    if (error) {
      return res.status(400).json({
        error: 'Datos inválidos',
        details: error.details.map(d => d.message)
      });
    }

    const { to, producto, diasRestantes, fechaVencimiento } = value;
    const transporter = createTransporter();

    const emailContent = emailTemplates.vencimiento(producto, diasRestantes, fechaVencimiento);

    const mailOptions = {
      from: process.env.SMTP_USER,
      to: Array.isArray(to) ? to.join(', ') : to,
      subject: emailContent.subject,
      text: emailContent.text,
      html: emailContent.html
    };

    const info = await transporter.sendMail(mailOptions);

    logger.info('Alerta de vencimiento enviada', {
      messageId: info.messageId,
      producto: producto.codigo,
      diasRestantes,
      to: mailOptions.to
    });

    res.json({
      success: true,
      message: 'Alerta de vencimiento enviada exitosamente',
      messageId: info.messageId
    });

  } catch (error) {
    logger.error('Error enviando alerta de vencimiento:', error);
    res.status(500).json({
      error: 'Error enviando alerta',
      message: error.message
    });
  }
});

// Endpoint para verificar configuración SMTP
router.get('/test', async (req, res) => {
  try {
    const transporter = createTransporter();
    await transporter.verify();
    
    res.json({
      success: true,
      message: 'Configuración SMTP válida'
    });
  } catch (error) {
    logger.error('Error en configuración SMTP:', error);
    res.status(500).json({
      success: false,
      error: 'Error en configuración SMTP',
      message: error.message
    });
  }
});

module.exports = router;
