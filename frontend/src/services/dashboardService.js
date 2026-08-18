/**
 * dashboardService.js - Service layer for Dashboard / BI metrics API calls
 */
import api from './api'

const dashboardService = {
  getSalesOverview() {
    return api.get('/sales/overview')
  },

  getStockOverview() {
    return api.get('/stocks/overview')
  },

  getHROverview() {
    return api.get('/hr/overview')
  },

  getPurchasesOverview() {
    return api.get('/purchases/overview')
  },

  getPurchasesAnalysis() {
    return api.get('/purchases/analysis')
  }
}

export default dashboardService
