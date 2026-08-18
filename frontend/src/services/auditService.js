/**
 * auditService.js - Service layer for Audit & Traceability API calls
 */
import api from './api'

const auditService = {
  /**
   * Fetch audit logs with optional filters
   * @param {{ module?: string, action?: string, username?: string }} filters
   */
  getLogs(filters = {}) {
    const params = {}
    if (filters.module) params.module = filters.module
    if (filters.action) params.action = filters.action
    if (filters.username) params.username = filters.username
    return api.get('/audit/logs', { params })
  },

  /** Fetch audit statistics */
  getStats() {
    return api.get('/audit/stats')
  }
}

export default auditService
