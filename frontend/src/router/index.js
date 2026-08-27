import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

import Login from '../views/auth/Login.vue'
import Forbidden from '../views/auth/Forbidden.vue'
import Dashboard from '../views/Dashboard.vue'
import UsersIndex from '../views/users/UsersIndex.vue'
import RolesIndex from '../views/roles/RolesIndex.vue'
import ProductsIndex from '../views/products/ProductsIndex.vue'
import CategoriesIndex from '../views/products/CategoriesIndex.vue'
import StocksIndex from '../views/stocks/StocksIndex.vue'
import PurchasesIndex from '../views/purchases/PurchasesIndex.vue'
import SalesIndex from '../views/sales/SalesIndex.vue'
import HRIndex from '../views/hr/HRIndex.vue'
import EmployeeDetail from '../views/hr/EmployeeDetail.vue'
import RecruitmentIndex from '../views/recruitment/RecruitmentIndex.vue'
import CandidateDetail from '../views/recruitment/CandidateDetail.vue'
import AuditIndex from '../views/audit/AuditIndex.vue'
import SystemSettingsIndex from '../views/system/SystemSettingsIndex.vue'
import { getFirstAllowedPath, userCanAccess } from '../utils/access'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/403',
    name: 'forbidden',
    component: Forbidden,
    meta: { public: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, permissions: ['DASHBOARD_READ'] }
  },
  {
    path: '/products',
    name: 'products',
    component: ProductsIndex,
    meta: { requiresAuth: true, permissions: ['PRODUCT_READ', 'PRODUCT_CREATE'] }
  },
  {
    path: '/products/categories',
    name: 'categories',
    component: CategoriesIndex,
    meta: { requiresAuth: true, permissions: ['CATEGORY_READ', 'CATEGORY_CREATE'] }
  },
  {
    path: '/stocks',
    name: 'stocks',
    component: StocksIndex,
    meta: { requiresAuth: true, permissions: ['STOCK_READ', 'STOCK_UPDATE', 'STOCK_MANAGE'] }
  },
  {
    path: '/purchases',
    name: 'purchases',
    component: PurchasesIndex,
    meta: { requiresAuth: true, permissions: ['PURCHASE_READ', 'PURCHASE_CREATE', 'PURCHASE_UPDATE', 'PURCHASE_VALIDATE'] }
  },
  {
    path: '/sales',
    name: 'sales',
    component: SalesIndex,
    meta: { requiresAuth: true, permissions: ['SALES_READ', 'SALES_CREATE', 'SALES_VALIDATE'] }
  },
  {
    path: '/hr',
    name: 'hr',
    component: HRIndex,
    meta: { requiresAuth: true, permissions: ['HR_READ', 'EMPLOYEE_READ', 'PAYROLL_READ', 'HOLIDAY_READ'] }
  },
  {
    path: '/hr/employees/:id',
    name: 'employee-detail',
    component: EmployeeDetail,
    meta: { requiresAuth: true, permissions: ['HR_READ', 'EMPLOYEE_READ'] }
  },
  {
    path: '/recruitment',
    name: 'recruitment',
    component: RecruitmentIndex,
    meta: { requiresAuth: true, permissions: ['HR_READ', 'HR_MANAGE'] }
  },
  {
    path: '/recruitment/candidates/:id',
    name: 'candidate-detail',
    component: CandidateDetail,
    meta: { requiresAuth: true, permissions: ['HR_READ', 'HR_MANAGE'] }
  },
  {
    path: '/users',
    name: 'users',
    component: UsersIndex,
    meta: { requiresAuth: true, permissions: ['USER_READ', 'USER_CREATE', 'USER_UPDATE'] }
  },
  {
    path: '/roles',
    name: 'roles',
    component: RolesIndex,
    meta: { requiresAuth: true, permissions: ['ROLE_READ', 'ROLE_CREATE', 'ROLE_UPDATE'] }
  },
  {
    path: '/permissions',
    name: 'permissions',
    component: RolesIndex,
    meta: { requiresAuth: true, permissions: ['ROLE_READ', 'PERMISSION_MANAGE'] }
  },
  {
    path: '/audit',
    name: 'audit',
    component: AuditIndex,
    meta: { requiresAuth: true, permissions: ['AUDIT_READ'] }
  },
  {
    path: '/system',
    name: 'system',
    component: SystemSettingsIndex,
    meta: { requiresAuth: true, permissions: ['SYSTEM_READ', 'SYSTEM_MANAGE'] }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }

    const valid = await authStore.restoreSession()
    if (!valid) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }

    const requiredPerms = to.meta.permissions
    if (requiredPerms && requiredPerms.length > 0) {
      const user = authStore.currentUser
      if (user && user.roles) {
        const roleNames = user.roles.map(r => (r.libelle || '').toUpperCase())
        if (!roleNames.includes('ADMIN')) {
          const userPerms = new Set()
          user.roles.forEach(r => {
            if (r.permissions) {
              r.permissions.forEach(p => userPerms.add((p.code || '').toUpperCase()))
            }
          })
          const hasAccess = userCanAccess(user, requiredPerms)
          if (!hasAccess) {
            return { name: 'forbidden', query: { from: to.fullPath } }
          }
        }
      } else {
        return { name: 'forbidden', query: { from: to.fullPath } }
      }
    }
  }

  if (to.name === 'login' && authStore.isAuthenticated) {
    return getFirstAllowedPath(authStore.currentUser)
  }

  return true
})

export default router
