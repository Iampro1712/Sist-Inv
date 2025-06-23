# 🚀 Sistema de Gestión de Inventario

Un sistema completo de gestión de inventario desarrollado con **Python**, **MySQL**, **Flask-RESTful**, **Celery** y un frontend moderno y responsive.

## ✨ Características Principales

### 🎯 Funcionalidades Core
- **Gestión de Productos**: CRUD completo con códigos, categorías, precios y ubicaciones
- **Control de Stock**: Seguimiento en tiempo real con niveles mínimos configurables
- **Movimientos de Inventario**: Entradas, salidas y ajustes con historial completo
- **Alertas Automáticas**: Notificaciones por stock bajo, productos vencidos y próximos a vencer
- **Reportes Avanzados**: Generación de reportes en PDF, Excel y JSON
- **Dashboard Interactivo**: Gráficos y estadísticas en tiempo real

### 🔧 Tecnologías Utilizadas

#### Backend
- **Python 3.8+** - Lenguaje principal
- **Flask** - Framework web
- **Flask-RESTful** - API REST
- **SQLAlchemy** - ORM para base de datos
- **MySQL** - Base de datos principal
- **Celery** - Tareas asíncronas
- **Redis** - Broker para Celery
- **JWT** - Autenticación

#### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **Bootstrap 5** - Framework CSS responsive
- **JavaScript ES6+** - Interactividad
- **Chart.js** - Gráficos y visualizaciones
- **Font Awesome** - Iconografía

#### Servicios Adicionales
- **Node.js** - Servicio de email
- **Nodemailer** - Envío de emails
- **APIs Externas** - Gestión de cuentas de email

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.8 o superior
- MySQL 5.7 o superior
- Redis Server
- Node.js 14 o superior
- Git

### Instalación Automática

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/sistema-inventario.git
cd sistema-inventario

# Ejecutar script de instalación
python setup.py
```

### Instalación Manual

1. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows
```

2. **Instalar dependencias de Python**
```bash
pip install -r requirements.txt
```

3. **Instalar dependencias de Node.js**
```bash
cd email_service
npm install
cd ..
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
cp email_service/.env.example email_service/.env
```

5. **Configurar base de datos**
```bash
# Editar .env con credenciales de MySQL
# Crear base de datos
python app.py init-db
python app.py create-admin
```

## ⚙️ Configuración

### Variables de Entorno Principales

```env
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=inventario_db
DB_USER=root
DB_PASSWORD=tu_password

# JWT
JWT_SECRET_KEY=tu_jwt_secret_key

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_app
```

## 🏃‍♂️ Ejecución

### Opción 1: Scripts Automáticos
```bash
# Servidor Flask
./start_flask.sh

# Celery Worker (nueva terminal)
./start_celery.sh

# Celery Beat (nueva terminal)
./start_beat.sh

# Servicio de Email (nueva terminal)
./start_email.sh
```

### Opción 2: Manual
```bash
# Terminal 1: Servidor Flask
source venv/bin/activate
python app.py

# Terminal 2: Celery Worker
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info

# Terminal 3: Celery Beat
source venv/bin/activate
celery -A celery_worker.celery beat --loglevel=info

# Terminal 4: Servicio de Email
cd email_service
npm start
```

## 🌐 Acceso a la Aplicación

- **URL Principal**: http://localhost:5000
- **API REST**: http://localhost:5000/api
- **Servicio Email**: http://localhost:3001
- **Credenciales por defecto**:
  - Usuario: `admin`
  - Contraseña: `admin123`

## 📊 Estructura del Proyecto

```
sistema-inventario/
├── backend/
│   ├── app/
│   │   ├── models/          # Modelos de base de datos
│   │   ├── resources/       # Endpoints de la API
│   │   ├── tasks/           # Tareas de Celery
│   │   └── utils/           # Utilidades
│   └── config/              # Configuraciones
├── frontend/
│   ├── static/
│   │   ├── css/             # Estilos personalizados
│   │   ├── js/              # JavaScript
│   │   └── images/          # Imágenes
│   └── templates/           # Plantillas HTML
├── email_service/           # Servicio de email Node.js
├── tests/                   # Pruebas unitarias
├── docs/                    # Documentación
├── app.py                   # Aplicación principal
├── celery_worker.py         # Worker de Celery
├── requirements.txt         # Dependencias Python
└── setup.py                 # Script de instalación
```

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `GET /api/auth/profile` - Obtener perfil
- `PUT /api/auth/profile` - Actualizar perfil

### Productos
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto
- `GET /api/productos/{id}` - Obtener producto
- `PUT /api/productos/{id}` - Actualizar producto
- `POST /api/productos/{id}/stock` - Actualizar stock

### Movimientos
- `GET /api/movimientos` - Historial de movimientos
- `GET /api/movimientos/estadisticas` - Estadísticas

### Alertas
- `GET /api/alertas` - Listar alertas
- `POST /api/alertas/generar` - Generar alertas automáticas
- `POST /api/alertas/{id}/resolver` - Resolver alerta

### Reportes
- `GET /api/reportes/inventario` - Reporte de inventario
- `GET /api/reportes/movimientos` - Reporte de movimientos

## 🎨 Características del Frontend

### Diseño Responsive
- **Mobile First**: Optimizado para dispositivos móviles
- **Bootstrap 5**: Framework CSS moderno
- **Componentes Reutilizables**: Interfaz consistente

### Funcionalidades Interactivas
- **Dashboard en Tiempo Real**: Gráficos y estadísticas actualizadas
- **Búsqueda Avanzada**: Filtros múltiples y búsqueda instantánea
- **Notificaciones**: Alertas visuales y sonoras
- **Modo Oscuro**: Soporte para preferencias del usuario

### Experiencia de Usuario
- **Navegación Intuitiva**: Menús organizados y accesibles
- **Feedback Visual**: Indicadores de estado y progreso
- **Validación en Tiempo Real**: Formularios inteligentes
- **Accesibilidad**: Cumple estándares WCAG

## 🔔 Sistema de Alertas

### Tipos de Alertas
- **Stock Bajo**: Cuando el stock actual ≤ stock mínimo
- **Sin Stock**: Cuando el stock actual = 0
- **Próximo a Vencer**: Productos que vencen en 30 días
- **Vencido**: Productos ya vencidos

### Notificaciones
- **Email Automático**: Envío programado de alertas
- **Dashboard**: Notificaciones en tiempo real
- **Badges**: Contadores visuales en la navegación

## 📈 Reportes y Analytics

### Tipos de Reportes
- **Inventario Actual**: Estado completo del inventario
- **Movimientos**: Historial de entradas y salidas
- **Análisis de Tendencias**: Patrones de consumo
- **Productos Críticos**: Items que requieren atención

### Formatos de Exportación
- **PDF**: Reportes formateados para impresión
- **Excel**: Datos para análisis adicional
- **JSON**: Integración con otros sistemas

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
python -m pytest

# Pruebas con cobertura
python -m pytest --cov=backend

# Pruebas específicas
python -m pytest tests/test_productos.py
```

## 🚀 Despliegue en Producción

### Docker (Recomendado)
```bash
# Construir imagen
docker build -t sistema-inventario .

# Ejecutar con docker-compose
docker-compose up -d
```

### Servidor Tradicional
```bash
# Usar Gunicorn para producción
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Equipo de Desarrollo

- **Backend**: Python/Flask/SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript/Bootstrap
- **DevOps**: Docker/CI/CD
- **Testing**: PyTest/Jest

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/sistema-inventario/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/tu-usuario/sistema-inventario/wiki)
- **Email**: soporte@sistema-inventario.com

---

⭐ **¡Si te gusta este proyecto, dale una estrella en GitHub!** ⭐
