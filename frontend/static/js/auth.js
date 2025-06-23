// Sistema de Inventario - Autenticación

// Gestión de autenticación
const Auth = {
    // Iniciar sesión
    async login(username, password) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error de autenticación');
            }

            const data = await response.json();
            
            // Guardar token
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('userData', JSON.stringify(data.usuario));
            
            // Actualizar token global
            authToken = data.access_token;
            
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    // Registrar usuario
    async register(userData) {
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error en el registro');
            }

            return await response.json();
        } catch (error) {
            console.error('Register error:', error);
            throw error;
        }
    },

    // Obtener perfil del usuario
    async getProfile() {
        try {
            const token = localStorage.getItem('authToken');
            if (!token) {
                throw new Error('No hay token de autenticación');
            }

            const response = await fetch('/api/auth/profile', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    this.logout();
                    throw new Error('Sesión expirada');
                }
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al obtener perfil');
            }

            return await response.json();
        } catch (error) {
            console.error('Get profile error:', error);
            throw error;
        }
    },

    // Actualizar perfil
    async updateProfile(profileData) {
        try {
            const token = localStorage.getItem('authToken');
            if (!token) {
                throw new Error('No hay token de autenticación');
            }

            const response = await fetch('/api/auth/profile', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al actualizar perfil');
            }

            const data = await response.json();
            
            // Actualizar datos locales
            localStorage.setItem('userData', JSON.stringify(data.usuario));
            
            return data;
        } catch (error) {
            console.error('Update profile error:', error);
            throw error;
        }
    },

    // Cambiar contraseña
    async changePassword(currentPassword, newPassword) {
        try {
            const token = localStorage.getItem('authToken');
            if (!token) {
                throw new Error('No hay token de autenticación');
            }

            const response = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al cambiar contraseña');
            }

            return await response.json();
        } catch (error) {
            console.error('Change password error:', error);
            throw error;
        }
    },

    // Cerrar sesión
    logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        authToken = null;
        window.location.href = '/login';
    },

    // Verificar si está autenticado
    isAuthenticated() {
        return !!localStorage.getItem('authToken');
    },

    // Obtener datos del usuario desde localStorage
    getUserData() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    },

    // Verificar rol del usuario
    hasRole(role) {
        const userData = this.getUserData();
        return userData && userData.rol === role;
    },

    // Verificar si tiene permisos (admin o manager)
    hasPermissions() {
        const userData = this.getUserData();
        return userData && (userData.rol === 'admin' || userData.rol === 'manager');
    }
};

// Formulario de login
function setupLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const submitBtn = document.getElementById('loginBtn');
        
        if (!username || !password) {
            Utils.showAlert('Por favor complete todos los campos', 'warning');
            return;
        }

        try {
            // Deshabilitar botón
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Iniciando sesión...';
            
            await Auth.login(username, password);
            
            Utils.showAlert('Inicio de sesión exitoso', 'success');
            
            // Redireccionar después de un breve delay
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
            
        } catch (error) {
            Utils.showAlert(error.message, 'danger');
        } finally {
            // Rehabilitar botón
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Iniciar Sesión';
        }
    });
}

// Formulario de registro
function setupRegisterForm() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(registerForm);
        const userData = Object.fromEntries(formData);
        const submitBtn = document.getElementById('registerBtn');
        
        // Validaciones básicas
        if (userData.password !== userData.confirmPassword) {
            Utils.showAlert('Las contraseñas no coinciden', 'warning');
            return;
        }

        if (userData.password.length < 6) {
            Utils.showAlert('La contraseña debe tener al menos 6 caracteres', 'warning');
            return;
        }

        if (!Utils.isValidEmail(userData.email)) {
            Utils.showAlert('Por favor ingrese un email válido', 'warning');
            return;
        }

        try {
            // Deshabilitar botón
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registrando...';
            
            // Remover confirmPassword antes de enviar
            delete userData.confirmPassword;
            
            await Auth.register(userData);
            
            Utils.showAlert('Registro exitoso. Puede iniciar sesión ahora.', 'success');
            
            // Limpiar formulario
            registerForm.reset();
            
            // Redireccionar al login después de un breve delay
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            
        } catch (error) {
            Utils.showAlert(error.message, 'danger');
        } finally {
            // Rehabilitar botón
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Registrarse';
        }
    });
}

// Formulario de cambio de contraseña
function setupChangePasswordForm() {
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (!changePasswordForm) return;

    changePasswordForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmNewPassword = document.getElementById('confirmNewPassword').value;
        const submitBtn = document.getElementById('changePasswordBtn');
        
        // Validaciones
        if (newPassword !== confirmNewPassword) {
            Utils.showAlert('Las contraseñas nuevas no coinciden', 'warning');
            return;
        }

        if (newPassword.length < 6) {
            Utils.showAlert('La nueva contraseña debe tener al menos 6 caracteres', 'warning');
            return;
        }

        try {
            // Deshabilitar botón
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cambiando...';
            
            await Auth.changePassword(currentPassword, newPassword);
            
            Utils.showAlert('Contraseña cambiada exitosamente', 'success');
            
            // Limpiar formulario
            changePasswordForm.reset();
            
        } catch (error) {
            Utils.showAlert(error.message, 'danger');
        } finally {
            // Rehabilitar botón
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-key"></i> Cambiar Contraseña';
        }
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    setupLoginForm();
    setupRegisterForm();
    setupChangePasswordForm();
    
    // Verificar autenticación en páginas protegidas
    const protectedPages = ['/dashboard', '/productos', '/movimientos', '/alertas', '/reportes'];
    const currentPath = window.location.pathname;
    
    if (protectedPages.some(page => currentPath.startsWith(page))) {
        if (!Auth.isAuthenticated()) {
            window.location.href = '/login';
            return;
        }
    }
    
    // Redireccionar si ya está autenticado y está en login/register
    if ((currentPath === '/login' || currentPath === '/register') && Auth.isAuthenticated()) {
        window.location.href = '/dashboard';
    }
});

// Exportar para uso global
window.Auth = Auth;
