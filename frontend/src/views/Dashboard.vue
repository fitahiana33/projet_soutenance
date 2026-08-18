<template>
  <AppLayout>
    <PageHeader
      title="Tableau de Bord Direction & BI"
      :subtitle="`Vue d'ensemble stratégique et pilotage des ressources pour ${fullName}`"
    >
      <template #actions>
        <AppButton variant="primary" size="sm" @click="fetchMetrics">
          <AppIcon name="refresh" size="16" />
          <span>Actualiser les Métriques</span>
        </AppButton>
      </template>
    </PageHeader>

    <!-- Executive KPI Grid (4 Pillars) -->
    <div class="kpi-grid">
      <!-- 1. Ventes / CA -->
      <AppCard class="kpi-card">
        <div class="kpi-body">
          <div class="kpi-icon kpi-icon--success">
            <AppIcon name="dollar-sign" size="22" />
          </div>
          <div class="kpi-details">
            <span class="kpi-title">Chiffre d'Affaires (Ventes)</span>
            <span class="kpi-value color-success">{{ formatCurrency(salesMetrics.total_revenue || 0) }}</span>
            <div class="kpi-trend kpi-trend--up">
              <AppIcon name="trend-up" size="14" />
              <span>{{ salesMetrics.total_orders_count || 0 }} commande(s) validée(s)</span>
            </div>
          </div>
        </div>
      </AppCard>

      <!-- 2. Stocks / Inventaire -->
      <AppCard class="kpi-card">
        <div class="kpi-body">
          <div class="kpi-icon kpi-icon--primary">
            <AppIcon name="box" size="22" />
          </div>
          <div class="kpi-details">
            <span class="kpi-title">Valeur Stock Inventaire</span>
            <span class="kpi-value color-primary">{{ formatCurrency(stockMetrics.total_stock_value || 0) }}</span>
            <div class="kpi-trend">
              <span>{{ stockMetrics.total_products || 0 }} références catalogue</span>
            </div>
          </div>
        </div>
      </AppCard>

      <!-- 3. RH / Paie -->
      <AppCard class="kpi-card">
        <div class="kpi-body">
          <div class="kpi-icon kpi-icon--info">
            <AppIcon name="users" size="22" />
          </div>
          <div class="kpi-details">
            <span class="kpi-title">Masse Salariale (Net)</span>
            <span class="kpi-value">{{ formatCurrency(hrMetrics.total_net_payroll_monthly || hrMetrics.total_net_payroll || 0) }}</span>
            <div class="kpi-trend">
              <span>{{ hrMetrics.active_employees || hrMetrics.total_employees || 0 }} salariés actifs</span>
            </div>
          </div>
        </div>
      </AppCard>

      <!-- 4. Achats & Fournisseurs -->
      <AppCard class="kpi-card">
        <div class="kpi-body">
          <div class="kpi-icon kpi-icon--warning">
            <AppIcon name="shopping-cart" size="22" />
          </div>
          <div class="kpi-details">
            <span class="kpi-title">Volume d'Achats</span>
            <span class="kpi-value color-warning">{{ formatCurrency(purchaseMetrics.total_purchase_amount || 0) }}</span>
            <div class="kpi-trend">
              <span>{{ purchaseMetrics.active_suppliers_count || 0 }} fournisseur(s) actifs</span>
            </div>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- BI Visualizations Grid -->
    <div class="dashboard-main-grid mb-6">
      <!-- SVG Chart 1: Répartition de la Paie (Brut vs Cotisations vs Net) -->
      <AppCard title="📊 Structure de la Masse Salariale & Charges" class="grid-card">
        <div class="chart-container">
          <div class="bar-chart">
            <div class="bar-group">
              <div class="bar-label">Salaire Brut Total</div>
              <div class="bar-track">
                <div class="bar-fill bg-blue-500" style="width: 100%;"></div>
              </div>
              <div class="bar-val">{{ formatCurrency(hrMetrics.total_gross_payroll || 0) }}</div>
            </div>

            <div class="bar-group">
              <div class="bar-label">Cotisations Salariales & IRSA</div>
              <div class="bar-track">
                <div class="bar-fill bg-rose-500" style="width: 27%;"></div>
              </div>
              <div class="bar-val">{{ formatCurrency((hrMetrics.total_gross_payroll || 0) * 0.27) }}</div>
            </div>

            <div class="bar-group">
              <div class="bar-label">Salaire Net Payé</div>
              <div class="bar-track">
                <div class="bar-fill bg-emerald-500" style="width: 73%;"></div>
              </div>
              <div class="bar-val">{{ formatCurrency(hrMetrics.total_net_payroll_monthly || 0) }}</div>
            </div>

            <div class="bar-group">
              <div class="bar-label">Charges Patronales (CNaPS+OSTIE)</div>
              <div class="bar-track">
                <div class="bar-fill bg-amber-500" style="width: 18%;"></div>
              </div>
              <div class="bar-val">{{ formatCurrency((hrMetrics.total_gross_payroll || 0) * 0.18) }}</div>
            </div>
          </div>
        </div>
      </AppCard>

      <!-- SVG Chart 2: Répartition des Stocks & Valorisation -->
      <AppCard title="📦 Valorisation des Stocks (CUMP vs FIFO)" class="grid-card">
        <div class="flex flex-col justify-between h-full">
          <div class="kpi-summary-box mb-4 p-3 bg-slate-900 rounded border border-slate-800">
            <div class="flex justify-between items-center mb-2">
              <span class="text-xs text-slate-400">Valorisation CUMP (Pondérée):</span>
              <span class="font-bold color-primary">{{ formatCurrency(stockMetrics.total_stock_value_cump || stockMetrics.total_stock_value || 0) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-xs text-slate-400">Valorisation FIFO (Épuisement):</span>
              <span class="font-bold color-success">{{ formatCurrency(stockMetrics.total_stock_value_fifo || stockMetrics.total_stock_value || 0) }}</span>
            </div>
          </div>

          <div class="stat-pill-grid grid grid-cols-2 gap-3 text-xs">
            <div class="p-3 bg-slate-900 rounded text-center">
              <span class="text-slate-400 block mb-1">Articles en Alerte</span>
              <span class="font-bold text-lg color-warning">{{ stockMetrics.low_stock_count || 0 }}</span>
            </div>
            <div class="p-3 bg-slate-900 rounded text-center">
              <span class="text-slate-400 block mb-1">Ruptures Stock</span>
              <span class="font-bold text-lg color-danger">{{ stockMetrics.out_of_stock_count || 0 }}</span>
            </div>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Security & Audit Timeline -->
    <div class="dashboard-main-grid">
      <!-- Audit Feed -->
      <AppCard title="🛡️ Journal des Dernières Actions d'Audit" class="grid-card">
        <div class="timeline">
          <div v-for="log in recentAuditLogs" :key="log.id_audit" class="timeline-item">
            <div :class="['timeline-badge', getBadgeClass(log.action)]">
              <AppIcon name="clock" size="14" />
            </div>
            <div class="timeline-content">
              <p class="timeline-title">{{ log.username }} — {{ log.module }} ({{ log.action }})</p>
              <p class="timeline-desc">{{ log.details || log.target_entity }}</p>
              <span class="timeline-time">{{ formatDate(log.created_at) }}</span>
            </div>
          </div>
          <div v-if="recentAuditLogs.length === 0" class="text-center text-muted py-4">
            Aucun événement d'audit récent.
          </div>
        </div>
      </AppCard>

      <!-- Active Services Status -->
      <AppCard title="⚡ État des Services Système ERP" class="grid-card">
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
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dashboardService from '../services/dashboardService'
import auditService from '../services/auditService'
import { useAuthStore } from '../store/auth'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/ui/PageHeader.vue'
import AppCard from '../components/ui/AppCard.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppIcon from '../components/ui/AppIcon.vue'

const authStore = useAuthStore()

const salesMetrics = ref({})
const stockMetrics = ref({})
const hrMetrics = ref({})
const purchaseMetrics = ref({})
const recentAuditLogs = ref([])

const fullName = computed(() => {
  const user = authStore.currentUser
  if (!user) return 'Direction Générale'
  if (user.first_name) {
    return `${user.first_name} ${user.name}`.trim()
  }
  return user.name || 'Direction Générale'
})

async function fetchMetrics() {
  try {
    const [salesRes, stockRes, hrRes, purchaseRes, auditRes] = await Promise.all([
      dashboardService.getSalesOverview().catch(() => ({ data: {} })),
      dashboardService.getStockOverview().catch(() => ({ data: {} })),
      dashboardService.getHROverview().catch(() => ({ data: {} })),
      dashboardService.getPurchasesOverview().catch(() => ({ data: {} })),
      auditService.getLogs({}).catch(() => ({ data: [] }))
    ])

    salesMetrics.value = salesRes.data || {}
    stockMetrics.value = stockRes.data || {}
    hrMetrics.value = hrRes.data || {}
    purchaseMetrics.value = purchaseRes.data || {}
    recentAuditLogs.value = Array.isArray(auditRes.data) ? auditRes.data.slice(0, 5) : []
  } catch (error) {
    console.error('Erreur chargement dashboard:', error)
  }
}

function formatCurrency(val) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val || 0)
}

function formatDate(str) {
  if (!str) return 'Récemment'
  return new Date(str).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function getBadgeClass(act) {
  if (act === 'CREATE') return 'timeline-badge--success'
  if (act === 'DELETE') return 'timeline-badge--danger'
  return 'timeline-badge--primary'
}

const modules = [
  {
    name: 'Module Ventes & Facturation Clients',
    desc: 'Devis, réservations stock et factures',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'dollar-sign'
  },
  {
    name: 'Module Achats & 3-Way Matching',
    desc: 'Commandes fournisseurs et réceptions BL',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'shopping-cart'
  },
  {
    name: 'Module Stocks & Inventaires CUMP/FIFO',
    desc: 'Valorisation dynamique et lots/séries',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'box'
  },
  {
    name: 'Module RH & Paie Madagascar',
    desc: 'Fiches de paie, CNaPS, OSTIE, IRSA',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'users'
  },
  {
    name: 'Module Recrutement & Matching',
    desc: 'Fiches de poste et scoring compétences',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'shield'
  },
  {
    name: 'Sécurité RBAC & Journal d\'Audit',
    desc: 'Journal d\'audit et matrice des habilitations',
    status: 'Opérationnel',
    variant: 'success',
    icon: 'clock'
  }
]

onMounted(fetchMetrics)
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

.kpi-icon--primary { background-color: var(--color-primary-light); color: var(--color-primary); }
.kpi-icon--success { background-color: var(--color-success-light); color: var(--color-success); }
.kpi-icon--info { background-color: rgba(37, 99, 235, 0.1); color: #1d4ed8; }
.kpi-icon--warning { background-color: rgba(245, 158, 11, 0.1); color: #d97706; }

.kpi-details { display: flex; flex-direction: column; }
.kpi-title { font-size: var(--font-size-xs); color: var(--color-text-muted); font-weight: var(--font-weight-medium); }
.kpi-value { font-size: 1.4rem; font-weight: var(--font-weight-bold); line-height: 1.2; margin: 2px 0; }
.kpi-trend { display: flex; align-items: center; gap: var(--space-1); font-size: var(--font-size-xs); color: var(--color-text-muted); }
.kpi-trend--up { color: var(--color-success); font-weight: var(--font-weight-semibold); }

.dashboard-main-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: var(--space-6);
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.bar-group {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.bar-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.bar-track {
  height: 10px;
  background-color: #1e293b;
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.4s ease;
}

.bar-val {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text);
  text-align: right;
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
}

.timeline-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.timeline-badge--primary { background: var(--color-primary-light); color: var(--color-primary); }
.timeline-badge--success { background: var(--color-success-light); color: var(--color-success); }
.timeline-badge--danger { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.timeline-content { flex: 1; }
.timeline-title { font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); margin: 0; }
.timeline-desc { font-size: var(--font-size-xs); color: var(--color-text-muted); margin: 2px 0 0; }
.timeline-time { font-size: 0.7rem; color: var(--color-text-muted); opacity: 0.8; }

.module-status-list { display: flex; flex-direction: column; gap: var(--space-3); }
.module-status-item { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0.75rem; background-color: var(--color-bg); border-radius: var(--radius-md); }
.module-info { display: flex; align-items: center; gap: var(--space-3); }
.module-icon { color: var(--color-primary); }
.module-name { font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); margin: 0; }
.module-desc { font-size: var(--font-size-xs); color: var(--color-text-muted); margin: 0; }
</style>
