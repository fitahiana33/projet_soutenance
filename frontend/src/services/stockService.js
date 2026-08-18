/**
 * stockService.js - Service layer for Stocks & Inventory API calls
 */
import api from './api'

const stockService = {
  getOverview() {
    return api.get('/stocks/overview')
  },

  getProducts() {
    return api.get('/products/')
  },

  /**
   * Get stock movements with optional filters
   * @param {object} filters - e.g. { product_id, movement_type, page }
   */
  getMovements(filters = {}) {
    return api.get('/stocks/movements', { params: filters })
  },

  createMovement(payload) {
    return api.post('/stocks/movements', payload)
  },

  getValuation() {
    return api.get('/stocks/valuation')
  },

  getRotation() {
    return api.get('/stocks/rotation')
  },

  getLots() {
    return api.get('/stocks/lots')
  },

  createLot(payload) {
    return api.post('/stocks/lots', payload)
  }
}

export default stockService
