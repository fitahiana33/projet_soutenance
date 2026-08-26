import { navigationSections } from '../config/navigation'

export function userCanAccess(user, permissions = []) {
  if (!permissions.length) return true
  if (!user?.roles) return false
  const roles = user.roles.map(role => (role.libelle || '').toUpperCase())
  if (roles.includes('ADMIN')) return true
  const granted = new Set(user.roles.flatMap(role => (role.permissions || []).map(permission => (permission.code || '').toUpperCase())))
  return permissions.some(permission => granted.has(permission.toUpperCase()))
}

export function getFirstAllowedPath(user) {
  const entries = navigationSections.flatMap(section => section.items || []).flatMap(item => item.children || item)
  const firstBusinessPage = entries.find(item => item.path !== '/dashboard' && userCanAccess(user, item.permissions || []))
  return firstBusinessPage?.path || '/dashboard'
}
