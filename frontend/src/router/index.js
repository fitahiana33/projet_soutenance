import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

import Login from '../views/auth/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import UsersIndex from '../views/users/UsersIndex.vue'
import RolesIndex from '../views/roles/RolesIndex.vue'
import DolibarrIndex from '../views/dolibarr/DolibarrIndex.vue'
import ProductsIndex from '../views/products/ProductsIndex.vue'
import CategoriesIndex from '../views/products/CategoriesIndex.vue'
import StocksIndex from '../views/stocks/StocksIndex.vue'

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
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/products',
    name: 'products',
    component: ProductsIndex,
    meta: { requiresAuth: true }
  },
  {
    path: '/products/categories',
    name: 'categories',
    component: CategoriesIndex,
    meta: { requiresAuth: true }
  },
  {
    path: '/stocks',
    name: 'stocks',
    component: StocksIndex,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'users',
    component: UsersIndex,
    meta: { requiresAuth: true }
  },
  {
    path: '/roles',
    name: 'roles',
    component: RolesIndex,
    meta: { requiresAuth: true }
  },
  {
    path: '/dolibarr',
    name: 'dolibarr',
    component: DolibarrIndex,
    meta: { requiresAuth: true }
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
  }

  if (to.name === 'login' && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
