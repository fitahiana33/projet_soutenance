<template>
  <AppLayout>
    <PageHeader
      title="Ressources Humaines & Gestion des Talents"
      subtitle="Fiches employés, suivi des temps & congés, calendrier des jours fériés, paie et performance"
      showBack
      backFallback="/dashboard"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" @click="handleExportHRExcel">
          <AppIcon name="file-text" size="16" />
          <span>Exporter Excel</span>
        </AppButton>
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
          <span class="kpi-value">{{ overview.active_employees || overview.total_employees || 0 }} <span class="kpi-unit">actifs</span></span>
          <span class="kpi-sub font-semibold color-success">Turnover: {{ overview.turnover_rate_percent || 0 }}%</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--primary">
          <AppIcon name="users" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Masse Salariale Mensuelle</span>
          <span class="kpi-value">{{ formatCurrency(overview.total_net_payroll_monthly || overview.total_net_payroll || 0) }}</span>
          <span class="kpi-sub text-muted">Coût total: {{ formatCurrency(overview.total_gross_payroll || 0) }}</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--success">
          <AppIcon name="dollar-sign" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Congés & Absentéisme</span>
          <span class="kpi-value color-warning">{{ overview.pending_time_off_count || 0 }} <span class="kpi-unit">en attente</span></span>
          <span class="kpi-sub color-info">Restant: {{ overview.remaining_leave_days || 0 }}j | Taux: {{ overview.absenteeism_rate_percent || 0 }}%</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--warning">
          <AppIcon name="clock" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Performance Moyenne</span>
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
          <AppBadge variant="success" label="Actif" />
        </template>

        <template #actions="{ item }">
          <AppButton variant="secondary" size="xs" @click="router.push(`/hr/employees/${item.id_employee}`)">
            <AppIcon name="eye" size="12" />
            <span>Fiche</span>
          </AppButton>
        </template>
      </AppTable>
    </div>

    <!-- TAB 2: TEMPS & ABSENCES -->
    <div v-if="activeTab === 'timeoff'">
      <div class="table-toolbar justify-end">
        <AppButton variant="primary" size="sm" @click="openCreateTimeOffModal">
          <AppIcon name="plus" size="14" />
          <span>Nouvelle Demande de Congé</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsTimeOff"
        :items="timeOffRequests"
        :loading="loading"
        empty-text="Aucune demande de congé enregistrée."
      >
        <template #col-leave_type="{ value }">
          <span class="badge badge-info">{{ value }}</span>
        </template>

        <template #col-status="{ item, value }">
          <div class="flex items-center gap-2">
            <span :class="['badge', value === 'ACCEPTE' ? 'badge-success' : (value === 'REFUSE' ? 'badge-danger' : 'badge-warning')]">
              {{ value }}
            </span>
            <div v-if="value === 'EN_ATTENTE'" class="flex gap-1">
              <button class="btn btn-success btn-xs" @click="handleValidateTimeOff(item.id_time_off, 'ACCEPTER')">✓</button>
              <button class="btn btn-danger btn-xs" @click="handleValidateTimeOff(item.id_time_off, 'REFUSER')">✗</button>
            </div>
          </div>
        </template>
      </AppTable>
    </div>

    <!-- TAB 3: PAIE -->
    <div v-if="activeTab === 'payroll'">
      <div class="table-toolbar justify-end">
        <AppButton variant="primary" size="sm" @click="openCreatePayrollModal">
          <AppIcon name="plus" size="14" />
          <span>Générer un Bulletin de Paie</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsPayrolls"
        :items="payrolls"
        :loading="loading"
        empty-text="Aucun bulletin de paie généré."
      >
        <template #col-period="{ value }">
          <span class="sku-badge font-mono">{{ value }}</span>
        </template>

        <template #col-gross_salary="{ value }">
          <span>{{ formatCurrency(value) }}</span>
        </template>

        <template #col-net_salary="{ value }">
          <strong class="color-primary">{{ formatCurrency(value) }}</strong>
        </template>

        <template #col-payment_status="{ value }">
          <AppBadge variant="success" label="PAYÉ" />
        </template>
      </AppTable>
    </div>

    <!-- TAB 4: PERFORMANCE & EVALUATIONS -->
    <div v-if="activeTab === 'performance'">
      <div class="table-toolbar justify-end">
        <AppButton variant="primary" size="sm" @click="openCreateEvaluationModal">
          <AppIcon name="plus" size="14" />
          <span>Nouvelle Évaluation</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsPerformance"
        :items="performanceEvaluations"
        :loading="loading"
        empty-text="Aucune évaluation de performance trouvée."
      >
        <template #col-performance_score="{ value }">
          <strong :class="value >= 80 ? 'color-success' : 'color-warning'">{{ value }}%</strong>
        </template>

        <template #col-rating_label="{ value }">
          <span class="badge badge-success">{{ value }}</span>
        </template>
      </AppTable>
    </div>

    <!-- TAB 5: JOURS FERIES LEGAUX -->
    <div v-if="activeTab === 'holidays'">
      <div class="table-toolbar justify-between">
        <p class="text-xs text-muted">Calendrier officiel des jours fériés légaux et chômés.</p>
        <AppButton variant="primary" size="sm" @click="openCreateHolidayModal">
          <AppIcon name="plus" size="14" />
          <span>Ajouter un Jour Férié</span>
        </AppButton>
      </div>

      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nom du Jour Férié</th>
              <th>Date (AAAA-MM-JJ)</th>
              <th>Type de Répétition</th>
              <th>Description</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hol in publicHolidays" :key="hol.id_holiday">
              <td class="font-mono text-xs text-muted">#{{ hol.id_holiday }}</td>
              <td class="font-bold color-text">{{ hol.name }}</td>
              <td class="font-mono text-amber-400 font-semibold">{{ hol.date }}</td>
              <td>
                <span :class="['badge', hol.is_recurring ? 'badge-info' : 'badge-neutral']">
                  {{ hol.is_recurring ? 'Annuel Répétitif' : 'Ponctuel' }}
                </span>
              </td>
              <td class="text-xs text-slate-300">{{ hol.description || '-' }}</td>
              <td>
                <div class="flex justify-end gap-2">
                  <button class="btn btn-secondary btn-xs" @click="openEditHolidayModal(hol)"><AppIcon name="edit" size="16" /> Éditer</button>
                  <button class="btn btn-danger btn-xs" @click="confirmDeleteHoliday(hol)"><AppIcon name="trash" size="16" /> Supprimer</button>
                </div>
              </td>
            </tr>
            <tr v-if="publicHolidays.length === 0">
              <td colspan="6" class="text-center py-6 text-muted">Aucun jour férié enregistré pour le moment.</td>
            </tr>
          </tbody>
        </table>
      </div>
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
        <AppInput id="to-reason" v-model="timeOffForm.reason" label="Motif (optionnel)" />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showTimeOffModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveTimeOff">Valider la Demande</AppButton>
      </template>
    </AppModal>

    <!-- Modal Générer Bulletin de Paie -->
    <AppModal v-model="showPayrollModal" title="Générer un Bulletin de Paie" size="sm">
      <form @submit.prevent="savePayroll" class="modal-form">
        <div class="form-group">
          <label class="form-label">Salarié concerné *</label>
          <select v-model="payrollForm.employee_id" class="form-select" required @change="onEmployeeSelectForPayroll">
            <option :value="null">Sélectionner un employé</option>
            <option v-for="e in employees" :key="e.id_employee" :value="e.id_employee">
              {{ e.first_name }} {{ e.last_name }} ({{ e.department }})
            </option>
          </select>
        </div>

        <AppInput id="pay-period" v-model="payrollForm.period" label="Période (AAAA-MM) *" placeholder="2026-08" required />
        <AppInput id="pay-gross" v-model.number="payrollForm.gross_salary" type="number" step="100" label="Salaire brut (€) *" required />
        <AppInput id="pay-bonus" v-model.number="payrollForm.bonus" type="number" step="50" label="Primes & Indemnités (€)" />
        <AppInput id="pay-ot" v-model.number="payrollForm.overtime_hours" type="number" step="0.5" label="Heures supplémentaires (Heures)" />
        <AppInput id="pay-ded" v-model.number="payrollForm.deductions" type="number" step="10" label="Total déductions / cotisations (€)" required />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showPayrollModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="savePayroll">Émettre le Bulletin</AppButton>
      </template>
    </AppModal>

    <!-- Modal Évaluation de Performance -->
    <AppModal v-model="showEvaluationModal" title="Saisir une Évaluation de Performance" size="sm">
      <form @submit.prevent="saveEvaluation" class="modal-form">
        <div class="form-group">
          <label class="form-label">Salarié évalué *</label>
          <select v-model="evalForm.employee_id" class="form-select" required>
            <option :value="null">Sélectionner un employé</option>
            <option v-for="e in employees" :key="e.id_employee" :value="e.id_employee">
              {{ e.first_name }} {{ e.last_name }} ({{ e.department }})
            </option>
          </select>
        </div>

        <AppInput id="eval-period" v-model="evalForm.evaluation_period" label="Période d'évaluation *" required />
        <AppInput id="eval-score" v-model.number="evalForm.performance_score" type="number" step="1" min="0" max="100" label="Score de performance (0-100%) *" required />
        <AppInput id="eval-goals" v-model="evalForm.goals_achieved" label="Objectifs réalisés *" required />
        <AppInput id="eval-training" v-model="evalForm.training_recommended" label="Formations recommandées" />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showEvaluationModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveEvaluation">Valider l'Évaluation</AppButton>
      </template>
    </AppModal>

    <!-- Modal Create / Edit Public Holiday -->
    <AppModal
      v-model="showHolidayModal"
      :title="editingHoliday ? 'Éditer le jour férié' : 'Ajouter un jour férié'"
      size="sm"
    >
      <form @submit.prevent="saveHoliday" class="modal-form space-y-4">
        <AppInput id="hol-name" v-model="holidayForm.name" label="Nom du jour férié *" placeholder="ex: Fête de l'Indépendance" required />
        <AppInput id="hol-date" v-model="holidayForm.date" type="date" label="Date (AAAA-MM-JJ) *" required />

        <div class="form-checkbox">
          <label class="checkbox-label">
            <input v-model="holidayForm.is_recurring" type="checkbox" />
            <span>Récurrent chaque année (Fête fixe)</span>
          </label>
        </div>

        <AppInput id="hol-desc" v-model="holidayForm.description" label="Description" placeholder="ex: Fête Nationale de Madagascar" />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showHolidayModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="savingHoliday" @click="saveHoliday">
          {{ editingHoliday ? 'Mettre à jour' : 'Enregistrer' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Modal Confirm Delete Holiday -->
    <AppModal v-model="showDeleteHolidayModal" title="Confirmer la suppression" size="sm">
      <p>Êtes-vous sûr de vouloir supprimer le jour férié <strong>{{ deletingHoliday?.name }}</strong> ({{ deletingHoliday?.date }}) ?</p>
      <template #footer>
        <AppButton variant="ghost" @click="showDeleteHolidayModal = false">Annuler</AppButton>
        <AppButton variant="danger" :loading="deletingHolidayStatus" @click="executeDeleteHoliday">Supprimer</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import hrService from '../../services/hrService'
import { exportToExcel } from '../../utils/excelExport'
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
const router = useRouter()
const loading = ref(false)
const saving = ref(false)

const pageError = ref('')
const pageSuccess = ref('')

const overview = ref({})
const employees = ref([])
const timeOffRequests = ref([])
const payrolls = ref([])
const performanceEvaluations = ref([])
const publicHolidays = ref([])

const searchQuery = ref('')

const showEmployeeModal = ref(false)
const showTimeOffModal = ref(false)
const showPayrollModal = ref(false)
const showEvaluationModal = ref(false)

const showHolidayModal = ref(false)
const showDeleteHolidayModal = ref(false)
const editingHoliday = ref(null)
const deletingHoliday = ref(null)
const savingHoliday = ref(false)
const deletingHolidayStatus = ref(false)

const tabs = [
  { id: 'employees', label: 'Fiches Employés', icon: 'users' },
  { id: 'timeoff', label: 'Temps & Absences', icon: 'clock' },
  { id: 'payroll', label: 'Gestion de la Paie', icon: 'dollar-sign' },
  { id: 'performance', label: 'Performance & Évaluations', icon: 'shield' },
  { id: 'holidays', label: 'Calendrier Jours Fériés', icon: 'clock' }
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

const holidayForm = ref({
  name: '',
  date: '',
  is_recurring: true,
  description: ''
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
    const [ovRes, empRes, toRes, payRes, perfRes, holRes] = await Promise.all([
      hrService.getOverview(),
      hrService.getEmployees(),
      hrService.getTimeOff(),
      hrService.getPayrolls(),
      hrService.getPerformance(),
      hrService.getHolidays()
    ])

    overview.value = ovRes.data || {}
    employees.value = empRes.data || []
    timeOffRequests.value = toRes.data || []
    payrolls.value = payRes.data || []
    performanceEvaluations.value = perfRes.data || []
    publicHolidays.value = holRes.data || []
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

function openCreateHolidayModal() {
  editingHoliday.value = null
  holidayForm.value = {
    name: '',
    date: new Date().toISOString().split('T')[0],
    is_recurring: true,
    description: ''
  }
  showHolidayModal.value = true
}

function openEditHolidayModal(hol) {
  editingHoliday.value = hol
  holidayForm.value = {
    name: hol.name,
    date: hol.date,
    is_recurring: hol.is_recurring,
    description: hol.description || ''
  }
  showHolidayModal.value = true
}

async function saveHoliday() {
  if (!holidayForm.value.name || !holidayForm.value.date) return
  savingHoliday.value = true
  try {
    if (editingHoliday.value) {
      await hrService.updateHoliday(editingHoliday.value.id_holiday, holidayForm.value)
      pageSuccess.value = 'Jour férié mis à jour avec succès.'
    } else {
      await hrService.createHoliday(holidayForm.value)
      pageSuccess.value = 'Nouveau jour férié ajouté au calendrier officiel.'
    }
    showHolidayModal.value = false
    await loadAllHRData()
  } catch (e) {
    pageError.value = 'Erreur lors de l\'enregistrement du jour férié.'
  } finally {
    savingHoliday.value = false
  }
}

function confirmDeleteHoliday(hol) {
  deletingHoliday.value = hol
  showDeleteHolidayModal.value = true
}

async function executeDeleteHoliday() {
  if (!deletingHoliday.value) return
  deletingHolidayStatus.value = true
  try {
    await hrService.deleteHoliday(deletingHoliday.value.id_holiday)
    pageSuccess.value = `Jour férié '${deletingHoliday.value.name}' supprimé avec succès.`
    showDeleteHolidayModal.value = false
    await loadAllHRData()
  } catch (e) {
    pageError.value = 'Erreur lors de la suppression du jour férié.'
  } finally {
    deletingHolidayStatus.value = false
  }
}

async function saveEmployee() {
  if (!empForm.value.first_name || !empForm.value.last_name) return
  saving.value = true
  try {
    await hrService.createEmployee(empForm.value)
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
    await hrService.createTimeOff(timeOffForm.value)
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
    await hrService.validateTimeOff(toId, {
      action,
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
    await hrService.createPayroll(payrollForm.value)
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
    await hrService.createEvaluation(evalForm.value)
    pageSuccess.value = 'Évaluation de performance enregistrée avec succès !'
    showEvaluationModal.value = false
    await loadAllHRData()
  } catch (e) {
    pageError.value = 'Erreur lors de l\'enregistrement de l\'évaluation.'
  } finally {
    saving.value = false
  }
}

function handleExportHRExcel() {
  if (activeTab.value === 'employees') {
    const cols = [
      { header: 'Matricule', key: 'registration_number' },
      { header: 'Nom', key: 'last_name' },
      { header: 'Prénom', key: 'first_name' },
      { header: 'Email', key: 'email' },
      { header: 'Poste', key: 'position' },
      { header: 'Département', key: 'department' },
      { header: 'Salaire de Base (€)', key: 'base_salary' },
      { header: 'Contrat', key: 'contract_type' },
      { header: 'Statut', key: 'status' }
    ]
    exportToExcel('effectif_salaries', 'Liste des Salariés', cols, employees.value)
  } else if (activeTab.value === 'payroll') {
    const cols = [
      { header: 'Salarié', key: 'employee_name' },
      { header: 'Période', key: 'period' },
      { header: 'Salaire Brut (€)', key: 'gross_salary' },
      { header: 'Primes (€)', key: 'bonus' },
      { header: 'Cotisations / Déductions (€)', key: 'deductions' },
      { header: 'Net à Payer (€)', key: 'net_salary' },
      { header: 'Statut', key: 'payment_status' }
    ]
    exportToExcel('etat_de_paie', 'État de Paie Mensuelle', cols, payrolls.value)
  } else if (activeTab.value === 'timeoff') {
    const cols = [
      { header: 'Salarié', key: 'employee_name' },
      { header: 'Type de Congé', key: 'leave_type' },
      { header: 'Date Début', key: 'start_date' },
      { header: 'Date Fin', key: 'end_date' },
      { header: 'Nombre Jours', key: 'days_count' },
      { header: 'Statut', key: 'status' }
    ]
    exportToExcel('suivi_conges', 'Demandes de Congés', cols, timeOffRequests.value)
  } else if (activeTab.value === 'holidays') {
    const cols = [
      { header: 'Nom du Jour Férié', key: 'name' },
      { header: 'Date (AAAA-MM-JJ)', key: 'date' },
      { header: 'Répétition', key: 'is_recurring', formatter: (val) => val ? 'Annuel' : 'Ponctuel' },
      { header: 'Description', key: 'description' }
    ]
    exportToExcel('jours_feries_legaux', 'Jours Fériés', cols, publicHolidays.value)
  } else {
    const cols = [
      { header: 'Salarié', key: 'employee_name' },
      { header: 'Évaluateur', key: 'evaluator_name' },
      { header: 'Période', key: 'review_period' },
      { header: 'Score (%)', key: 'performance_score' },
      { header: 'Appréciation', key: 'rating_label' }
    ]
    exportToExcel('evaluations_performance', 'Évaluations', cols, performanceEvaluations.value)
  }
}

onMounted(() => {
  loadAllHRData()
})
</script>

<style scoped>
.tabs-header {
  display: flex;
  gap: var(--space-2);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--space-2);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.9rem;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  border: none;
  background: none;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: var(--color-text);
  background-color: var(--color-bg);
}

.tab-btn--active {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.table-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.table-search {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-md);
  width: 320px;
}

.table-search input {
  border: none;
  background: none;
  color: var(--color-text);
  font-size: var(--font-size-xs);
  width: 100%;
}

.table-search input:focus {
  outline: none;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.form-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.form-select {
  padding: 0.45rem 0.75rem;
  font-size: var(--font-size-xs);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-surface);
  color: var(--color-text);
}

.form-checkbox {
  margin-top: var(--space-2);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  cursor: pointer;
}
</style>
