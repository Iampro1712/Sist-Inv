// Sistema de Inventario - JavaScript Principal

// Configuración global
const API_BASE_URL = '/api';
let authToken = localStorage.getItem('authToken');

// Configuración de axios (si se usa)
if (typeof axios !== 'undefined') {
    axios.defaults.baseURL = API_BASE_URL;
    axios.defaults.headers.common['Authorization'] = authToken ? `Bearer ${authToken}` : '';
}

// Utilidades generales
const Utils = {
    // Mostrar spinner de carga
    showLoading() {
        document.getElementById('loading-spinner').classList.remove('d-none');
    },

    // Ocultar spinner de carga
    hideLoading() {
        document.getElementById('loading-spinner').classList.add('d-none');
    },

    // Mostrar alerta
    showAlert(message, type = 'info', duration = 5000) {
        const alertsContainer = document.getElementById('alerts-container');
        const alertId = 'alert-' + Date.now();
        
        const alertHTML = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)}"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertsContainer.insertAdjacentHTML('beforeend', alertHTML);
        
        // Auto-dismiss después del tiempo especificado
        if (duration > 0) {
            setTimeout(() => {
                const alertElement = document.getElementById(alertId);
                if (alertElement) {
                    const bsAlert = new bootstrap.Alert(alertElement);
                    bsAlert.close();
                }
            }, duration);
        }
    },

    // Obtener icono para tipo de alerta
    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    // Formatear moneda
    formatCurrency(amount) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP'
        }).format(amount || 0);
    },

    // Formatear fecha
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CO', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Formatear fecha solo
    formatDateOnly(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CO');
    },

    // Debounce para búsquedas
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Validar email
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Generar badge de estado de stock
    getStockBadge(stockActual, stockMinimo) {
        if (stockActual === 0) {
            return '<span class="badge bg-danger">Sin Stock</span>';
        } else if (stockActual <= stockMinimo) {
            return '<span class="badge bg-warning">Stock Bajo</span>';
        } else if (stockActual <= stockMinimo * 2) {
            return '<span class="badge bg-info">Stock Medio</span>';
        } else {
            return '<span class="badge bg-success">Stock Alto</span>';
        }
    },

    // Generar badge de prioridad de alerta
    getPriorityBadge(priority) {
        const badges = {
            'critica': '<span class="badge bg-danger">Crítica</span>',
            'alta': '<span class="badge bg-warning">Alta</span>',
            'media': '<span class="badge bg-info">Media</span>',
            'baja': '<span class="badge bg-secondary">Baja</span>'
        };
        return badges[priority] || badges['media'];
    }
};

// API Helper
const API = {
    // Realizar petición GET
    async get(endpoint, params = {}) {
        try {
            Utils.showLoading();
            const url = new URL(API_BASE_URL + endpoint, window.location.origin);
            Object.keys(params).forEach(key => {
                if (params[key] !== null && params[key] !== undefined) {
                    url.searchParams.append(key, params[key]);
                }
            });

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': authToken ? `Bearer ${authToken}` : '',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            Utils.showAlert('Error al cargar datos: ' + error.message, 'danger');
            throw error;
        } finally {
            Utils.hideLoading();
        }
    },

    // Realizar petición POST
    async post(endpoint, data = {}) {
        try {
            Utils.showLoading();
            const response = await fetch(API_BASE_URL + endpoint, {
                method: 'POST',
                headers: {
                    'Authorization': authToken ? `Bearer ${authToken}` : '',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            Utils.showAlert('Error al enviar datos: ' + error.message, 'danger');
            throw error;
        } finally {
            Utils.hideLoading();
        }
    },

    // Realizar petición PUT
    async put(endpoint, data = {}) {
        try {
            Utils.showLoading();
            const response = await fetch(API_BASE_URL + endpoint, {
                method: 'PUT',
                headers: {
                    'Authorization': authToken ? `Bearer ${authToken}` : '',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            Utils.showAlert('Error al actualizar datos: ' + error.message, 'danger');
            throw error;
        } finally {
            Utils.hideLoading();
        }
    },

    // Realizar petición DELETE
    async delete(endpoint) {
        try {
            Utils.showLoading();
            const response = await fetch(API_BASE_URL + endpoint, {
                method: 'DELETE',
                headers: {
                    'Authorization': authToken ? `Bearer ${authToken}` : '',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API DELETE Error:', error);
            Utils.showAlert('Error al eliminar: ' + error.message, 'danger');
            throw error;
        } finally {
            Utils.hideLoading();
        }
    }
};

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticación
    if (!authToken && !window.location.pathname.includes('login')) {
        window.location.href = '/login';
        return;
    }

    // Solo cargar información del usuario si está autenticado
    if (authToken) {
        // Cargar información del usuario
        loadUserInfo();

        // Cargar contador de alertas
        loadAlertsCount();
    }

    // Configurar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Configurar popovers de Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Cargar información del usuario
async function loadUserInfo() {
    try {
        const response = await API.get('/auth/profile');
        const userNameElement = document.getElementById('user-name');
        if (userNameElement && response.nombre) {
            userNameElement.textContent = `${response.nombre} ${response.apellido}`;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Cargar contador de alertas
async function loadAlertsCount() {
    try {
        const response = await API.get('/alertas/estadisticas');
        const alertsCountElement = document.getElementById('alertas-count');
        if (alertsCountElement) {
            alertsCountElement.textContent = response.alertas_no_leidas || 0;
            if (response.alertas_no_leidas > 0) {
                alertsCountElement.classList.add('pulse');
            }
        }
    } catch (error) {
        console.error('Error loading alerts count:', error);
    }
}

// Función global para cerrar sesión
function logout() {
    localStorage.removeItem('authToken');
    Utils.showAlert('Sesión cerrada exitosamente', 'success', 2000);
    setTimeout(() => {
        window.location.href = '/login';
    }, 2000);
}

// Exportar para uso global
window.Utils = Utils;
window.API = API;
