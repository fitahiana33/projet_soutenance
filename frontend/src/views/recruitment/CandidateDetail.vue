<template>
  <AppLayout>
    <PageHeader
      :title="candidateName"
      subtitle="Fiche complète candidat, CV et suivi du processus de recrutement"
      showBack
      backFallback="/recruitment"
    />

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <div v-if="loading" class="detail-card">Chargement de la fiche candidat...</div>

    <div v-else-if="candidate" class="detail-grid">
      <AppCard class="summary-card">
        <div class="summary-top">
          <div>
            <p class="eyebrow">Candidat</p>
            <h2>{{ candidateName }}</h2>
            <p class="text-muted">{{ candidate.email || 'Email non renseigne' }}</p>
          </div>
          <span :class="['badge', statusBadgeClass(candidate.status)]">{{ candidate.status || 'EN_EVALUATION' }}</span>
        </div>
        <div class="summary-metrics">
          <div>
            <span>Experience</span>
            <strong>{{ valueOrDash(candidate.experience_years) }} an(s)</strong>
          </div>
          <div>
            <span>Matching</span>
            <strong>{{ scoreLabel(candidate.matching_score) }}</strong>
          </div>
          <div>
            <span>Decision</span>
            <strong>{{ candidate.final_decision || 'En attente' }}</strong>
          </div>
        </div>
      </AppCard>

      <AppCard>
        <h3>Informations personnelles</h3>
        <div class="info-grid">
          <InfoItem label="Prenom" :value="candidate.first_name" />
          <InfoItem label="Nom" :value="candidate.last_name" />
          <InfoItem label="Email" :value="candidate.email" />
          <InfoItem label="Telephone" :value="candidate.phone" />
          <InfoItem label="Diplome" :value="candidate.degree" />
          <InfoItem label="Date de creation" :value="formatDate(candidate.created_at)" />
        </div>
      </AppCard>

      <AppCard>
        <h3>Offre, competences et CV</h3>
        <div class="info-grid">
          <InfoItem label="Offre liee" :value="jobTitle" />
          <InfoItem label="Score matching" :value="scoreLabel(candidate.matching_score)" />
          <InfoItem label="CV" :value="candidate.cv_filename || 'Aucun CV attache'" />
          <InfoItem label="Validation" :value="validationLabel" />
        </div>
        <div class="skills-list">
          <span v-for="skill in candidate.skills || []" :key="skill" class="badge badge-neutral">{{ skill }}</span>
          <span v-if="!(candidate.skills || []).length" class="text-muted">Aucune competence renseignee.</span>
        </div>
      </AppCard>

      <AppCard>
        <h3>Evaluations</h3>
        <div v-if="(candidate.evaluations || []).length" class="timeline">
          <div v-for="evaluation in candidate.evaluations" :key="evaluation.id_evaluation" class="timeline-item">
            <strong>{{ scoreLabel(evaluation.score) }}</strong>
            <span>{{ formatDate(evaluation.created_at) }}</span>
            <p>{{ evaluation.comments || 'Aucun commentaire.' }}</p>
            <p class="text-muted">Forces: {{ evaluation.strengths || '-' }} | Points a ameliorer: {{ evaluation.weaknesses || '-' }}</p>
          </div>
        </div>
        <p v-else class="text-muted">Aucune evaluation enregistree.</p>
      </AppCard>

      <AppCard>
        <h3>Entretiens</h3>
        <div v-if="(candidate.interviews || []).length" class="timeline">
          <div v-for="interview in candidate.interviews" :key="interview.id_interview" class="timeline-item">
            <strong>{{ formatDate(interview.scheduled_at) }}</strong>
            <span>{{ interview.status || 'PLANIFIE' }}</span>
            <p>{{ interview.feedback || 'Aucun retour saisi.' }}</p>
            <p class="text-muted">Score: {{ scoreLabel(interview.score) }}</p>
          </div>
        </div>
        <p v-else class="text-muted">Aucun entretien planifie.</p>
      </AppCard>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import recruitmentService from '../../services/recruitmentService'
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
      h('strong', props.value || '-')
    ])
  }
})

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const pageError = ref('')
const candidate = ref(null)
const jobOffers = ref([])

const candidateName = computed(() => {
  if (!candidate.value) return 'Fiche candidat'
  return `${candidate.value.first_name || ''} ${candidate.value.last_name || ''}`.trim() || 'Fiche candidat'
})

const jobTitle = computed(() => {
  const jobId = candidate.value?.job_offer_id
  if (!jobId) return 'Candidature spontanee'
  const job = jobOffers.value.find(item => Number(item.id_job) === Number(jobId))
  return job ? `${job.title} (${job.department})` : `Offre #${jobId}`
})

const validationLabel = computed(() => {
  if (!candidate.value?.validated_at) return 'Non validee'
  return `${candidate.value.final_decision || 'Decision'} le ${formatDate(candidate.value.validated_at)}`
})

function valueOrDash(value) {
  return value === null || value === undefined || value === '' ? '-' : value
}

function scoreLabel(value) {
  return value === null || value === undefined || value === '' ? 'Non calcule' : `${Number(value).toFixed(1)}%`
}

function statusBadgeClass(status) {
  if (status === 'RETENU') return 'badge-success'
  if (status === 'REFUSE') return 'badge-neutral'
  if (status === 'ENTRETIEN') return 'badge-warning'
  return 'badge-info'
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium', timeStyle: value.includes('T') ? 'short' : undefined }).format(new Date(value))
}

async function loadCandidate() {
  loading.value = true
  pageError.value = ''
  try {
    const [candidateRes, jobsRes] = await Promise.all([
      recruitmentService.getCandidate(route.params.id),
      recruitmentService.getJobOffers()
    ])
    candidate.value = candidateRes.data
    jobOffers.value = jobsRes.data || []
  } catch (error) {
    pageError.value = error.response?.data?.detail || 'Impossible de charger la fiche candidat.'
  } finally {
    loading.value = false
  }
}

onMounted(loadCandidate)
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

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.timeline {
  display: grid;
  gap: var(--space-3);
}

.timeline-item {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
}

.timeline-item span {
  color: var(--color-text-muted);
  display: block;
  font-size: var(--font-size-xs);
  margin-top: var(--space-1);
}

.timeline-item p {
  margin: var(--space-2) 0 0;
}

.rotate-left {
  transform: rotate(90deg);
}
</style>
