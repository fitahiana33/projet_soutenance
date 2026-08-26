/**
 * salesService.js - Service layer for Sales & Customers API calls
 */
import api from './api'

const salesService = {
  getOverview() {
    return api.get('/sales/overview')
  },

  getOrders() {
    return api.get('/sales/orders')
  },

  createOrder(payload) {
    return api.post('/sales/orders', payload)
  },

  updateOrderStatus(orderId, status) {
    return api.put(`/sales/orders/${orderId}/status?status=${status}`)
  },

  getQuotes() {
    return api.get('/sales/quotes')
  },

  createQuote(payload) {
    return api.post('/sales/quotes', payload)
  },

  getCustomers() {
    return api.get('/sales/customers')
  },

  createCustomer(payload) {
    return api.post('/sales/customers', payload)
  },

  updateCustomer(id, payload) {
    return api.put(`/sales/customers/${id}`, payload)
  },

  deleteCustomer(id) {
    return api.delete(`/sales/customers/${id}`)
  },

  getInvoices() {
    return api.get('/sales/invoices')
  },

  createInvoice(payload) {
    return api.post('/sales/invoices', payload)
  },

  updateInvoicePayment(id, payload) {
    return api.put(`/sales/invoices/${id}/payment`, payload)
  }
}

export default salesService
