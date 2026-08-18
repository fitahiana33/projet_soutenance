/**
 * userService.js - Service layer for Users & Roles & Permissions API calls
 */
import api from './api'

const userService = {
  // ── Users ──────────────────────────────────────────────────────────────────
  getUsers() {
    return api.get('/users/')
  },

  createUser(payload) {
    return api.post('/users/', payload)
  },

  updateUser(id, payload) {
    return api.put(`/users/${id}`, payload)
  },

  deleteUser(id) {
    return api.delete(`/users/${id}`)
  },

  setUserStatus(id, isActive) {
    return api.patch(`/users/${id}/status?is_active=${isActive}`)
  },

  assignRoles(userId, roleIds) {
    return api.post(`/users/${userId}/roles`, { role_ids: roleIds })
  },

  // ── Roles ──────────────────────────────────────────────────────────────────
  getRoles() {
    return api.get('/roles/')
  },

  createRole(payload) {
    return api.post('/roles/', payload)
  },

  updateRole(id, payload) {
    return api.put(`/roles/${id}`, payload)
  },

  deleteRole(id) {
    return api.delete(`/roles/${id}`)
  },

  assignPermissions(roleId, permissionIds) {
    return api.post(`/roles/${roleId}/permissions`, { permission_ids: permissionIds })
  },

  // ── Permissions ────────────────────────────────────────────────────────────
  getPermissions() {
    return api.get('/permissions/')
  },

  createPermission(payload) {
    return api.post('/permissions/', payload)
  },

  updatePermission(id, payload) {
    return api.put(`/permissions/${id}`, payload)
  },

  deletePermission(id) {
    return api.delete(`/permissions/${id}`)
  }
}

export default userService
