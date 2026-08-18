import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

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

export const authApi = {
  register:       (data) => api.post('/auth/register', data),
  login:          (data) => api.post('/auth/login', data),
  refresh:        ()     => api.post('/auth/refresh'),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword:  (data) => api.post('/auth/reset-password', data),
}

export const usersApi = {
  getProfile:    (userId)       => api.get(`/users/${userId}`),
  updateProfile: (userId, data) => api.patch(`/users/${userId}`, data),
}

export const productsApi = {
  listCategories: ()           => api.get('/products/categories'),
  listProducts:   (categoryId) => api.get('/products/products', {
    params: categoryId ? { category_id: categoryId } : {}
  }),
  getProduct: (id) => api.get(`/products/products/${id}`),
}

export const ordersApi = {
  getCart:          ()       => api.get('/orders/cart'),
  addToCart:        (data)   => api.post('/orders/cart/items', data),
  removeFromCart:   (itemId) => api.delete(`/orders/cart/items/${itemId}`),
  checkout:         ()       => api.post('/orders/checkout'),
  listOrders:       ()       => api.get('/orders/orders'),
  listAllOrders:    ()       => api.get('/orders/orders/all'),
  getOrder:         (id)     => api.get(`/orders/orders/${id}`),
  confirmDelivery:  (id)     => api.patch(`/orders/orders/${id}/confirm-delivery`),
}

export const paymentsApi = {
  getPaymentByOrder: (orderId) => api.get(`/payments/payments/order/${orderId}`),
}

export const shippingApi = {
  getShipmentByOrderStaff: (orderId) => api.get(`/shipping/shipments/order/${orderId}/staff`),
  getShipmentByOrder: (orderId)  => api.get(`/shipping/shipments/order/${orderId}`),
  createShipment:     (data)     => api.post('/shipping/shipments', data),
  dispatchShipment:   (id, data) => api.patch(`/shipping/shipments/${id}/dispatch`, data),
  notifyCustomer:     (id, data) => api.patch(`/shipping/shipments/${id}/notify-customer`, data),
  deliverShipment:    (id, data) => api.patch(`/shipping/shipments/${id}/deliver`, data),
  getShipment:        (id)       => api.get(`/shipping/shipments/${id}`),
}

export default api
