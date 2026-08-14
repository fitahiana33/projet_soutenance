<template>
  <aside :class="['app-sidebar', { 'app-sidebar--collapsed': collapsed }]">
    <div class="sidebar-header">
      <span v-if="!collapsed" class="sidebar-title">NAVIGATION METIER</span>
      <span v-else class="sidebar-title sidebar-title--collapsed">ERP</span>
    </div>

    <nav class="sidebar-nav">
      <ul>
        <li v-for="item in navItems" :key="item.name">
          <!-- Standard Single Link -->
          <router-link
            v-if="!item.children"
            :to="item.path"
            class="nav-link"
            active-class="nav-link--active"
            :title="collapsed ? item.name : undefined"
          >
            <AppIcon :name="item.icon" size="20" class="nav-icon" />
            <span v-if="!collapsed" class="nav-text">{{ item.name }}</span>
            <span v-if="!collapsed && item.badge" class="nav-badge">{{ item.badge }}</span>
          </router-link>

          <!-- Collapsible Dropdown Parent -->
          <div v-else class="nav-dropdown">
            <button
              type="button"
              :class="['nav-link', 'nav-dropdown-toggle', { 'nav-link--active': isChildActive(item) }]"
              @click="toggleMenu(item.name)"
              :title="collapsed ? item.name : undefined"
            >
              <AppIcon :name="item.icon" size="20" class="nav-icon" />
              <span v-if="!collapsed" class="nav-text">{{ item.name }}</span>
              <span v-if="!collapsed" :class="['chevron-icon', { 'chevron-icon--open': openMenus[item.name] }]">
                ▼
              </span>
            </button>

            <!-- Submenu Children Items -->
            <ul v-if="!collapsed && openMenus[item.name]" class="submenu">
              <li v-for="child in item.children" :key="child.path">
                <router-link
                  :to="child.path"
                  class="submenu-link"
                  active-class="submenu-link--active"
                >
                  <AppIcon :name="child.icon" size="16" class="submenu-icon" />
                  <span>{{ child.name }}</span>
                </router-link>
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </nav>

    <div class="sidebar-footer">
      <div v-if="!collapsed" class="system-status">
        <span class="status-indicator"></span>
        <span class="status-text">Serveur connecté</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { navigationItems } from '../../config/navigation'
import AppIcon from '../ui/AppIcon.vue'

defineProps({
  collapsed: { type: Boolean, default: false }
})

const route = useRoute()
const navItems = navigationItems
const openMenus = ref({
  'Référentiel Produits': true
})

function toggleMenu(name) {
  openMenus.value[name] = !openMenus.value[name]
}

function isChildActive(item) {
  if (!item.children) return false
  return item.children.some(child => route.path === child.path)
}

watchEffect(() => {
  navItems.forEach(item => {
    if (item.children && isChildActive(item)) {
      openMenus.value[item.name] = true
    }
  })
})
</script>

<style scoped>
.app-sidebar {
  width: var(--sidebar-width);
  background-color: var(--color-sidebar-bg);
  color: var(--color-sidebar-text);
  display: flex;
  flex-direction: column;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  min-height: calc(100vh - var(--header-height));
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.app-sidebar--collapsed {
  width: var(--sidebar-width-collapsed);
}

.sidebar-header {
  padding: var(--space-5) var(--space-5) var(--space-3);
}

.sidebar-title {
  font-size: 0.7rem;
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.08em;
  color: #64748b;
  text-transform: uppercase;
}

.sidebar-title--collapsed {
  text-align: center;
  display: block;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-3) var(--space-3);
}

.sidebar-nav ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: 0;
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0.7rem 0.9rem;
  color: var(--color-sidebar-text);
  border-radius: var(--radius-md);
  transition: all 0.15s ease;
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
  position: relative;
  width: 100%;
  border: none;
  background: none;
  cursor: pointer;
  text-align: left;
}

.nav-link:hover {
  background-color: var(--color-sidebar-hover);
  color: var(--color-sidebar-text-active);
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
}

.nav-link:hover .nav-icon {
  transform: scale(1.08);
}

.nav-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-badge {
  font-size: 0.65rem;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  background-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  font-weight: var(--font-weight-semibold);
}

.chevron-icon {
  font-size: 0.6rem;
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
  margin-top: 0.2rem;
  margin-bottom: 0.4rem;
  padding-left: 1.2rem !important;
  display: flex;
  flex-direction: column;
  gap: 2px !important;
}

.submenu-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.5rem 0.8rem;
  color: #94a3b8;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  text-decoration: none;
  transition: all 0.15s ease;
}

.submenu-link:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

.submenu-link--active {
  color: #60a5fa;
  font-weight: var(--font-weight-semibold);
  background-color: rgba(37, 99, 235, 0.15);
}

.submenu-icon {
  opacity: 0.8;
}

.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.system-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  color: #94a3b8;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #10b981;
  box-shadow: 0 0 8px #10b981;
}
</style>
