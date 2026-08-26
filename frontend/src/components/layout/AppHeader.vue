<template>
  <header class="app-header">
    <div class="header-left">
      <button
        type="button"
        class="toggle-btn"
        aria-label="Basculer le menu latéral"
        @click="$emit('toggle-sidebar')"
      >
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M3 6h14M3 10h14M3 14h14" stroke-linecap="round"/>
        </svg>
      </button>

      <div class="brand">
        <div class="brand-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
            <rect width="32" height="32" rx="8" fill="url(#g1)"/>
            <path d="M8 16h4l3-6 4 12 3-6h4" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="g1" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                <stop stop-color="#2563eb"/>
                <stop offset="1" stop-color="#1d4ed8"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">Smart ERP</span>
          <span class="brand-tagline">Système de Pilotage d'Entreprise</span>
        </div>
      </div>
    </div>

    <div class="header-center" role="search">
      <div class="global-search" @click="$emit('open-search')">
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <circle cx="8.5" cy="8.5" r="5.5"/><path d="M16 16l-3-3"/>
        </svg>
        <span class="search-placeholder">Recherche rapide...</span>
        <kbd class="search-kbd">Ctrl+K</kbd>
      </div>
    </div>

    <div class="header-right">
      <!-- Notifications -->
      <div class="header-icon-btn" title="Notifications" role="button" tabindex="0">
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M10 2a6 6 0 00-6 6v2.586l-1.707 1.707A1 1 0 003 14h14a1 1 0 00.707-1.707L16 10.586V8a6 6 0 00-6-6z"/>
          <path d="M8 14s0 2 2 2 2-2 2-2H8z"/>
        </svg>
        <span class="notification-dot" aria-label="Nouvelles notifications"></span>
      </div>

      <!-- User Profile -->
      <div class="user-profile" :title="`Connecté en tant que ${userName} (${userRole})`">
        <div class="user-avatar" aria-hidden="true">{{ userInitials }}</div>
        <div class="user-info">
          <span class="user-name">{{ userName }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
      </div>

      <div class="header-divider" aria-hidden="true"></div>

      <AppButton variant="ghost" size="sm" class="logout-btn" @click="handleLogout" aria-label="Se déconnecter">
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M13 10H3m0 0l3-3m-3 3l3 3" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M8 5V4a1 1 0 011-1h7a1 1 0 011 1v12a1 1 0 01-1 1H9a1 1 0 01-1-1v-1" stroke-linecap="round"/>
        </svg>
        <span class="logout-label">Déconnexion</span>
      </AppButton>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import AppButton from '../ui/AppButton.vue'

defineEmits(['toggle-sidebar', 'open-search'])

const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => {
  const user = authStore.currentUser
  if (!user) return 'Administrateur'
  if (user.first_name) return `${user.first_name} ${user.name}`.trim()
  return user.name || 'Administrateur'
})

const userInitials = computed(() => {
  const user = authStore.currentUser
  if (!user) return 'AD'
  const f = user.first_name ? user.first_name[0] : (user.name ? user.name[0] : 'A')
  const l = user.name ? user.name[0] : 'D'
  return (f + l).toUpperCase()
})

const userRole = computed(() => {
  const user = authStore.currentUser
  if (user && user.roles && user.roles.length > 0) {
    return user.roles.map(r => r.libelle).join(', ')
  }
  return 'Administrateur'
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 0 var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* --- Left --- */
.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-shrink: 0;
}

.toggle-btn {
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  cursor: pointer;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  transition: all 0.15s ease;
  min-width: 36px;
  min-height: 36px;
  justify-content: center;
}

.toggle-btn:hover {
  background-color: var(--color-bg);
  color: var(--color-text);
  border-color: var(--color-primary);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  letter-spacing: -0.02em;
}

.brand-tagline {
  font-size: 0.6rem;
  color: var(--color-text-muted);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

/* --- Center --- */
.header-center {
  flex: 1;
  max-width: 480px;
  margin: 0 auto;
}

.global-search {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.45rem var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  transition: all 0.15s ease;
}

.global-search:hover {
  border-color: var(--color-primary);
  background: var(--color-surface);
}

.search-placeholder {
  flex: 1;
}

.search-kbd {
  font-size: 0.65rem;
  background: var(--color-border);
  border-radius: 3px;
  padding: 1px 5px;
  color: var(--color-text-muted);
  font-family: monospace;
}

/* --- Right --- */
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

.header-icon-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-muted);
  transition: all 0.15s ease;
}

.header-icon-btn:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.notification-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  border: 1.5px solid var(--color-surface);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: default;
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), #1d4ed8);
  color: #fff;
  font-weight: var(--font-weight-bold);
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.header-divider {
  width: 1px;
  height: 24px;
  background: var(--color-border);
}

.logout-btn {
  gap: var(--space-2);
}

.logout-label {
  font-size: var(--font-size-sm);
}

@media (max-width: 768px) {
  .header-center { display: none; }
  .brand-tagline { display: none; }
  .user-info { display: none; }
  .logout-label { display: none; }
}
</style>
