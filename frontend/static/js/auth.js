// Authentication utilities

// Get token from localStorage
function getToken() {
    try {
        return window.localStorage.getItem('access_token');
    } catch (e) {
        console.error('localStorage not available:', e);
        return null;
    }
}

// Set token in localStorage
function setToken(token) {
    try {
        window.localStorage.setItem('access_token', token);
    } catch (e) {
        console.error('localStorage not available:', e);
    }
}

// Remove token from localStorage
function removeToken() {
    try {
        window.localStorage.removeItem('access_token');
    } catch (e) {
        console.error('localStorage not available:', e);
    }
}

// Setup axios interceptors
function setupAxiosInterceptors() {
    if (typeof axios === 'undefined') {
        console.error('Axios is not loaded yet!');
        return;
    }

    // Request interceptor to add token
    axios.interceptors.request.use(
        (config) => {
            const token = getToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        (error) => {
            return Promise.reject(error);
        }
    );

    // Response interceptor to handle 401 errors
    axios.interceptors.response.use(
        (response) => {
            return response;
        },
        (error) => {
            if (error.response && error.response.status === 401) {
                // Token expired or invalid, redirect to login
                removeToken();
                window.location.href = '/login';
            }
            return Promise.reject(error);
        }
    );
}

// Setup interceptors immediately if axios is available
if (typeof axios !== 'undefined') {
    setupAxiosInterceptors();
}

// Verify token and get user info
async function verifyAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return null;
    }

    try {
        const response = await axios.get('/api/auth/verify', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return response.data;
    } catch (error) {
        console.error('Auth verification failed:', error);
        removeToken();
        window.location.href = '/login';
        return null;
    }
}

// Logout function
async function logout() {
    const token = getToken();
    if (token) {
        try {
            await axios.post('/api/auth/logout', {}, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    removeToken();
    window.location.href = '/login';
}

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Ensure interceptors are setup (in case they weren't set up earlier)
    setupAxiosInterceptors();

    // Verify authentication
    const user = await verifyAuth();
    if (user) {
        // Display username
        const usernameDisplay = document.getElementById('usernameDisplay');
        if (usernameDisplay) {
            usernameDisplay.textContent = user.username;
        }
    }
});
