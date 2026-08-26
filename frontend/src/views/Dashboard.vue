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

    <!-- Tendances: les variations expliquent l'evolution, pas seulement le niveau actuel. -->
    <div class="dashboard-insights mb-6">
      <AppCard title="Evolution de l'activite commerciale (6 derniers mois)" class="trend-card">
        <p class="chart-description">Chiffre d'affaires encaisse par mois, base sur les factures enregistrees.</p>
        <div v-if="salesTrend.length" class="trend-chart" aria-label="Evolution du chiffre d'affaires sur six mois">
          <div v-for="point in salesTrend" :key="point.period" class="trend-column">
            <span class="trend-value">{{ formatCompactCurrency(point.revenue) }}</span>
            <div class="trend-bar-track">
              <div class="trend-bar" :style="{ height: `${trendHeight(point.revenue)}%` }"></div>
            </div>
            <span class="trend-label">{{ formatMonth(point.period) }}</span>
          </div>
        </div>
        <div v-else class="empty-state">Aucune donnee mensuelle disponible.</div>
      </AppCard>

      <div class="variation-grid">
        <AppCard class="variation-card">
          <span class="kpi-title">CA encaisse ce mois</span>
          <strong class="variation-value">{{ formatCurrency(salesMetrics.current_month_revenue || 0) }}</strong>
          <span :class="['variation-label', variationClass(salesMetrics.revenue_variation_percent)]">
            {{ variationLabel(salesMetrics.revenue_variation_percent) }} vs mois precedent
          </span>
        </AppCard>
        <AppCard class="variation-card">
          <span class="kpi-title">Factures emises ce mois</span>
          <strong class="variation-value">{{ salesMetrics.current_month_invoices || 0 }}</strong>
          <span :class="['variation-label', variationClass(salesMetrics.invoices_variation_percent)]">
            {{ variationLabel(salesMetrics.invoices_variation_percent) }} vs mois precedent
          </span>
        </AppCard>
        <AppCard class="variation-card">
          <span class="kpi-title">Achats commandes ce mois</span>
          <strong class="variation-value">{{ formatCurrency(purchaseMetrics.current_month_purchase_amount || 0) }}</strong>
          <span :class="['variation-label', variationClass(purchaseMetrics.purchase_variation_percent)]">
            {{ variationLabel(purchaseMetrics.purchase_variation_percent) }} vs mois precedent
          </span>
        </AppCard>
      </div>
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
                <div class="bar-fill bg-blue-500" :style="{ width: `${payrollBars.gross}%` }"></div>
              </div>
              <div class="bar-val">{{ formatCurrency(hrMetrics.total_gross_payroll || 0) }}</div>
            </div>

            <div class="bar-group">
              <div class="bar-label">Cotisations Salariales & IRSA</div>
              <div class="bar-track">
                <div class="bar-fill bg-rose-500" :style="{ width: `${payrollBars.employeeCharges}%` }"></div>
              </div>
              <div class="bar-val">{{ formatCurrency(hrMetrics.total_employee_deductions || 0) }}</div>
            </div>

            <div class="bar-group">
              <div class="bar-label">Salaire Net Payé</div>
              <div class="bar-track">
                <div class="bar-fill bg-emerald-500" :style="{ width: `${payrollBars.net}%` }"></div>
              </div>
              <div class="bar-val">{{ formatCurrency(hrMetrics.total_net_payroll_monthly || 0) }}</div>
            </div>

            <div class="bar-group">
              <div class="bar-label">Charges Patronales (CNaPS+OSTIE)</div>
              <div class="bar-track">
                <div class="bar-fill bg-amber-500" :style="{ width: `${payrollBars.employerCharges}%` }"></div>
              </div>
              <div class="bar-val">{{ formatCurrency(hrMetrics.total_employer_charges || 0) }}</div>
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

const payrollBars = computed(() => {
  const gross = Math.max(Number(hrMetrics.value.total_gross_payroll || 0), 0)
  const employeeCharges = Math.max(Number(hrMetrics.value.total_employee_deductions || 0), 0)
  const net = Math.max(Number(hrMetrics.value.total_net_payroll || 0), 0)
  const employerCharges = Math.max(Number(hrMetrics.value.total_employer_charges || 0), 0)
  const maximum = Math.max(gross, employeeCharges, net, employerCharges, 1)
  const width = value => Math.min(100, Math.max(0, (value / maximum) * 100))

  return {
    gross: width(gross),
    employeeCharges: width(employeeCharges),
    net: width(net),
    employerCharges: width(employerCharges)
  }
})

const salesTrend = computed(() => Array.isArray(salesMetrics.value.sales_trend) ? salesMetrics.value.sales_trend : [])
const trendMax = computed(() => Math.max(...salesTrend.value.map(point => Number(point.revenue || 0)), 1))

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

function formatCompactCurrency(val) {
  return new Intl.NumberFormat('fr-FR', { notation: 'compact', maximumFractionDigits: 1 }).format(Number(val || 0))
}

function formatMonth(period) {
  if (!period) return '-'
  return new Intl.DateTimeFormat('fr-FR', { month: 'short' }).format(new Date(`${period}-02`))
}

function trendHeight(value) {
  return Math.max(4, (Number(value || 0) / trendMax.value) * 100)
}

function variationLabel(value) {
  if (value === null || value === undefined) return 'Nouveau / non comparable'
  const numeric = Number(value)
  return `${numeric >= 0 ? '+' : ''}${numeric.toFixed(1)} %`
}

function variationClass(value) {
  if (value === null || value === undefined) return 'variation-label--neutral'
  return Number(value) >= 0 ? 'variation-label--positive' : 'variation-label--negative'
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

.dashboard-insights {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(320px, 1fr);
  gap: var(--space-6);
}

.chart-description {
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
  margin-bottom: var(--space-4);
}

.trend-chart {
  display: flex;
  align-items: end;
  gap: var(--space-4);
  min-height: 190px;
  padding: var(--space-4) var(--space-2) 0;
  border-bottom: 1px solid var(--color-border);
}

.trend-column {
  display: flex;
  align-items: center;
  flex: 1;
  flex-direction: column;
  gap: var(--space-2);
  min-width: 42px;
  height: 100%;
  justify-content: end;
}

.trend-value,
.trend-label {
  color: var(--color-text-muted);
  font-size: 0.68rem;
  white-space: nowrap;
}

.trend-bar-track {
  align-items: end;
  background: var(--color-bg);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  display: flex;
  height: 120px;
  overflow: hidden;
  width: min(42px, 100%);
}

.trend-bar {
  background: linear-gradient(180deg, var(--color-primary), #73a3ff);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  min-height: 4px;
  transition: height 0.35s ease;
  width: 100%;
}

.variation-grid {
  display: grid;
  gap: var(--space-4);
  grid-template-rows: repeat(3, 1fr);
}

.variation-card {
  border-left: 3px solid var(--color-primary);
  display: flex;
  gap: var(--space-1);
  justify-content: center;
  padding: var(--space-4);
}

.variation-value {
  font-size: var(--font-size-xl);
}

.variation-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.variation-label--positive { color: var(--color-success); }
.variation-label--negative { color: var(--color-danger); }
.variation-label--neutral { color: var(--color-text-muted); }

.empty-state {
  color: var(--color-text-muted);
  padding: var(--space-8) 0;
  text-align: center;
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

@media (max-width: 900px) {
  .dashboard-insights {
    grid-template-columns: 1fr;
  }
}

</style>
