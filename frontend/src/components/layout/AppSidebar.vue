<template>
  <aside :class="['app-sidebar', { 'app-sidebar--collapsed': collapsed }]">
    <div class="sidebar-header">
      <div class="brand-logo">
        <div class="brand-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none" width="26" height="26">
            <rect width="32" height="32" rx="7" fill="url(#sg1)"/>
            <path d="M8 16h4l3-6 4 12 3-6h4" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="sg1" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                <stop stop-color="#2563eb"/><stop offset="1" stop-color="#1e40af"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div v-if="!collapsed" class="brand-text-wrap">
          <span class="brand-name">Smart ERP</span>
          <span class="brand-sub">Pilotage Entreprise</span>
        </div>
      </div>
    </div>

    <nav class="sidebar-nav">
      <div v-for="(section, idx) in filteredNavSections" :key="idx" class="nav-section">
        <div v-if="!collapsed && section.header" class="section-header">
          {{ section.header }}
        </div>

        <ul class="section-list">
          <li v-for="item in section.items" :key="item.name">
            <!-- Link Standard -->
            <router-link
              v-if="!item.children"
              :to="item.path"
              class="nav-link"
              active-class="nav-link--active"
              :title="collapsed ? item.name : undefined"
            >
              <AppIcon :name="item.icon" size="18" class="nav-icon" />
              <span v-if="!collapsed" class="nav-text">{{ item.name }}</span>
              <span v-if="!collapsed && item.badge" class="nav-badge">{{ item.badge }}</span>
            </router-link>

            <!-- Dropdown Enfant -->
            <div v-else class="nav-dropdown">
              <button
                type="button"
                :class="['nav-link', 'nav-dropdown-toggle', { 'nav-link--active': isChildActive(item) }]"
                @click="toggleMenu(item.name)"
                :title="collapsed ? item.name : undefined"
              >
                <AppIcon :name="item.icon" size="18" class="nav-icon" />
                <span v-if="!collapsed" class="nav-text">{{ item.name }}</span>
                <span v-if="!collapsed" :class="['chevron-icon', { 'chevron-icon--open': openMenus[item.name] }]">
                  ▼
                </span>
              </button>

              <ul v-if="!collapsed && openMenus[item.name]" class="submenu">
                <li v-for="child in item.children" :key="child.path">
                  <router-link
                    :to="child.path"
                    class="submenu-link"
                    active-class="submenu-link--active"
                  >
                    <AppIcon :name="child.icon" size="14" class="submenu-icon" />
                    <span>{{ child.name }}</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
        </ul>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div v-if="!collapsed" class="system-status">
        <div class="status-row">
          <span class="status-indicator" :class="{ 'status-indicator--online': true }" aria-label="Système opérationnel"></span>
          <span class="status-text">Système opérationnel</span>
        </div>
        <span class="status-time">{{ currentTime }}</span>
      </div>
      <div v-else class="status-indicator status-indicator--online status-indicator--centered"></div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watchEffect, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { navigationSections } from '../../config/navigation'
import AppIcon from '../ui/AppIcon.vue'

const currentTime = ref('')
let timer = null
function updateTime() {
  currentTime.value = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}
onMounted(() => { updateTime(); timer = setInterval(updateTime, 60000) })
onUnmounted(() => clearInterval(timer))

defineProps({
  collapsed: { type: Boolean, default: false }
})

const route = useRoute()
const authStore = useAuthStore()

const openMenus = ref({
  'Référentiel Produits': true
})

function canAccess(item) {
  if (!item.permissions || item.permissions.length === 0) return true
  const user = authStore.currentUser
  if (!user || !user.roles) return false

  const roleNames = user.roles.map(r => r.libelle.toUpperCase())
  if (roleNames.includes('ADMIN')) return true

  const userPerms = new Set()
  user.roles.forEach(r => {
    if (r.permissions) {
      r.permissions.forEach(p => userPerms.add(p.code.toUpperCase()))
    }
  })

  return item.permissions.some(perm => userPerms.has(perm.toUpperCase()))
}

const filteredNavSections = computed(() => {
  return navigationSections
    .map(section => {
      const filteredItems = section.items
        .filter(item => canAccess(item))
        .map(item => {
          if (item.children) {
            const filteredChildren = item.children.filter(child => canAccess(child))
            return { ...item, children: filteredChildren }
          }
          return item
        })
        .filter(item => !item.children || item.children.length > 0)

      return {
        ...section,
        items: filteredItems
      }
    })
    .filter(section => section.items.length > 0)
})

function toggleMenu(name) {
  openMenus.value[name] = !openMenus.value[name]
}

function isChildActive(item) {
  if (!item.children) return false
  return item.children.some(child => route.path === child.path)
}

watchEffect(() => {
  filteredNavSections.value.forEach(section => {
    section.items.forEach(item => {
      if (item.children && isChildActive(item)) {
        openMenus.value[item.name] = true
      }
    })
  })
})
</script>

<style scoped>
.app-sidebar {
  width: var(--sidebar-width);
  background-color: #0f172a;
  color: #94a3b8;
  display: flex;
  flex-direction: column;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  min-height: calc(100vh - var(--header-height));
  border-right: 1px solid #1e293b;
}

.app-sidebar--collapsed {
  width: var(--sidebar-width-collapsed);
}

.sidebar-header {
  padding: var(--space-4) var(--space-4) var(--space-3);
  border-bottom: 1px solid #1e293b;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.brand-icon-wrap {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.brand-text-wrap {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand-name {
  font-size: 0.875rem;
  font-weight: var(--font-weight-bold);
  color: #ffffff;
  letter-spacing: -0.01em;
}

.brand-sub {
  color: #60a5fa;
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-3) var(--space-2);
  overflow-y: auto;
}

.nav-section {
  margin-bottom: var(--space-4);
}

.section-header {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #475569;
  text-transform: uppercase;
  padding: 0.4rem 0.75rem 0.2rem;
}

.section-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0.55rem 0.75rem;
  color: #94a3b8;
  border-radius: var(--radius-md);
  transition: all 0.15s ease;
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  font-size: 0.825rem;
  position: relative;
  width: 100%;
  border: none;
  background: none;
  cursor: pointer;
  text-align: left;
}

.nav-link:hover {
  background-color: #1e293b;
  color: #f8fafc;
}

.nav-link--active {
  background-color: var(--color-primary);
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
}

.nav-link--active .nav-icon {
  color: #ffffff;
}

.nav-icon {
  transition: transform 0.15s ease;
  flex-shrink: 0;
}

.nav-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-badge {
  font-size: 0.6rem;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background-color: rgba(255, 255, 255, 0.1);
  color: #93c5fd;
  font-weight: var(--font-weight-semibold);
}

.chevron-icon {
  font-size: 0.55rem;
  transition: transform 0.2s ease;
  opacity: 0.7;
}

.chevron-icon--open {
  transform: rotate(180deg);
}

.nav-dropdown {
  display: flex;
  flex-direction: column;
}

.submenu {
  margin-top: 0.15rem;
  margin-bottom: 0.3rem;
  padding-left: 1.1rem !important;
  display: flex;
  flex-direction: column;
  gap: 2px !important;
}

.submenu-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.45rem 0.75rem;
  color: #64748b;
  border-radius: var(--radius-sm);
  font-size: 0.775rem;
  text-decoration: none;
  transition: all 0.15s ease;
}

.submenu-link:hover {
  background-color: #1e293b;
  color: #ffffff;
}

.submenu-link--active {
  color: #60a5fa;
  font-weight: var(--font-weight-semibold);
  background-color: rgba(37, 99, 235, 0.15);
}

.sidebar-footer {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid #1e293b;
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.7rem;
  color: #64748b;
}

.status-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator--online {
  background-color: #10b981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.7);
  animation: pulse-online 2s ease-in-out infinite;
}

.status-indicator--centered {
  margin: auto;
}

.status-time {
  font-size: 0.65rem;
  color: #475569;
  padding-left: 14px;
}

@keyframes pulse-online {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media (max-width: 768px) {
  .app-sidebar {
    width: var(--sidebar-width-collapsed);
  }

  .app-sidebar:not(.app-sidebar--collapsed) {
    width: min(82vw, var(--sidebar-width));
    position: fixed;
    inset: var(--header-height) auto 0 0;
    z-index: 90;
    box-shadow: var(--shadow-lg);
  }
}
</style>
