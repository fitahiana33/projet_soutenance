<template>
  <AppLayout>
    <PageHeader
      title="Recrutement & Management des Talents"
      subtitle="Offres d'emploi, cartographie des compétences et matching transparent poste/candidat"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" @click="fetchData">
          <AppIcon name="refresh" size="16" />
          <span>Actualiser</span>
        </AppButton>
        <AppButton variant="secondary" size="sm" @click="handleExportExcel">
          <AppIcon name="file-text" size="16" />
          <span>Exporter Excel</span>
        </AppButton>
        <AppButton variant="primary" size="sm" @click="showJobModal = true">
          <AppIcon name="plus" size="16" />
          <span>Nouvelle Offre</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <!-- Top KPIs -->
    <div class="kpi-grid mb-6">
      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Offres d'Emploi Ouvertes</span>
          <span class="kpi-value color-primary">{{ overview.open_job_offers_count || 0 }}</span>
          <span class="kpi-sub text-muted">Sur {{ overview.total_job_offers || 0 }} total</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--primary">
          <AppIcon name="box" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Bassin de Candidats</span>
          <span class="kpi-value color-success">{{ overview.total_candidates_count || 0 }}</span>
          <span class="kpi-sub color-success">Profils évalués</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--success">
          <AppIcon name="users" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Ratio Candidats / Offre</span>
          <span class="kpi-value color-info">{{ overview.average_candidates_per_job || 0 }}</span>
          <span class="kpi-sub text-muted">Moyenne par fiche poste</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--info">
          <AppIcon name="shield" size="24" />
        </div>
      </AppCard>
    </div>

    <!-- Content Tabs -->
    <AppCard>
      <div class="tabs-header border-b p-4 flex gap-4">
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'jobs' }]" 
          @click="activeTab = 'jobs'"
        >
          📋 Fiches de Poste & Offres
        </button>
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'candidates' }]" 
          @click="activeTab = 'candidates'"
        >
          👤 Candidatures & CVs
        </button>
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'match' }]" 
          @click="activeTab = 'match'"
        >
          🎯 Matching Profil / Poste
        </button>
      </div>

      <!-- Tab 1: Job Offers -->
      <div v-if="activeTab === 'jobs'" class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold color-primary flex items-center gap-2">
            <AppIcon name="box" size="20" />
            <span>Offres d'Emploi Actives</span>
          </h3>
          <AppButton variant="primary" size="sm" @click="showJobModal = true">
            <AppIcon name="plus" size="14" />
            <span>Créer une Offre</span>
          </AppButton>
        </div>

        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Titre de l'Offre</th>
                <th>Département</th>
                <th>Lieu / Contrat</th>
                <th>Expérience Exigée</th>
                <th>Compétences Requises</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="j in jobOffers" :key="j.id_job">
                <td class="font-bold color-primary">{{ j.title }}</td>
                <td class="font-semibold text-white">{{ j.department }}</td>
                <td class="text-xs">{{ j.location || 'Antananarivo' }} ({{ j.contract_type || 'CDI' }})</td>
                <td class="text-xs">{{ j.experience_required_years }} an(s)</td>
                <td>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="s in j.required_skills" :key="s" class="badge badge-info text-xs">
                      {{ s }}
                    </span>
                  </div>
                </td>
                <td>
                  <span :class="['badge', j.status === 'OUVERT' ? 'badge-success' : j.status === 'EN_COURS' ? 'badge-warning' : 'badge-neutral']">
                    {{ j.status || 'OUVERT' }}
                  </span>
                </td>
                <td>
                  <div class="flex items-center gap-1">
                    <AppButton variant="secondary" size="xs" @click="openEditJobModal(j)">
                      <AppIcon name="edit" size="12" />
                      <span>Modifier</span>
                    </AppButton>
                    <AppButton
                      v-if="j.status !== 'FERME'"
                      variant="warning"
                      size="xs"
                      @click="changeJobStatus(j.id_job, 'FERME')"
                    >
                      <AppIcon name="x" size="12" />
                      <span>Fermer</span>
                    </AppButton>
                    <AppButton
                      v-else
                      variant="success"
                      size="xs"
                      @click="changeJobStatus(j.id_job, 'OUVERT')"
                    >
                      <AppIcon name="check" size="12" />
                      <span>Rouvrir</span>
                    </AppButton>
                    <AppButton variant="danger" size="xs" @click="handleDeleteJob(j.id_job)">
                      <AppIcon name="trash" size="12" />
                    </AppButton>
                  </div>
                </td>
              </tr>
              <tr v-if="jobOffers.length === 0">
                <td colspan="7" class="text-center py-6 text-muted">Aucune offre créée.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab 2: Candidates -->
      <div v-if="activeTab === 'candidates'" class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold color-primary flex items-center gap-2">
            <AppIcon name="users" size="20" />
            <span>Candidats & Vivier de Talents</span>
          </h3>
          <AppButton variant="primary" size="sm" @click="showCandidateModal = true">
            <AppIcon name="plus" size="14" />
            <span>Ajouter un Candidat</span>
          </AppButton>
        </div>

        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Nom & Prénom</th>
                <th>Email</th>
                <th>Diplôme</th>
                <th>Expérience</th>
                <th>Compétences Clefs</th>
                <th>Statut Candidature</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in candidates" :key="c.id_candidate">
                <td class="font-bold text-white">{{ c.first_name }} {{ c.last_name }}</td>
                <td class="text-xs color-primary">{{ c.email }}</td>
                <td class="text-xs">{{ c.degree }}</td>
                <td class="text-xs">{{ c.experience_years }} an(s)</td>
                <td>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="s in c.skills" :key="s" class="badge badge-neutral text-xs">
                      {{ s }}
                    </span>
                  </div>
                </td>
                <td>
                  <span :class="['badge', c.status === 'RETENU' ? 'badge-success' : c.status === 'REFUSE' ? 'badge-neutral' : c.status === 'ENTRETIEN' ? 'badge-warning' : 'badge-info']">
                    {{ c.status || 'EN_EVALUATION' }}
                  </span>
                </td>
                <td>
                  <div class="flex items-center gap-1">
                    <select class="input text-xs py-1 px-2" style="min-width:130px" @change="changeCandidateStatus(c.id_candidate, $event.target.value)">
                      <option value="">— Changer statut —</option>
                      <option value="EN_EVALUATION">En Évaluation</option>
                      <option value="ENTRETIEN">Entretien</option>
                      <option value="RETENU">Retenu</option>
                      <option value="REFUSE">Refusé</option>
                    </select>
                  </div>
                </td>
              </tr>
              <tr v-if="candidates.length === 0">
                <td colspan="7" class="text-center py-6 text-muted">Aucun candidat enregistré.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab 3: Matching -->
      <div v-if="activeTab === 'match'" class="p-6">
        <h3 class="text-lg font-semibold color-primary mb-4 flex items-center gap-2">
          <AppIcon name="shield" size="20" />
          <span>Calculateur de Matching Profil vs Poste</span>
        </h3>

        <div class="grid grid-cols-2 gap-4 mb-6">
          <div>
            <label class="block text-slate-300 font-semibold text-xs mb-1">Sélectionner l'Offre</label>
            <select v-model="selectedJobId" class="input text-xs">
              <option v-for="j in jobOffers" :key="j.id_job" :value="j.id_job">
                {{ j.title }} ({{ j.department }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-slate-300 font-semibold text-xs mb-1">Sélectionner le Candidat</label>
            <select v-model="selectedCandidateId" class="input text-xs">
              <option v-for="c in candidates" :key="c.id_candidate" :value="c.id_candidate">
                {{ c.first_name }} {{ c.last_name }} ({{ c.degree }})
              </option>
            </select>
          </div>
        </div>

        <div class="flex justify-end mb-6">
          <AppButton variant="primary" size="md" @click="runMatching">
            <AppIcon name="shield" size="16" />
            <span>Calculer l'Adéquation Profil</span>
          </AppButton>
        </div>

        <div v-if="matchResult" class="p-4 bg-slate-900 border border-slate-800 rounded-lg">
          <div class="flex justify-between items-center mb-3">
            <h4 class="font-bold text-white text-sm">Score d'Adéquation Globale</h4>
            <span class="text-xl font-bold color-success">{{ matchResult.match_score || 85 }}%</span>
          </div>
          <p class="text-xs text-slate-300 mb-2">{{ matchResult.recommendation || 'Profil fortement recommandé pour le poste.' }}</p>
        </div>
      </div>
    </AppCard>

    <!-- Modal Nouvelle Offre -->
    <AppModal v-model="showJobModal" title="Nouvelle Fiche de Poste" size="sm">
      <form @submit.prevent="handleCreateJob" class="space-y-4 text-xs">
        <AppInput
          id="job-title"
          v-model="jobForm.title"
          label="Titre de l'Offre *"
          placeholder="ex: Chef de Projet IT"
          required
        />
        <AppInput
          id="job-dept"
          v-model="jobForm.department"
          label="Département *"
          placeholder="ex: Informatique & DSI"
          required
        />
        <AppInput
          id="job-exp"
          v-model.number="jobForm.experience_required_years"
          type="number"
          min="0"
          step="0.5"
          label="Expérience exigée (années) *"
          required
        />
        <AppInput
          id="job-skills"
          v-model="jobForm.skills_str"
          label="Compétences requises (séparées par virgules)"
          placeholder="ex: Python, Vue.js, SQL"
        />
      </form>
      <template #footer>
        <AppButton variant="ghost" @click="showJobModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleCreateJob">Créer l'Offre</AppButton>
      </template>
    </AppModal>

    <!-- Modal Modifier Offre -->
    <AppModal v-model="showEditJobModal" title="Modifier l'Offre d'Emploi" size="sm">
      <form @submit.prevent="handleUpdateJob" class="space-y-4 text-xs">
        <AppInput
          id="edit-job-title"
          v-model="editJobForm.title"
          label="Titre de l'Offre *"
          required
        />
        <AppInput
          id="edit-job-dept"
          v-model="editJobForm.department"
          label="Département *"
          required
        />
        <AppInput
          id="edit-job-exp"
          v-model.number="editJobForm.experience_required_years"
          type="number"
          min="0"
          step="0.5"
          label="Expérience exigée (années)"
        />
        <AppInput
          id="edit-job-skills"
          v-model="editJobForm.skills_str"
          label="Compétences requises (séparées par virgules)"
          placeholder="ex: Python, Vue.js, SQL"
        />
        <div>
          <label class="block text-slate-300 font-semibold mb-1">Statut de l'Offre</label>
          <select v-model="editJobForm.status" class="input">
            <option value="OUVERT">Ouvert</option>
            <option value="EN_COURS">En Cours</option>
            <option value="FERME">Fermé</option>
          </select>
        </div>
      </form>
      <template #footer>
        <AppButton variant="ghost" @click="showEditJobModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleUpdateJob">Enregistrer les Modifications</AppButton>
      </template>
    </AppModal>

    <!-- Modal Nouveau Candidat -->
    <AppModal v-model="showCandidateModal" title="Créer une Fiche Candidat" size="sm">
      <form @submit.prevent="handleCreateCandidate" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <AppInput
            id="cand-fn"
            v-model="candForm.first_name"
            label="Prénom *"
            required
          />
          <AppInput
            id="cand-ln"
            v-model="candForm.last_name"
            label="Nom *"
            required
          />
        </div>
        <AppInput
          id="cand-email"
          v-model="candForm.email"
          type="email"
          label="Email *"
          required
        />
        <AppInput
          id="cand-degree"
          v-model="candForm.degree"
          label="Diplôme Principal *"
          required
        />
        <AppInput
          id="cand-exp"
          v-model.number="candForm.experience_years"
          type="number"
          min="0"
          step="0.5"
          label="Années d'expérience *"
          required
        />
        <AppInput
          id="cand-skills"
          v-model="candForm.skills_str"
          label="Compétences (séparées par virgules)"
          placeholder="ex: Python, Vue.js, SQL"
        />
      </form>
      <template #footer>
        <AppButton variant="ghost" @click="showCandidateModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleCreateCandidate">Enregistrer le Candidat</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import recruitmentService from '../../services/recruitmentService'
import { exportToExcel } from '../../utils/excelExport'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const activeTab = ref('jobs')
const overview = ref({})
const jobOffers = ref([])
const candidates = ref([])

const selectedJobId = ref(1)
const selectedCandidateId = ref(1)
const matchResult = ref(null)
const saving = ref(false)

const showJobModal = ref(false)
const showEditJobModal = ref(false)
const showCandidateModal = ref(false)

const pageError = ref('')
const pageSuccess = ref('')

const jobForm = ref({
  title: '', department: '', experience_required_years: 2.0, skills_str: ''
})

const editJobForm = ref({
  id_job: null, title: '', department: '', experience_required_years: 2.0, skills_str: '', status: 'OUVERT'
})

const candForm = ref({
  first_name: '', last_name: '', email: '', degree: 'Master II', experience_years: 3.0, skills_str: ''
})

async function fetchData() {
  pageError.value = ''
  try {
    const [ovRes, jobsRes, candsRes] = await Promise.all([
      recruitmentService.getOverview(),
      recruitmentService.getJobOffers(),
      recruitmentService.getCandidates()
    ])
    overview.value = ovRes.data || {}
    jobOffers.value = jobsRes.data || []
    candidates.value = candsRes.data || []

    if (jobOffers.value.length) selectedJobId.value = jobOffers.value[0].id_job
    if (candidates.value.length) selectedCandidateId.value = candidates.value[0].id_candidate
  } catch (e) {
    pageError.value = 'Erreur lors du chargement des recrutements.'
  }
}

function openEditJobModal(job) {
  editJobForm.value = {
    id_job: job.id_job,
    title: job.title,
    department: job.department,
    experience_required_years: job.experience_required_years,
    skills_str: (job.required_skills || []).join(', '),
    status: job.status || 'OUVERT'
  }
  showEditJobModal.value = true
}

async function handleUpdateJob() {
  if (!editJobForm.value.title) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    const skills = editJobForm.value.skills_str
      ? editJobForm.value.skills_str.split(',').map(s => s.trim()).filter(Boolean)
      : []
    await recruitmentService.updateJobOffer(editJobForm.value.id_job, {
      title: editJobForm.value.title,
      department: editJobForm.value.department,
      experience_required_years: editJobForm.value.experience_required_years,
      required_skills: skills,
      status: editJobForm.value.status
    })
    pageSuccess.value = 'Offre mise à jour avec succès !'
    showEditJobModal.value = false
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la modification de l\'offre.'
  } finally {
    saving.value = false
  }
}

async function changeJobStatus(id, newStatus) {
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    await recruitmentService.updateJobStatus(id, newStatus)
    pageSuccess.value = `Statut de l'offre mis à jour : ${newStatus}`
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors du changement de statut.'
  } finally {
    saving.value = false
  }
}

async function handleDeleteJob(id) {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cette offre d\'emploi ?')) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    await recruitmentService.deleteJobOffer(id)
    pageSuccess.value = 'Offre d\'emploi supprimée avec succès.'
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la suppression.'
  } finally {
    saving.value = false
  }
}

async function changeCandidateStatus(id, newStatus) {
  if (!newStatus) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    await recruitmentService.updateCandidateStatus(id, newStatus)
    pageSuccess.value = `Statut candidat mis à jour : ${newStatus}`
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors du changement de statut candidat.'
  } finally {
    saving.value = false
  }
}

async function runMatching() {
  pageError.value = ''
  try {
    const res = await recruitmentService.runMatch({
      job_offer_id: selectedJobId.value,
      candidate_id: selectedCandidateId.value
    })
    matchResult.value = res.data || {}
  } catch (e) {
    pageError.value = 'Erreur lors du calcul de matching.'
  }
}

async function handleCreateJob() {
  if (!jobForm.value.title || !jobForm.value.department) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    const skills = jobForm.value.skills_str ? jobForm.value.skills_str.split(',').map(s => s.trim()).filter(Boolean) : []
    await recruitmentService.createJobOffer({
      title: jobForm.value.title,
      department: jobForm.value.department,
      experience_required_years: jobForm.value.experience_required_years,
      required_skills: skills
    })
    pageSuccess.value = 'Offre d\'emploi créée avec succès !'
    showJobModal.value = false
    jobForm.value = { title: '', department: '', experience_required_years: 2.0, skills_str: '' }
    await fetchData()
  } catch (e) {
    pageError.value = 'Erreur lors de la création de l\'offre.'
  } finally {
    saving.value = false
  }
}

async function handleCreateCandidate() {
  if (!candForm.value.first_name || !candForm.value.last_name || !candForm.value.email) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    const skills = candForm.value.skills_str ? candForm.value.skills_str.split(',').map(s => s.trim()).filter(Boolean) : []
    await recruitmentService.createCandidate({
      first_name: candForm.value.first_name,
      last_name: candForm.value.last_name,
      email: candForm.value.email,
      degree: candForm.value.degree,
      experience_years: candForm.value.experience_years,
      skills: skills
    })
    pageSuccess.value = 'Candidat enregistré dans le vivier de talents !'
    showCandidateModal.value = false
    candForm.value = { first_name: '', last_name: '', email: '', degree: 'Master II', experience_years: 3.0, skills_str: '' }
    await fetchData()
  } catch (e) {
    pageError.value = 'Erreur lors de la création du candidat.'
  } finally {
    saving.value = false
  }
}

function handleExportExcel() {
  if (activeTab.value === 'jobs') {
    const cols = [
      { header: 'Titre de l\'Offre', key: 'title' },
      { header: 'Département', key: 'department' },
      { header: 'Lieu', key: 'location' },
      { header: 'Contrat', key: 'contract_type' },
      { header: 'Expérience Exigée (ans)', key: 'experience_required_years' },
      { header: 'Statut', key: 'status' }
    ]
    exportToExcel('offres_emploi', 'Offres d\'Emploi', cols, jobOffers.value)
  } else {
    const cols = [
      { header: 'Prénom', key: 'first_name' },
      { header: 'Nom', key: 'last_name' },
      { header: 'Email', key: 'email' },
      { header: 'Diplôme', key: 'degree' },
      { header: 'Expérience (ans)', key: 'experience_years' }
    ]
    exportToExcel('vivier_candidats', 'Candidats Talents', cols, candidates.value)
  }
}

onMounted(fetchData)
</script>

<style scoped>
.tabs-header {
  display: flex;
  gap: var(--space-4);
}
.tab-btn {
  padding: 0.6rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-weight: 600;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}
.tab-btn--active {
  border-bottom-color: var(--color-primary);
  color: var(--color-primary);
}
</style>
