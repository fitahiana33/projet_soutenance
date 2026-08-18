/**
 * systemService.js - Service layer for System Parameters & Maintenance API calls
 */
import api from './api'

const systemService = {
  // ── Parameters (PostgreSQL CRUD) ──────────────────────────────────────────
  /**
   * Get all parameters as raw objects from PostgreSQL
   * @param {string|null} category - Optional category filter
   */
  getParameters(category = null) {
    const params = { raw: true }
    if (category) params.category = category
    return api.get('/system/parameters', { params })
  },

  /** Get computed key/value dict (used by payroll engine) */
  getParametersDict() {
    return api.get('/system/parameters')
  },

  createParameter(payload) {
    return api.post('/system/parameters', payload)
  },

  updateParameter(id, payload) {
    return api.put(`/system/parameters/${id}`, payload)
  },

  deleteParameter(id) {
    return api.delete(`/system/parameters/${id}`)
  },

  bulkUpdateParameters(payload) {
    return api.put('/system/parameters', payload)
  },

  // ── Data Reset ────────────────────────────────────────────────────────────
  resetAllData(confirmText) {
    return api.post('/system/reset-data', { confirm_text: confirmText })
  }
}

export default systemService
