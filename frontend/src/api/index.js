import axios from 'axios'

// All requests go to the nginx proxy at port 3000
// nginx routes /api/auth/* → auth-service, etc.
// This means zero CORS issues — everything is same-origin.
const api = axios.create({ baseURL: '/api' })

// Attach JWT to every request if one is stored
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401, clear stored tokens and redirect to login
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_id')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  refresh: () => api.post('/auth/refresh'),
}

// ── Users ─────────────────────────────────────────────────────────
export const usersApi = {
  getProfile: (userId) => api.get(`/users/${userId}`),
  updateProfile: (userId, data) => api.patch(`/users/${userId}`, data),
}

// ── Products ──────────────────────────────────────────────────────
export const productsApi = {
  listCategories: () => api.get('/products/categories'),
  listProducts: (categoryId) =>
    api.get('/products/products', { params: categoryId ? { category_id: categoryId } : {} }),
  getProduct: (id) => api.get(`/products/products/${id}`),
}

// ── Orders / Cart ─────────────────────────────────────────────────
export const ordersApi = {
  getCart: () => api.get('/orders/cart'),
  addToCart: (data) => api.post('/orders/cart/items', data),
  removeFromCart: (itemId) => api.delete(`/orders/cart/items/${itemId}`),
  checkout: () => api.post('/orders/checkout'),
  listOrders: () => api.get('/orders/orders'),
  getOrder: (id) => api.get(`/orders/orders/${id}`),
}

// ── Payments ──────────────────────────────────────────────────────
export const paymentsApi = {
  getPaymentByOrder: (orderId) => api.get(`/payments/payments/order/${orderId}`),
}

export default api
