<template>
  <AppLayout>
    <PageHeader
      title="Ressources Humaines & Gestion des Talents"
      subtitle="Fiches employés, suivi des temps & congés, gestion de la paie et évaluation des performances"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" @click="openCreateTimeOffModal">
          <AppIcon name="clock" size="16" />
          <span>Demande de Congé</span>
        </AppButton>
        <AppButton variant="primary" size="sm" @click="openCreateEmployeeModal">
          <AppIcon name="plus" size="16" />
          <span>Nouveau Salarié</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <!-- Top KPI Cards -->
    <div class="kpi-grid mb-6">
      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Effectif Total</span>
          <span class="kpi-value">{{ overview.total_employees || 0 }} <span class="kpi-unit">salariés</span></span>
          <span class="kpi-sub font-semibold color-success">Equipe active & sous contrat</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--primary">
          <AppIcon name="users" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Masse Salariale Mensuelle (Net)</span>
          <span class="kpi-value">{{ formatCurrency(overview.total_net_payroll_monthly) }}</span>
          <span class="kpi-sub text-muted">Hors charges patronales</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--success">
          <AppIcon name="dollar-sign" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Congés en Attente</span>
          <span class="kpi-value color-warning">{{ overview.pending_time_off_count || 0 }}</span>
          <span class="kpi-sub color-warning">Demandes à valider</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--warning">
          <AppIcon name="clock" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Performance Moyen RH</span>
          <span class="kpi-value color-primary">{{ overview.average_performance_score || 0 }}%</span>
          <span class="kpi-sub color-success">Note globale de l'équipe</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--info">
          <AppIcon name="shield" size="24" />
        </div>
      </AppCard>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-header mb-4">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-btn', { 'tab-btn--active': activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <AppIcon :name="tab.icon" size="16" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- TAB 1: EMPLOYES -->
    <div v-if="activeTab === 'employees'">
      <div class="table-toolbar">
        <div class="table-search">
          <AppIcon name="search" size="16" class="text-muted" />
          <input v-model="searchQuery" type="text" placeholder="Rechercher par nom, département ou poste..." />
        </div>
        <AppButton variant="primary" size="sm" @click="openCreateEmployeeModal">
          <AppIcon name="plus" size="14" />
          <span>Ajouter un Employé</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsEmployees"
        :items="filteredEmployees"
        :loading="loading"
        empty-text="Aucun salarié trouvé dans le registre RH."
      >
        <template #col-matricule="{ value }">
          <span class="sku-badge font-mono">{{ value }}</span>
        </template>

        <template #col-name="{ item }">
          <div>
            <strong>{{ item.first_name }} {{ item.last_name }}</strong>
            <div class="text-xs text-muted">{{ item.email }}</div>
          </div>
        </template>

        <template #col-base_salary="{ value }">
          <strong>{{ formatCurrency(value) }}</strong>
        </template>

        <template #col-status="{ value }">
          <AppBadge
            :variant="value === 'ACTIF' ? 'success' : value === 'CONGE' ? 'warning' : 'danger'"
            :label="value"
          />
        </template>
      </AppTable>
    </div>

    <!-- TAB 2: TEMPS ET ABSENCES -->
    <div v-if="activeTab === 'timeoff'">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Demandes de Congés & Suivi des Absences</h3>
        <AppButton variant="primary" size="sm" @click="openCreateTimeOffModal">
          <AppIcon name="plus" size="14" />
          <span>Saisir une Demande de Congé</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsTimeOff"
        :items="timeOffRequests"
        :loading="loading"
        empty-text="Aucune demande de congé enregistrée."
      >
        <template #col-leave_type="{ value }">
          <AppBadge
            :variant="value === 'PAYE' ? 'primary' : value === 'RTT' ? 'info' : 'warning'"
            :label="value"
          />
        </template>

        <template #col-status="{ value }">
          <AppBadge
            :variant="value === 'ACCEPTE' ? 'success' : value === 'EN_ATTENTE' ? 'warning' : 'danger'"
            :label="value"
          />
        </template>

        <template #actions="{ item }">
          <div v-if="item.status === 'EN_ATTENTE'" class="flex gap-2">
            <AppButton variant="success" size="xs" @click="handleValidateTimeOff(item.id_time_off, 'ACCEPTER')">
              Accepter
            </AppButton>
            <AppButton variant="danger" size="xs" @click="handleValidateTimeOff(item.id_time_off, 'REFUSER')">
              Refuser
            </AppButton>
          </div>
          <span v-else class="text-xs text-muted">Traité</span>
        </template>
      </AppTable>
    </div>

    <!-- TAB 3: PAIE -->
    <div v-if="activeTab === 'payroll'">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Gestion de la Paie & Bulletin des Salaires</h3>
        <AppButton variant="primary" size="sm" @click="openCreatePayrollModal">
          <AppIcon name="plus" size="14" />
          <span>Générer un Bulletin de Paie</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsPayrolls"
        :items="payrolls"
        :loading="loading"
        empty-text="Aucune fiche de paie enregistrée."
      >
        <template #col-period="{ value }">
          <span class="sku-badge font-mono">{{ value }}</span>
        </template>

        <template #col-gross_salary="{ value }">
          {{ formatCurrency(value) }}
        </template>

        <template #col-net_salary="{ value }">
          <strong class="color-success text-md">{{ formatCurrency(value) }}</strong>
        </template>

        <template #col-payment_status="{ value }">
          <AppBadge
            :variant="value === 'PAYE' ? 'success' : 'warning'"
            :label="value"
          />
        </template>
      </AppTable>
    </div>

    <!-- TAB 4: PERFORMANCE & COMPETENCES -->
    <div v-if="activeTab === 'performance'">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Évaluations de Performance & Plan de Formations</h3>
        <AppButton variant="primary" size="sm" @click="openCreateEvaluationModal">
          <AppIcon name="plus" size="14" />
          <span>Nouvelle Évaluation RH</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsPerformance"
        :items="performanceEvaluations"
        :loading="loading"
        empty-text="Aucune évaluation enregistrée."
      >
        <template #col-performance_score="{ value }">
          <span class="text-lg font-bold color-primary">{{ value }}%</span>
        </template>

        <template #col-rating_label="{ value }">
          <AppBadge
            :variant="value === 'EXCELLENT' ? 'success' : value === 'SATISFAISANT' ? 'info' : 'warning'"
            :label="value"
          />
        </template>
      </AppTable>
    </div>

    <!-- Modal Nouveau Salarié -->
    <AppModal v-model="showEmployeeModal" title="Créer une Fiche Salarié" size="sm">
      <form @submit.prevent="saveEmployee" class="modal-form">
        <AppInput id="emp-fn" v-model="empForm.first_name" label="Prénom *" required />
        <AppInput id="emp-ln" v-model="empForm.last_name" label="Nom *" required />
        <AppInput id="emp-email" v-model="empForm.email" type="email" label="Email Professionnel *" required />
        <AppInput id="emp-phone" v-model="empForm.phone" label="Téléphone" />

        <div class="form-group">
          <label class="form-label">Département / Service *</label>
          <select v-model="empForm.department" class="form-select" required>
            <option value="IT & R&D">IT & R&D</option>
            <option value="Ventes & Marketing">Ventes & Marketing</option>
            <option value="Achats & Logistique">Achats & Logistique</option>
            <option value="Finance & Comptabilité">Finance & Comptabilité</option>
            <option value="Ressources Humaines">Ressources Humaines</option>
          </select>
        </div>

        <AppInput id="emp-job" v-model="empForm.job_title" label="Intitulé du poste *" required />

        <div class="form-group">
          <label class="form-label">Type de contrat *</label>
          <select v-model="empForm.contract_type" class="form-select" required>
            <option value="CDI">CDI</option>
            <option value="CDD">CDD</option>
            <option value="Stage">Stage</option>
            <option value="Prestation">Prestation</option>
          </select>
        </div>

        <AppInput id="emp-hire" v-model="empForm.hire_date" type="date" label="Date d'embauche *" required />
        <AppInput id="emp-sal" v-model.number="empForm.base_salary" type="number" step="100" label="Salaire brut mensuel (€) *" required />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showEmployeeModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveEmployee">Enregistrer Salarié</AppButton>
      </template>
    </AppModal>

    <!-- Modal Demande de Congé -->
    <AppModal v-model="showTimeOffModal" title="Demande de Congé / Absence" size="sm">
      <form @submit.prevent="saveTimeOff" class="modal-form">
        <div class="form-group">
          <label class="form-label">Salarié concerné *</label>
          <select v-model="timeOffForm.employee_id" class="form-select" required>
            <option :value="null">Sélectionner un employé</option>
            <option v-for="e in employees" :key="e.id_employee" :value="e.id_employee">
              {{ e.first_name }} {{ e.last_name }} ({{ e.department }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Type d'absence *</label>
          <select v-model="timeOffForm.leave_type" class="form-select" required>
            <option value="PAYE">Congé Payé</option>
            <option value="RTT">RTT</option>
            <option value="MALADIE">Arrêt Maladie</option>
            <option value="SANS_SOLDE">Congé Sans Solde</option>
          </select>
        </div>

        <AppInput id="to-start" v-model="timeOffForm.start_date" type="date" label="Date de début *" required />
        <AppInput id="to-end" v-model="timeOffForm.end_date" type="date" label="Date de fin *" required />
        <AppInput id="to-days" v-model.number="timeOffForm.days_count" type="number" step="0.5" label="Nombre de jours *" required />
        <AppInput id="to-reason" v-model="timeOffForm.reason" label="Motif / Justificatif" />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showTimeOffModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveTimeOff">Soumettre la Demande</AppButton>
      </template>
    </AppModal>

    <!-- Modal Générer Fiche de Paie -->
    <AppModal v-model="showPayrollModal" title="Générer un Bulletin de Paie" size="sm">
      <form @submit.prevent="savePayroll" class="modal-form">
        <div class="form-group">
          <label class="form-label">Salarié *</label>
          <select v-model="payrollForm.employee_id" class="form-select" required @change="onEmployeeSelectForPayroll">
            <option :value="null">Sélectionner un employé</option>
            <option v-for="e in employees" :key="e.id_employee" :value="e.id_employee">
              {{ e.first_name }} {{ e.last_name }}
            </option>
          </select>
        </div>

        <AppInput id="pay-per" v-model="payrollForm.period" label="Période de paie *" placeholder="2026-08" required />
        <AppInput id="pay-gross" v-model.number="payrollForm.gross_salary" type="number" step="10" label="Salaire Brut (€) *" required />
        <AppInput id="pay-bonus" v-model.number="payrollForm.bonus" type="number" step="10" label="Primes (€)" />
        <AppInput id="pay-ot-hrs" v-model.number="payrollForm.overtime_hours" type="number" step="0.5" label="Heures Sup (heures)" />
        <AppInput id="pay-ot-amt" v-model.number="payrollForm.overtime_amount" type="number" step="10" label="Heures Sup (€)" />
        <AppInput id="pay-ded" v-model.number="payrollForm.deductions" type="number" step="10" label="Retenues & Cotisations (€)" />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showPayrollModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="savePayroll">Valider la Paie</AppButton>
      </template>
    </AppModal>

    <!-- Modal Évaluation Performance -->
    <AppModal v-model="showEvaluationModal" title="Saisir une Évaluation RH" size="sm">
      <form @submit.prevent="saveEvaluation" class="modal-form">
        <div class="form-group">
          <label class="form-label">Salarié évalué *</label>
          <select v-model="evalForm.employee_id" class="form-select" required>
            <option :value="null">Sélectionner un employé</option>
            <option v-for="e in employees" :key="e.id_employee" :value="e.id_employee">
              {{ e.first_name }} {{ e.last_name }}
            </option>
          </select>
        </div>

        <AppInput id="ev-per" v-model="evalForm.evaluation_period" label="Période d'évaluation *" placeholder="Année 2026" required />
        <AppInput id="ev-score" v-model.number="evalForm.performance_score" type="number" step="0.5" label="Score de performance (0 à 100) *" required />
        <AppInput id="ev-goals" v-model="evalForm.goals_achieved" label="Objectifs & Réalisations *" required />
        <AppInput id="ev-train" v-model="evalForm.training_recommended" label="Formations recommandées" />
        <AppInput id="ev-evol" v-model="evalForm.career_evolution_notes" label="Perspective d'évolution de carrière" />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showEvaluationModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveEvaluation">Enregistrer l'Évaluation</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppTable from '../../components/ui/AppTable.vue'
import AppBadge from '../../components/ui/AppBadge.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const activeTab = ref('employees')
const overview = ref({})
const employees = ref([])
const timeOffRequests = ref([])
const payrolls = ref([])
const performanceEvaluations = ref([])

const searchQuery = ref('')
const loading = ref(false)
const saving = ref(false)

const pageError = ref('')
const pageSuccess = ref('')

const showEmployeeModal = ref(false)
const showTimeOffModal = ref(false)
const showPayrollModal = ref(false)
const showEvaluationModal = ref(false)

const tabs = [
  { id: 'employees', label: 'Fiches Employés', icon: 'users' },
  { id: 'timeoff', label: 'Temps & Absences', icon: 'clock' },
  { id: 'payroll', label: 'Gestion de la Paie', icon: 'dollar-sign' },
  { id: 'performance', label: 'Performance & Évaluations', icon: 'shield' }
]

const empForm = ref({
  first_name: '', last_name: '', email: '', phone: '',
  department: 'IT & R&D', job_title: '', contract_type: 'CDI',
  hire_date: '2026-01-01', base_salary: 3000.0
})

const timeOffForm = ref({
  employee_id: null, leave_type: 'PAYE', start_date: '', end_date: '', days_count: 1.0, reason: ''
})

const payrollForm = ref({
  employee_id: null, period: '2026-08', gross_salary: 3000.0, bonus: 0.0, overtime_hours: 0.0, overtime_amount: 0.0, deductions: 660.0
})

const evalForm = ref({
  employee_id: null, evaluation_period: 'Année 2026', performance_score: 90.0, goals_achieved: '', training_recommended: '', career_evolution_notes: ''
})

const filteredEmployees = computed(() => {
  if (!searchQuery.value) return employees.value
  const q = searchQuery.value.toLowerCase()
  return employees.value.filter(e =>
    e.first_name.toLowerCase().includes(q) ||
    e.last_name.toLowerCase().includes(q) ||
    e.department.toLowerCase().includes(q) ||
    e.job_title.toLowerCase().includes(q) ||
    e.matricule.toLowerCase().includes(q)
  )
})

const columnsEmployees = [
  { key: 'matricule', label: 'Matricule', width: '15%' },
  { key: 'name', label: 'Salarié', width: '25%' },
  { key: 'department', label: 'Département', width: '20%' },
  { key: 'job_title', label: 'Poste Occupé', width: '20%' },
  { key: 'seniority_label', label: 'Ancienneté', width: '12%' },
  { key: 'status', label: 'Statut', width: '8%' }
]

const columnsTimeOff = [
  { key: 'employee_name', label: 'Salarié', width: '25%' },
  { key: 'leave_type', label: 'Type d\'Absence', width: '15%' },
  { key: 'start_date', label: 'Début', width: '15%' },
  { key: 'end_date', label: 'Fin', width: '15%' },
  { key: 'days_count', label: 'Jours', width: '10%' },
  { key: 'status', label: 'Statut', width: '20%' }
]

const columnsPayrolls = [
  { key: 'period', label: 'Période', width: '12%' },
  { key: 'employee_name', label: 'Salarié', width: '25%' },
  { key: 'gross_salary', label: 'Brut', width: '15%' },
  { key: 'net_salary', label: 'Net à Payer', width: '18%' },
  { key: 'payment_status', label: 'Statut', width: '15%' }
]

const columnsPerformance = [
  { key: 'employee_name', label: 'Salarié', width: '22%' },
  { key: 'evaluation_period', label: 'Période', width: '15%' },
  { key: 'performance_score', label: 'Score %', width: '12%' },
  { key: 'goals_achieved', label: 'Objectifs & Réalisations', width: '36%' },
  { key: 'rating_label', label: 'Évaluation', width: '15%' }
]

async function loadAllHRData() {
  loading.value = true
  pageError.value = ''
  try {
    const [ovRes, empRes, toRes, payRes, perfRes] = await Promise.all([
      api.get('/hr/overview'),
      api.get('/hr/employees'),
      api.get('/hr/time-off'),
      api.get('/hr/payrolls'),
      api.get('/hr/performance')
    ])

    overview.value = ovRes.data || {}
    employees.value = empRes.data || []
    timeOffRequests.value = toRes.data || []
    payrolls.value = payRes.data || []
    performanceEvaluations.value = perfRes.data || []
  } catch (e) {
    pageError.value = 'Erreur lors du chargement des données RH.'
  } finally {
    loading.value = false
  }
}

function formatCurrency(val) {
  if (val === undefined || val === null) return '0,00 €'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val)
}

function openCreateEmployeeModal() {
  empForm.value = {
    first_name: '', last_name: '', email: '', phone: '',
    department: 'IT & R&D', job_title: '', contract_type: 'CDI',
    hire_date: '2026-01-01', base_salary: 3200.0
  }
  showEmployeeModal.value = true
}

function openCreateTimeOffModal() {
  timeOffForm.value = {
    employee_id: employees.value.length ? employees.value[0].id_employee : null,
    leave_type: 'PAYE', start_date: '', end_date: '', days_count: 1.0, reason: ''
  }
  showTimeOffModal.value = true
}

function openCreatePayrollModal() {
  const emp = employees.value.length ? employees.value[0] : null
  payrollForm.value = {
    employee_id: emp ? emp.id_employee : null,
    period: '2026-08',
    gross_salary: emp ? emp.base_salary : 3000.0,
    bonus: 0.0, overtime_hours: 0.0, overtime_amount: 0.0, deductions: emp ? roundVal(emp.base_salary * 0.22) : 660.0
  }
  showPayrollModal.value = true
}

function onEmployeeSelectForPayroll() {
  const e = employees.value.find(emp => emp.id_employee === payrollForm.value.employee_id)
  if (e) {
    payrollForm.value.gross_salary = e.base_salary
    payrollForm.value.deductions = roundVal(e.base_salary * 0.22)
  }
}

function roundVal(v) {
  return Math.round(v * 100) / 100
}

function openCreateEvaluationModal() {
  evalForm.value = {
    employee_id: employees.value.length ? employees.value[0].id_employee : null,
    evaluation_period: 'Année 2026', performance_score: 92.0, goals_achieved: '', training_recommended: '', career_evolution_notes: ''
  }
  showEvaluationModal.value = true
}

async function saveEmployee() {
  if (!empForm.value.first_name || !empForm.value.last_name) return
  saving.value = true
  try {
    await api.post('/hr/employees', empForm.value)
    pageSuccess.value = 'Nouveau salarié enregistré avec succès dans le registre RH !'
    showEmployeeModal.value = false
    await loadAllHRData()
  } catch (e) {
    pageError.value = 'Erreur lors de la création de la fiche salarié.'
  } finally {
    saving.value = false
  }
}

async function saveTimeOff() {
  if (!timeOffForm.value.employee_id || !timeOffForm.value.start_date) return
  saving.value = true
  try {
    await api.post('/hr/time-off', timeOffForm.value)
    pageSuccess.value = 'Demande de congé enregistrée !'
    showTimeOffModal.value = false
    await loadAllHRData()
  } catch (e) {
    pageError.value = 'Erreur lors de la création de la demande de congé.'
  } finally {
    saving.value = false
  }
}

async function handleValidateTimeOff(toId, action) {
  loading.value = true
  try {
    await api.put(`/hr/time-off/${toId}/validate`, {
      action: action,
      comment: action === 'ACCEPTER' ? 'Congé accordé' : 'Non compatible avec le planning'
    })
    pageSuccess.value = `Demande de congé ${action === 'ACCEPTER' ? 'acceptée' : 'refusée'} !`
    await loadAllHRData()
  } catch (e) {
    pageError.value = 'Erreur lors du traitement de la demande.'
  } finally {
    loading.value = false
  }
}

async function savePayroll() {
  if (!payrollForm.value.employee_id || !payrollForm.value.period) return
  saving.value = true
  try {
    await api.post('/hr/payrolls', payrollForm.value)
    pageSuccess.value = 'Fiche de paie générée et enregistrée !'
    showPayrollModal.value = false
    await loadAllHRData()
  } catch (e) {
    pageError.value = 'Erreur lors de la génération de la paie.'
  } finally {
    saving.value = false
  }
}

async function saveEvaluation() {
  if (!evalForm.value.employee_id || !evalForm.value.goals_achieved) return
  saving.value = true
  try {
    await api.post('/hr/performance', evalForm.value)
    pageSuccess.value = 'Évaluation de performance enregistrée avec succès !'
    showEvaluationModal.value = false
    await loadAllHRData()
  } catch (e) {
    pageError.value = 'Erreur lors de l\'enregistrement de l\'évaluation.'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadAllHRData()
})
</script>
