<template>
  <AppLayout>
    <PageHeader
      :title="employeeName"
      subtitle="Fiche complète salarié, contrat et informations RH"
      showBack
      backFallback="/hr"
    />

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <div v-if="loading" class="detail-card">Chargement de la fiche employe...</div>

    <div v-else-if="employee" class="detail-grid">
      <AppCard class="summary-card">
        <div class="summary-top">
          <div>
            <p class="eyebrow">Salarie</p>
            <h2>{{ employeeName }}</h2>
            <p class="text-muted">{{ employee.email || 'Email non renseigne' }}</p>
          </div>
          <span :class="['badge', employee.status === 'ACTIF' ? 'badge-success' : 'badge-warning']">{{ employee.status || 'ACTIF' }}</span>
        </div>
        <div class="summary-metrics">
          <div>
            <span>Matricule</span>
            <strong>{{ employee.matricule || '-' }}</strong>
          </div>
          <div>
            <span>Poste</span>
            <strong>{{ employee.job_title || employee.position || '-' }}</strong>
          </div>
          <div>
            <span>Salaire brut</span>
            <strong>{{ formatCurrency(employee.base_salary) }}</strong>
          </div>
          <div>
            <span>Anciennete</span>
            <strong>{{ employee.seniority_label || '-' }}</strong>
          </div>
        </div>
      </AppCard>

      <AppCard>
        <h3>Identite</h3>
        <div class="info-grid">
          <InfoItem label="Prenom" :value="employee.first_name" />
          <InfoItem label="Nom" :value="employee.last_name" />
          <InfoItem label="Email" :value="employee.email" />
          <InfoItem label="Telephone" :value="employee.phone" />
          <InfoItem label="CIN" :value="employee.cin || employee.cin_number" />
          <InfoItem label="Situation familiale" :value="employee.marital_status || employee.civil_status" />
          <InfoItem label="Enfants a charge" :value="employee.children_count ?? employee.number_of_children" />
          <InfoItem label="Adresse" :value="employee.address" />
        </div>
      </AppCard>

      <AppCard>
        <h3>Contrat et poste</h3>
        <div class="info-grid">
          <InfoItem label="Departement" :value="employee.department" />
          <InfoItem label="Poste" :value="employee.job_title || employee.position" />
          <InfoItem label="Categorie" :value="employee.category" />
          <InfoItem label="Contrat" :value="employee.contract_type" />
          <InfoItem label="Date embauche" :value="formatDate(employee.hire_date || employee.hiring_date)" />
          <InfoItem label="Fin contrat" :value="formatDate(employee.end_contract_date)" />
          <InfoItem label="Responsable" :value="employee.manager_id || employee.supervisor_id" />
          <InfoItem label="Compte utilisateur lie" :value="employee.user_id" />
        </div>
      </AppCard>

      <AppCard>
        <h3>Paie et contacts</h3>
        <div class="info-grid">
          <InfoItem label="Salaire de base" :value="formatCurrency(employee.base_salary)" />
          <InfoItem label="Devise" :value="employee.currency" />
          <InfoItem label="Banque" :value="employee.bank_name" />
          <InfoItem label="Compte bancaire" :value="employee.bank_account || employee.rib" />
          <InfoItem label="Contact urgence" :value="employee.emergency_contact_name" />
          <InfoItem label="Telephone urgence" :value="employee.emergency_contact_phone" />
        </div>
      </AppCard>

      <AppCard>
        <h3>Notes RH</h3>
        <p class="notes">{{ employee.notes || 'Aucune note RH enregistree.' }}</p>
      </AppCard>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import hrService from '../../services/hrService'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const InfoItem = defineComponent({
  props: {
    label: { type: String, required: true },
    value: { type: [String, Number], default: null }
  },
  setup(props) {
    return () => h('div', { class: 'info-item' }, [
      h('span', props.label),
      h('strong', props.value === null || props.value === undefined || props.value === '' ? '-' : props.value)
    ])
  }
})

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const pageError = ref('')
const employee = ref(null)

const employeeName = computed(() => {
  if (!employee.value) return 'Fiche employe'
  return `${employee.value.first_name || ''} ${employee.value.last_name || ''}`.trim() || 'Fiche employe'
})

function formatCurrency(value) {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(amount)
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium' }).format(new Date(value))
}

async function loadEmployee() {
  loading.value = true
  pageError.value = ''
  try {
    const res = await hrService.getEmployee(route.params.id)
    employee.value = res.data
  } catch (error) {
    pageError.value = error.response?.data?.detail || 'Impossible de charger la fiche employe.'
  } finally {
    loading.value = false
  }
}

onMounted(loadEmployee)
</script>

<style scoped>
.detail-grid {
  display: grid;
  gap: var(--space-4);
}

.detail-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-muted);
  padding: var(--space-6);
}

.summary-card {
  border-left: 4px solid var(--color-primary);
}

.summary-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

.summary-top h2,
h3 {
  color: var(--color-text);
  margin: 0 0 var(--space-3);
}

.eyebrow {
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--space-1);
  text-transform: uppercase;
}

.summary-metrics,
.info-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.summary-metrics {
  margin-top: var(--space-4);
}

.summary-metrics div,
.info-item {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
}

.summary-metrics span,
.info-item span {
  color: var(--color-text-muted);
  display: block;
  font-size: var(--font-size-xs);
  margin-bottom: var(--space-1);
}

.summary-metrics strong,
.info-item strong {
  color: var(--color-text);
}

.notes {
  color: var(--color-text);
  margin: 0;
}

.rotate-left {
  transform: rotate(90deg);
}
</style>
