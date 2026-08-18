/**
 * productService.js - Service layer for Products & Categories API calls
 */
import api from './api'

const productService = {
  // ── Products ──────────────────────────────────────────────────────────────
  getProducts() {
    return api.get('/products/')
  },

  createProduct(payload) {
    return api.post('/products/', payload)
  },

  updateProduct(id, payload) {
    return api.put(`/products/${id}`, payload)
  },

  deleteProduct(id) {
    return api.delete(`/products/${id}`)
  },

  // ── Stock Movements per Product ───────────────────────────────────────────
  getProductMovements(id) {
    return api.get(`/products/${id}/movements`)
  },

  createProductMovement(id, payload) {
    return api.post(`/products/${id}/movement`, payload)
  },

  // ── Categories ────────────────────────────────────────────────────────────
  getCategories() {
    return api.get('/products/categories')
  },

  createCategory(payload) {
    return api.post('/products/categories', payload)
  },

  updateCategory(id, payload) {
    return api.put(`/products/categories/${id}`, payload)
  },

  deleteCategory(id) {
    return api.delete(`/products/categories/${id}`)
  }
}

export default productService
