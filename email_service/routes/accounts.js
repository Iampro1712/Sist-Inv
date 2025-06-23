const express = require('express');
const axios = require('axios');
const Joi = require('joi');
const logger = require('../utils/logger');

const router = express.Router();

// Esquemas de validación
const createAccountSchema = Joi.object({
  email: Joi.string().email().required(),
  name: Joi.string().required(),
  domain: Joi.string().default(process.env.EMAIL_DOMAIN),
  password: Joi.string().min(8)
});

// Endpoint para crear cuenta de email usando API externa (ejemplo con Mailgun)
router.post('/create', async (req, res) => {
  try {
    // Validar datos de entrada
    const { error, value } = createAccountSchema.validate(req.body);
    if (error) {
      return res.status(400).json({
        error: 'Datos inválidos',
        details: error.details.map(d => d.message)
      });
    }

    const { email, name, domain, password } = value;

    // Verificar que tenemos la configuración necesaria
    if (!process.env.EMAIL_API_KEY || !process.env.EMAIL_API_URL) {
      return res.status(500).json({
        error: 'Configuración de API externa no disponible'
      });
    }

    // Ejemplo de creación de cuenta con Mailgun API
    // Nota: Esto es un ejemplo, debes adaptarlo según la API que uses
    try {
      const response = await axios.post(
        `${process.env.EMAIL_API_URL}/${domain}/credentials`,
        {
          login: email,
          password: password || generateRandomPassword()
        },
        {
          auth: {
            username: 'api',
            password: process.env.EMAIL_API_KEY
          },
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      logger.info('Cuenta de email creada exitosamente', {
        email,
        domain,
        apiResponse: response.status
      });

      res.json({
        success: true,
        message: 'Cuenta de email creada exitosamente',
        account: {
          email,
          name,
          domain,
          created_at: new Date().toISOString()
        }
      });

    } catch (apiError) {
      logger.error('Error creando cuenta en API externa:', {
        error: apiError.message,
        status: apiError.response?.status,
        data: apiError.response?.data
      });

      // Si la API externa falla, podemos simular la creación para desarrollo
      if (process.env.NODE_ENV === 'development') {
        logger.warn('Simulando creación de cuenta para desarrollo');
        
        res.json({
          success: true,
          message: 'Cuenta de email creada exitosamente (simulado)',
          account: {
            email,
            name,
            domain: domain || 'localhost',
            created_at: new Date().toISOString(),
            simulated: true
          }
        });
      } else {
        res.status(500).json({
          error: 'Error creando cuenta en el proveedor de email',
          message: apiError.response?.data?.message || apiError.message
        });
      }
    }

  } catch (error) {
    logger.error('Error en creación de cuenta:', error);
    res.status(500).json({
      error: 'Error interno del servidor',
      message: error.message
    });
  }
});

// Endpoint para listar cuentas existentes
router.get('/list', async (req, res) => {
  try {
    const domain = req.query.domain || process.env.EMAIL_DOMAIN;

    if (!process.env.EMAIL_API_KEY || !process.env.EMAIL_API_URL) {
      return res.status(500).json({
        error: 'Configuración de API externa no disponible'
      });
    }

    try {
      const response = await axios.get(
        `${process.env.EMAIL_API_URL}/${domain}/credentials`,
        {
          auth: {
            username: 'api',
            password: process.env.EMAIL_API_KEY
          }
        }
      );

      res.json({
        success: true,
        accounts: response.data.items || [],
        total: response.data.total_count || 0
      });

    } catch (apiError) {
      logger.error('Error obteniendo lista de cuentas:', apiError);

      // Simulación para desarrollo
      if (process.env.NODE_ENV === 'development') {
        res.json({
          success: true,
          accounts: [
            {
              login: 'admin@localhost',
              created_at: new Date().toISOString(),
              simulated: true
            }
          ],
          total: 1,
          simulated: true
        });
      } else {
        res.status(500).json({
          error: 'Error obteniendo lista de cuentas',
          message: apiError.response?.data?.message || apiError.message
        });
      }
    }

  } catch (error) {
    logger.error('Error listando cuentas:', error);
    res.status(500).json({
      error: 'Error interno del servidor',
      message: error.message
    });
  }
});

// Endpoint para eliminar cuenta
router.delete('/:email', async (req, res) => {
  try {
    const { email } = req.params;
    const domain = req.query.domain || process.env.EMAIL_DOMAIN;

    if (!email) {
      return res.status(400).json({
        error: 'Email es requerido'
      });
    }

    if (!process.env.EMAIL_API_KEY || !process.env.EMAIL_API_URL) {
      return res.status(500).json({
        error: 'Configuración de API externa no disponible'
      });
    }

    try {
      await axios.delete(
        `${process.env.EMAIL_API_URL}/${domain}/credentials/${email}`,
        {
          auth: {
            username: 'api',
            password: process.env.EMAIL_API_KEY
          }
        }
      );

      logger.info('Cuenta de email eliminada', { email, domain });

      res.json({
        success: true,
        message: 'Cuenta eliminada exitosamente'
      });

    } catch (apiError) {
      logger.error('Error eliminando cuenta:', apiError);

      if (process.env.NODE_ENV === 'development') {
        res.json({
          success: true,
          message: 'Cuenta eliminada exitosamente (simulado)',
          simulated: true
        });
      } else {
        res.status(500).json({
          error: 'Error eliminando cuenta',
          message: apiError.response?.data?.message || apiError.message
        });
      }
    }

  } catch (error) {
    logger.error('Error eliminando cuenta:', error);
    res.status(500).json({
      error: 'Error interno del servidor',
      message: error.message
    });
  }
});

// Función auxiliar para generar contraseña aleatoria
function generateRandomPassword(length = 12) {
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
  let password = '';
  for (let i = 0; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length));
  }
  return password;
}

module.exports = router;
