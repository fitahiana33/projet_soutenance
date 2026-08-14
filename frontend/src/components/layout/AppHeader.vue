<template>
  <header class="app-header">
    <div class="header-left">
      <button
        type="button"
        class="toggle-btn"
        aria-label="Basculer le menu"
        @click="$emit('toggle-sidebar')"
      >
        <AppIcon name="menu" size="20" />
      </button>

      <div class="brand">
        <span class="brand-logo">⚡</span>
        <span class="brand-name">Smart ERP</span>
        <AppBadge variant="primary" label="Pro" />
      </div>
    </div>

    <div class="header-right">
      <div class="user-profile">
        <div class="user-avatar">{{ userInitials }}</div>
        <div class="user-info">
          <span class="user-name">{{ userName }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
      </div>

      <AppButton variant="ghost" size="sm" class="logout-btn" @click="handleLogout">
        <AppIcon name="logout" size="16" />
        <span>Déconnexion</span>
      </AppButton>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import AppButton from '../ui/AppButton.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppIcon from '../ui/AppIcon.vue'

defineEmits(['toggle-sidebar'])

const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => {
  const user = authStore.currentUser
  if (!user) return 'Administrateur'
  if (user.first_name) {
    return `${user.first_name} ${user.name}`.trim()
  }
  return user.name || 'Administrateur'
})

const userInitials = computed(() => {
  const user = authStore.currentUser
  if (!user) return 'AD'
  const firstChar = user.first_name ? user.first_name[0] : (user.name ? user.name[0] : 'A')
  const lastChar = user.name ? user.name[0] : 'D'
  return (firstChar + lastChar).toUpperCase()
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
  padding: 0 var(--space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.toggle-btn {
  background: none;
  border: 1px solid var(--color-border);
  font-size: 1.25rem;
  color: var(--color-text);
  cursor: pointer;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  transition: background-color 0.15s ease;
}

.toggle-btn:hover {
  background-color: var(--color-bg);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.brand-logo {
  font-size: 1.2rem;
}

.brand-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  letter-spacing: -0.02em;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-left: var(--space-2);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), #1d4ed8);
  color: #ffffff;
  font-weight: var(--font-weight-bold);
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
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
}

.user-role {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.logout-btn {
  gap: var(--space-2);
}
</style>
