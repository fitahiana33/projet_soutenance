/**
 * hrService.js - Service layer for Human Resources & Payroll API calls
 */
import api from './api'

const hrService = {
  // ── Overview & Dashboard ─────────────────────────────────────────────────
  getOverview() {
    return api.get('/hr/overview')
  },

  // ── Employees ─────────────────────────────────────────────────────────────
  getEmployees() {
    return api.get('/hr/employees')
  },

  getEmployee(id) {
    return api.get(`/hr/employees/${id}`)
  },

  createEmployee(payload) {
    return api.post('/hr/employees', payload)
  },

  // ── Time Off / Leave ──────────────────────────────────────────────────────
  getTimeOff() {
    return api.get('/hr/time-off')
  },

  createTimeOff(payload) {
    return api.post('/hr/time-off', payload)
  },

  validateTimeOff(id, payload) {
    return api.put(`/hr/time-off/${id}/validate`, payload)
  },

  // ── Payrolls ──────────────────────────────────────────────────────────────
  getPayrolls() {
    return api.get('/hr/payrolls')
  },

  createPayroll(payload) {
    return api.post('/hr/payrolls', payload)
  },

  // ── Performance Evaluations ───────────────────────────────────────────────
  getPerformance() {
    return api.get('/hr/performance')
  },

  createEvaluation(payload) {
    return api.post('/hr/performance', payload)
  },

  // ── Public Holidays (PostgreSQL CRUD) ─────────────────────────────────────
  getHolidays() {
    return api.get('/hr/holidays/')
  },

  createHoliday(payload) {
    return api.post('/hr/holidays/', payload)
  },

  updateHoliday(id, payload) {
    return api.put(`/hr/holidays/${id}`, payload)
  },

  deleteHoliday(id) {
    return api.delete(`/hr/holidays/${id}`)
  }
}

export default hrService
