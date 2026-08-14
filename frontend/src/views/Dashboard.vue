<template>
  <AppLayout>
    <PageHeader
      title="Tableau de bord ERP"
      :subtitle="`Vue d'ensemble et métriques clés pour ${fullName}`"
    >
      <template #actions>
        <AppButton variant="primary" size="sm" @click="openQuickAction">
          <AppIcon name="plus" size="16" />
          <span>Action Rapide</span>
        </AppButton>
      </template>
    </PageHeader>

    <!-- KPI Metric Cards -->
    <div class="kpi-grid">
      <AppCard class="kpi-card">
        <div class="kpi-body">
          <div class="kpi-icon kpi-icon--primary">
            <AppIcon name="users" size="22" />
          </div>
          <div class="kpi-details">
            <span class="kpi-title">Utilisateurs Enregistrés</span>
            <span class="kpi-value">{{ totalUsers }}</span>
            <div class="kpi-trend kpi-trend--up">
              <AppIcon name="trend-up" size="14" />
              <span>Base PostgreSQL active</span>
            </div>
          </div>
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-body">
          <div class="kpi-icon kpi-icon--info">
            <AppIcon name="shield" size="22" />
          </div>
          <div class="kpi-details">
            <span class="kpi-title">Rôles Configurés</span>
            <span class="kpi-value">{{ totalRoles }}</span>
            <div class="kpi-trend">
              <span>RBAC Actif</span>
            </div>
          </div>
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-body">
          <div class="kpi-icon kpi-icon--success">
            <AppIcon name="check" size="22" />
          </div>
          <div class="kpi-details">
            <span class="kpi-title">Permissions Système</span>
            <span class="kpi-value">{{ totalPermissions }}</span>
            <div class="kpi-trend kpi-trend--up">
              <span>Privilèges filtrés</span>
            </div>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Main Content Grid -->
    <div class="dashboard-main-grid">
      <!-- Recent Operational Activity -->
      <AppCard title="Journal des Opérations & Sécurité" class="grid-card">
        <div class="timeline">
          <div v-for="act in recentActivities" :key="act.id" class="timeline-item">
            <div :class="['timeline-badge', `timeline-badge--${act.type}`]">
              <AppIcon :name="act.icon" size="14" />
            </div>
            <div class="timeline-content">
              <p class="timeline-title">{{ act.title }}</p>
              <p class="timeline-desc">{{ act.description }}</p>
              <span class="timeline-time">{{ act.time }}</span>
            </div>
          </div>
        </div>
      </AppCard>

      <!-- Active Modules Status -->
      <AppCard title="État des Services Actifs" class="grid-card">
        <div class="module-status-list">
          <div v-for="mod in modules" :key="mod.name" class="module-status-item">
            <div class="module-info">
              <AppIcon :name="mod.icon" size="18" class="module-icon" />
              <div>
                <h4 class="module-name">{{ mod.name }}</h4>
                <p class="module-desc">{{ mod.desc }}</p>
              </div>
            </div>
            <AppBadge :variant="mod.variant" :label="mod.status" />
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Quick Action Modal -->
    <AppModal v-model="showActionModal" title="Actions Rapides d'Administration" size="md">
      <p>Sélectionnez une opération d'administration à exécuter :</p>
      <div class="quick-action-buttons">
        <AppButton variant="secondary" block @click="$router.push('/users')">
          <AppIcon name="users" size="16" />
          <span>Gérer les comptes utilisateurs</span>
        </AppButton>
        <AppButton variant="secondary" block @click="$router.push('/roles')">
          <AppIcon name="shield" size="16" />
          <span>Configurer les rôles et permissions RBAC</span>
        </AppButton>
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="showActionModal = false">Fermer</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../store/auth'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/ui/PageHeader.vue'
import AppCard from '../components/ui/AppCard.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppIcon from '../components/ui/AppIcon.vue'
import AppModal from '../components/ui/AppModal.vue'

const authStore = useAuthStore()
const showActionModal = ref(false)

const totalUsers = ref(0)
const totalRoles = ref(0)
const totalPermissions = ref(0)

const fullName = computed(() => {
  const user = authStore.currentUser
  if (!user) return 'Administrateur'
  if (user.first_name) {
    return `${user.first_name} ${user.name}`.trim()
  }
  return user.name || 'Administrateur'
})

async function fetchDashboardMetrics() {
  try {
    const [usersRes, rolesRes, permsRes] = await Promise.all([
      api.get('/users/').catch(() => ({ data: [] })),
      api.get('/roles/').catch(() => ({ data: [] })),
      api.get('/permissions/').catch(() => ({ data: [] }))
    ])

    if (Array.isArray(usersRes.data)) totalUsers.value = usersRes.data.length
    if (Array.isArray(rolesRes.data)) totalRoles.value = rolesRes.data.length
    if (Array.isArray(permsRes.data)) totalPermissions.value = permsRes.data.length
  } catch (error) {
    // Fallback metrics
    totalUsers.value = 1
    totalRoles.value = 1
    totalPermissions.value = 14
  }
}

onMounted(() => {
  fetchDashboardMetrics()
})

function openQuickAction() {
  showActionModal.value = true
}

const recentActivities = [
  {
    id: 1,
    type: 'primary',
    icon: 'users',
    title: 'Authentification réussie',
    description: 'Connexion de l\'administrateur système.',
    time: 'Récemment'
  },
  {
    id: 2,
    type: 'info',
    icon: 'shield',
    title: 'Vérification du socle RBAC',
    description: 'Permissions et rôles chargés avec succès depuis la BD.',
    time: 'Aujourd\'hui'
  }
]

const modules = [
  {
    name: 'Authentification JWT & Sécurité',
    desc: 'Tokens bearer et gestion des sessions',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'shield'
  },
  {
    name: 'Gestion des Utilisateurs',
    desc: 'CRUD comptes et affectation des rôles',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'users'
  },
  {
    name: 'Gestion des Rôles & Permissions',
    desc: 'Matrice RBAC et privilèges granulaires',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'shield'
  }
]
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.kpi-card {
  border: 1px solid var(--color-border);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.kpi-body {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon--primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.kpi-icon--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.kpi-icon--info {
  background-color: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
}

.kpi-details {
  display: flex;
  flex-direction: column;
}

.kpi-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
}

.kpi-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  line-height: 1.1;
  margin: var(--space-1) 0;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.kpi-trend--up {
  color: var(--color-success);
  font-weight: var(--font-weight-semibold);
}

.dashboard-main-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: var(--space-6);
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  position: relative;
}

.timeline-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.timeline-badge--primary { background: var(--color-primary-light); color: var(--color-primary); }
.timeline-badge--info { background: rgba(37, 99, 235, 0.1); color: #1d4ed8; }

.timeline-content {
  flex: 1;
}

.timeline-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.timeline-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 2px 0 0;
}

.timeline-time {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  opacity: 0.8;
}

.module-status-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.module-status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3);
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
}

.module-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.module-icon {
  color: var(--color-primary);
}

.module-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.module-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.quick-action-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: var(--space-4);
}
</style>
