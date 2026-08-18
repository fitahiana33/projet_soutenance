<template>
  <aside :class="['app-sidebar', { 'app-sidebar--collapsed': collapsed }]">
    <div class="sidebar-header">
      <div class="brand-logo">
        <span class="brand-badge">PRO</span>
        <span v-if="!collapsed" class="brand-name">SMART ERP <span class="brand-sub font-semibold">ENTERPRISE</span></span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <div v-for="(section, idx) in navSections" :key="idx" class="nav-section">
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
        <span class="status-indicator"></span>
        <span class="status-text">PostgreSQL & Dolibarr Sync OK</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { navigationSections } from '../../config/navigation'
import AppIcon from '../ui/AppIcon.vue'

defineProps({
  collapsed: { type: Boolean, default: false }
})

const route = useRoute()
const navSections = navigationSections
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
  navSections.forEach(section => {
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

.brand-badge {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #ffffff;
  font-size: 0.65rem;
  font-weight: var(--font-weight-bold);
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-sm);
  letter-spacing: 0.05em;
}

.brand-name {
  font-size: 0.85rem;
  font-weight: var(--font-weight-bold);
  color: #ffffff;
  letter-spacing: 0.05em;
}

.brand-sub {
  color: #60a5fa;
  font-size: 0.75rem;
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
  align-items: center;
  gap: var(--space-2);
  font-size: 0.7rem;
  color: #64748b;
}

.status-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #10b981;
  box-shadow: 0 0 8px #10b981;
}
</style>
