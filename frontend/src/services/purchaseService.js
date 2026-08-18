/**
 * purchaseService.js - Service layer for Purchases & Procurement API calls
 */
import api from './api'

const purchaseService = {
  // ── Overview & Analysis ───────────────────────────────────────────────────
  getOverview() {
    return api.get('/purchases/overview')
  },

  getAnalysis() {
    return api.get('/purchases/analysis')
  },

  getAiRecommendations(payload) {
    return api.post('/purchases/analysis/recommend', payload)
  },

  // ── Suppliers ─────────────────────────────────────────────────────────────
  getSuppliers() {
    return api.get('/purchases/suppliers')
  },

  createSupplier(payload) {
    return api.post('/purchases/suppliers', payload)
  },

  // ── Requisitions ──────────────────────────────────────────────────────────
  getRequisitions() {
    return api.get('/purchases/requisitions')
  },

  createRequisition(payload) {
    return api.post('/purchases/requisitions', payload)
  },

  validateRequisition(id, payload) {
    return api.put(`/purchases/requisitions/${id}/validate`, payload)
  },

  // ── Orders ────────────────────────────────────────────────────────────────
  getOrders() {
    return api.get('/purchases/orders')
  },

  createOrder(payload) {
    return api.post('/purchases/orders', payload)
  },

  // ── Receipts ──────────────────────────────────────────────────────────────
  getReceipts() {
    return api.get('/purchases/receipts')
  },

  createReceipt(payload) {
    return api.post('/purchases/orders/receipt', payload)
  },

  // ── Invoices ──────────────────────────────────────────────────────────────
  getInvoices() {
    return api.get('/purchases/invoices')
  },

  createInvoice(payload) {
    return api.post('/purchases/invoices', payload)
  }
}

export default purchaseService
