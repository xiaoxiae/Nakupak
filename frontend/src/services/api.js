import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const auth = {
  create: () => api.post('/api/auth/create'),
  join: (token) => api.post('/api/auth/join', { token }),
  me: () => api.get('/api/auth/me'),
}

export const categories = {
  list: () => api.get('/api/categories'),
  create: (data) => api.post('/api/categories', data),
  update: (id, data) => api.put(`/api/categories/${id}`, data),
  delete: (id) => api.delete(`/api/categories/${id}`),
}

export const items = {
  list: () => api.get('/api/items'),
  create: (data) => api.post('/api/items', data),
  update: (id, data) => api.put(`/api/items/${id}`, data),
  delete: (id) => api.delete(`/api/items/${id}`),
  merge: (targetId, sourceIds) => api.post(`/api/items/${targetId}/merge`, { source_ids: sourceIds }),
  bulkDelete: (ids) => api.post('/api/items/delete', { ids }),
  bulkSetCategory: (itemIds, categoryId) => api.post('/api/items/set-category', { item_ids: itemIds, category_id: categoryId }),
}

export const shoppingList = {
  get: () => api.get('/api/list'),
  add: (items) => api.post('/api/list/add', { items }),
  update: (id, quantity) => api.put(`/api/list/${id}`, { quantity }),
  remove: (id) => api.delete(`/api/list/${id}`),
  addRecipe: (recipeId) => api.post(`/api/list/add-recipe/${recipeId}`),
  bulkRemove: (ids) => api.post('/api/list/remove', { ids }),
  clear: () => api.delete('/api/list'),
}

export const pool = {
  get: () => api.get('/api/pool'),
}

export const recipes = {
  list: () => api.get('/api/recipes'),
  create: (data) => api.post('/api/recipes', data),
  update: (id, data) => api.put(`/api/recipes/${id}`, data),
  delete: (id) => api.delete(`/api/recipes/${id}`),
}

export const sessions = {
  start: () => api.post('/api/session/start'),
  getActive: () => api.get('/api/session/active'),
  toggleCheck: (itemId) => api.put(`/api/session/check/${itemId}`),
  complete: () => api.post('/api/session/complete'),
  abort: () => api.delete('/api/session/active'),
  list: () => api.get('/api/sessions'),
  delete: (id) => api.delete(`/api/sessions/${id}`),
}

export default api
