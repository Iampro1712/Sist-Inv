// Dashboard - Sistema de Inventario

let movimientosChart = null;
let categoriasChart = null;

// Inicializar dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    initializeCharts();
});

// Cargar datos del dashboard
async function loadDashboardData() {
    try {
        // Cargar estadísticas generales
        await loadStats();
        
        // Cargar últimos movimientos
        await loadRecentMovements();
        
        // Cargar alertas recientes
        await loadRecentAlerts();
        
        // Cargar datos para gráficos
        await loadChartData();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        Utils.showAlert('Error al cargar datos del dashboard', 'danger');
    }
}

// Cargar estadísticas principales
async function loadStats() {
    try {
        // Obtener productos con filtros para estadísticas
        const productosResponse = await API.get('/productos', { per_page: 1000 });
        const productos = productosResponse.productos || [];
        
        // Calcular estadísticas
        const totalProductos = productos.length;
        const valorInventario = productos.reduce((sum, p) => sum + (p.valor_inventario || 0), 0);
        const stockBajo = productos.filter(p => p.necesita_restock).length;
        
        // Obtener alertas activas
        const alertasResponse = await API.get('/alertas/estadisticas');
        const alertasActivas = alertasResponse.alertas_activas || 0;
        
        // Actualizar elementos del DOM
        updateStatElement('total-productos', totalProductos);
        updateStatElement('valor-inventario', Utils.formatCurrency(valorInventario));
        updateStatElement('stock-bajo', stockBajo);
        updateStatElement('alertas-activas', alertasActivas);
        
    } catch (error) {
        console.error('Error loading stats:', error);
        // Mostrar valores por defecto en caso de error
        updateStatElement('total-productos', '0');
        updateStatElement('valor-inventario', '$0');
        updateStatElement('stock-bajo', '0');
        updateStatElement('alertas-activas', '0');
    }
}

// Actualizar elemento de estadística
function updateStatElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = value;
        element.classList.add('fade-in');
    }
}

// Cargar últimos movimientos
async function loadRecentMovements() {
    try {
        const response = await API.get('/movimientos', { per_page: 5 });
        const movimientos = response.movimientos || [];
        
        const container = document.getElementById('ultimos-movimientos');
        if (!container) return;
        
        if (movimientos.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No hay movimientos recientes</p>';
            return;
        }
        
        const movimientosHTML = movimientos.map(mov => `
            <div class="d-flex align-items-center mb-3 p-2 border-start border-3 ${getBorderColor(mov.tipo)}">
                <div class="me-3">
                    <i class="fas ${getMovementIcon(mov.tipo)} fa-lg ${getIconColor(mov.tipo)}"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="fw-bold">${mov.producto_nombre || 'N/A'}</div>
                    <small class="text-muted">
                        ${mov.tipo.toUpperCase()} - ${mov.cantidad} unidades
                        ${mov.motivo ? `(${mov.motivo})` : ''}
                    </small>
                    <div class="text-xs text-muted">
                        ${Utils.formatDate(mov.fecha_movimiento)}
                    </div>
                </div>
                <div class="text-end">
                    <span class="badge ${getMovementBadge(mov.tipo)}">${mov.tipo}</span>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = movimientosHTML;
        
    } catch (error) {
        console.error('Error loading recent movements:', error);
        const container = document.getElementById('ultimos-movimientos');
        if (container) {
            container.innerHTML = '<p class="text-danger text-center">Error al cargar movimientos</p>';
        }
    }
}

// Cargar alertas recientes
async function loadRecentAlerts() {
    try {
        const response = await API.get('/alertas', { per_page: 5, activas_only: true });
        const alertas = response.alertas || [];
        
        const container = document.getElementById('alertas-recientes');
        if (!container) return;
        
        if (alertas.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No hay alertas activas</p>';
            return;
        }
        
        const alertasHTML = alertas.map(alerta => `
            <div class="d-flex align-items-center mb-3 p-2 border-start border-3 ${getAlertBorderColor(alerta.prioridad)}">
                <div class="me-3">
                    <i class="fas ${getAlertIcon(alerta.tipo)} fa-lg ${getAlertIconColor(alerta.prioridad)}"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="fw-bold">${alerta.titulo}</div>
                    <small class="text-muted">${alerta.producto_nombre || 'N/A'}</small>
                    <div class="text-xs text-muted">
                        ${Utils.formatDate(alerta.fecha_creacion)}
                    </div>
                </div>
                <div class="text-end">
                    ${Utils.getPriorityBadge(alerta.prioridad)}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = alertasHTML;
        
    } catch (error) {
        console.error('Error loading recent alerts:', error);
        const container = document.getElementById('alertas-recientes');
        if (container) {
            container.innerHTML = '<p class="text-danger text-center">Error al cargar alertas</p>';
        }
    }
}

// Inicializar gráficos
function initializeCharts() {
    // Configuración común para gráficos
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.color = '#858796';
}

// Cargar datos para gráficos
async function loadChartData() {
    try {
        // Cargar datos de movimientos para el gráfico de líneas
        await loadMovimientosChart();
        
        // Cargar datos de categorías para el gráfico de dona
        await loadCategoriasChart();
        
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

// Cargar gráfico de movimientos
async function loadMovimientosChart() {
    try {
        // Obtener datos de los últimos 7 días
        const fechaHasta = new Date().toISOString().split('T')[0];
        const fechaDesde = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        
        const response = await API.get('/movimientos/estadisticas', {
            fecha_desde: fechaDesde,
            fecha_hasta: fechaHasta
        });
        
        const ctx = document.getElementById('movimientosChart');
        if (!ctx) return;
        
        // Datos de ejemplo (en una implementación real, necesitarías agrupar por día)
        const labels = [];
        const entradasData = [];
        const salidasData = [];
        
        // Generar etiquetas para los últimos 7 días
        for (let i = 6; i >= 0; i--) {
            const fecha = new Date(Date.now() - i * 24 * 60 * 60 * 1000);
            labels.push(fecha.toLocaleDateString('es-CO', { month: 'short', day: 'numeric' }));
            entradasData.push(Math.floor(Math.random() * 20) + 5); // Datos de ejemplo
            salidasData.push(Math.floor(Math.random() * 15) + 3); // Datos de ejemplo
        }
        
        if (movimientosChart) {
            movimientosChart.destroy();
        }
        
        movimientosChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Entradas',
                    data: entradasData,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Salidas',
                    data: salidasData,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading movimientos chart:', error);
    }
}

// Cargar gráfico de categorías
async function loadCategoriasChart() {
    try {
        const response = await API.get('/categorias');
        const categorias = response.categorias || [];
        
        const ctx = document.getElementById('categoriasChart');
        if (!ctx) return;
        
        // Obtener productos por categoría
        const productosResponse = await API.get('/productos', { per_page: 1000 });
        const productos = productosResponse.productos || [];
        
        // Contar productos por categoría
        const categoriaCount = {};
        productos.forEach(producto => {
            const categoriaNombre = producto.categoria_nombre || 'Sin categoría';
            categoriaCount[categoriaNombre] = (categoriaCount[categoriaNombre] || 0) + 1;
        });
        
        const labels = Object.keys(categoriaCount);
        const data = Object.values(categoriaCount);
        const colors = [
            '#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8',
            '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
        ];
        
        if (categoriasChart) {
            categoriasChart.destroy();
        }
        
        categoriasChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading categorias chart:', error);
    }
}

// Funciones auxiliares para estilos
function getBorderColor(tipo) {
    const colors = {
        'entrada': 'border-success',
        'salida': 'border-warning',
        'ajuste': 'border-info'
    };
    return colors[tipo] || 'border-secondary';
}

function getMovementIcon(tipo) {
    const icons = {
        'entrada': 'fa-arrow-up',
        'salida': 'fa-arrow-down',
        'ajuste': 'fa-edit'
    };
    return icons[tipo] || 'fa-exchange-alt';
}

function getIconColor(tipo) {
    const colors = {
        'entrada': 'text-success',
        'salida': 'text-warning',
        'ajuste': 'text-info'
    };
    return colors[tipo] || 'text-secondary';
}

function getMovementBadge(tipo) {
    const badges = {
        'entrada': 'bg-success',
        'salida': 'bg-warning',
        'ajuste': 'bg-info'
    };
    return badges[tipo] || 'bg-secondary';
}

function getAlertBorderColor(prioridad) {
    const colors = {
        'critica': 'border-danger',
        'alta': 'border-warning',
        'media': 'border-info',
        'baja': 'border-secondary'
    };
    return colors[prioridad] || 'border-info';
}

function getAlertIcon(tipo) {
    const icons = {
        'stock_bajo': 'fa-exclamation-triangle',
        'sin_stock': 'fa-times-circle',
        'vencimiento': 'fa-clock',
        'vencido': 'fa-ban'
    };
    return icons[tipo] || 'fa-bell';
}

function getAlertIconColor(prioridad) {
    const colors = {
        'critica': 'text-danger',
        'alta': 'text-warning',
        'media': 'text-info',
        'baja': 'text-secondary'
    };
    return colors[prioridad] || 'text-info';
}

// Funciones globales para botones del dashboard
function refreshDashboard() {
    Utils.showAlert('Actualizando dashboard...', 'info', 2000);
    loadDashboardData();
}

async function generateAlerts() {
    try {
        Utils.showLoading();
        const response = await API.post('/alertas/generar');
        Utils.showAlert(`Se generaron ${response.alertas_creadas} nuevas alertas`, 'success');
        
        // Recargar datos del dashboard
        await loadDashboardData();
        
    } catch (error) {
        console.error('Error generating alerts:', error);
        Utils.showAlert('Error al generar alertas', 'danger');
    } finally {
        Utils.hideLoading();
    }
}
