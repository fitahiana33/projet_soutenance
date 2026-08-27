<template>
  <AppLayout>
    <PageHeader
      title="Réglages Système & Paramètres Métiers"
      subtitle="Gestion intégrale des règles de calcul (Paie Madagascar, TVA, Stocks) et configurations de l'entreprise"
      showBack
      backFallback="/dashboard"
    >
      <template #actions>
        <AppButton variant="primary" size="sm" @click="openCreateParamModal">
          <AppIcon name="plus" size="16" />
          <span>Nouveau Paramètre</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <!-- Navigation Tabs -->
    <AppCard class="mb-6">
      <div class="tabs-header border-b p-4 flex gap-4">
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'parameters' }]" 
          @click="activeTab = 'parameters'"
        >
          ⚙️ Paramètres Métiers System Configuration
        </button>
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'reset' }]" 
          @click="activeTab = 'reset'"
        >
          🛡️ Purge & Réinitialisation
        </button>
      </div>

      <!-- Tab 1: Configurable Calculation Parameters -->
      <div v-if="activeTab === 'parameters'" class="p-6">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h3 class="text-lg font-bold color-primary flex items-center gap-2">
              <AppIcon name="settings" size="20" />
              <span>Paramètres Métiers & Règles de Calcul</span>
            </h3>
            <p class="text-xs text-muted">Toutes les règles métiers (CNaPS, OSTIE, IRSA, Heures Sup, TVA) sont configurées ici.</p>
          </div>
          <div class="flex gap-2">
            <AppButton variant="secondary" size="sm" @click="fetchRawParameters">
              <AppIcon name="refresh" size="14" /> Actualiser
            </AppButton>
            <AppButton variant="primary" size="sm" @click="openCreateParamModal">
              <AppIcon name="plus" size="14" /> Ajouter un Paramètre
            </AppButton>
          </div>
        </div>

        <!-- Categorized Parameters Grid -->
        <div class="space-y-6">
          <!-- Category Filter Tabs -->
          <div class="flex gap-2 mb-4">
            <button 
              v-for="cat in categories" 
              :key="cat.id" 
              :class="['filter-badge', { 'filter-badge--active': selectedCategory === cat.id }]"
              @click="selectedCategory = cat.id"
            >
              {{ cat.label }} ({{ countByCategory(cat.id) }})
            </button>
          </div>

          <!-- Parameters Table -->
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Catégorie</th>
                  <th>Clé Unique</th>
                  <th>Libellé / Intitulé</th>
                  <th>Valeur du Paramètre</th>
                  <th>Description</th>
                  <th style="text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="param in filteredParams" :key="param.id_param">
                  <td>
                    <span :class="['badge', getCategoryBadgeClass(param.category)]">
                      {{ param.category }}
                    </span>
                  </td>
                  <td class="font-mono text-xs strong color-primary">{{ param.key }}</td>
                  <td class="font-semibold text-xs text-white">{{ param.label }}</td>
                  <td>
                    <input 
                      v-model="param.value" 
                      type="text" 
                      class="input text-xs font-mono py-1 px-2 w-32 border-amber-500/50" 
                      @change="quickUpdateParam(param)"
                    />
                  </td>
                  <td class="text-xs text-slate-300 max-w-xs truncate">{{ param.description || '-' }}</td>
                  <td>
                    <div class="flex justify-end gap-2">
                      <button class="btn btn-secondary btn-xs" title="Éditer" @click="openEditParamModal(param)">
                        <AppIcon name="edit" size="16" /> Éditer
                      </button>
                      <button class="btn btn-danger btn-xs" title="Supprimer" @click="confirmDeleteParam(param)">
                        <AppIcon name="trash" size="16" /> Supprimer
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="filteredParams.length === 0">
                  <td colspan="6" class="text-center py-6 text-muted">Aucun paramètre système trouvé pour cette catégorie.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab 2: Reset scope -->
      <div v-if="activeTab === 'reset'" class="p-6 space-y-6">
        <h3 class="text-lg font-bold flex items-center gap-2 color-primary">
          <AppIcon name="shield" size="22" />
          <span>Périmètre de Réinitialisation Métier</span>
        </h3>

        <div class="reset-scope-grid">
          <div class="scope-box scope-box--danger">
            <h4 class="font-bold color-danger mb-3 flex items-center gap-2">
              <AppIcon name="trash" size="18" />
              <span>Données Réinitialisées & Purgées</span>
            </h4>
            <ul class="scope-list">
              <li><strong>Catalogue Produits & Catégories</strong></li>
              <li><strong>Répertoire Tiers & Fournisseurs</strong></li>
              <li><strong>Workflow Achats</strong> (Demandes, Commandes, Réceptions, Factures)</li>
              <li><strong>Ressources Humaines</strong> (Employés, Congés, Paie, Évaluations)</li>
              <li><strong>Stocks & Traçabilité</strong> (Mouvements & Lots)</li>
              <li><strong>Comptes utilisateurs secondaires</strong></li>
            </ul>
          </div>

          <div class="scope-box scope-box--success">
            <h4 class="font-bold color-success mb-3 flex items-center gap-2">
              <AppIcon name="shield" size="18" />
              <span>Données Conservées & Sécurisées</span>
            </h4>
            <ul class="scope-list">
              <li><strong>Compte Administrateur principal</strong> (<code>admin@erp.com</code>)</li>
              <li><strong>Rôles système par défaut</strong> (8 rôles système)</li>
              <li><strong>Permissions & Matrice de sécurité</strong> (Contrôle d'accès RBAC)</li>
              <li><strong>Paramètres Métiers & Jours Fériés de Référence</strong></li>
            </ul>
          </div>
        </div>

        <!-- Danger Zone Block -->
        <div class="danger-zone-card p-4 rounded-lg flex justify-between items-center">
          <div>
            <h4 class="font-bold color-danger mb-1 flex items-center gap-2">
              <AppIcon name="alert-circle" size="20" />
              <span>Zone de Purge des Données Métiers</span>
            </h4>
            <p class="text-xs text-muted">
              Cette action effacera définitivement l'ensemble des données d'essai métier.
            </p>
          </div>
          <AppButton variant="danger" size="md" @click="showResetModal = true">
            <AppIcon name="trash" size="18" />
            <span>Réinitialiser les données métier</span>
          </AppButton>
        </div>
      </div>
    </AppCard>

    <!-- Modal Create / Edit System Parameter -->
    <AppModal
      v-model="showParamModal"
      :title="editingParam ? 'Éditer le paramètre système' : 'Nouveau paramètre système'"
      size="sm"
    >
      <form @submit.prevent="saveParam" class="space-y-4 text-xs">
        <AppAlert v-if="modalError" variant="danger" dismissible @dismiss="modalError = ''">
          {{ modalError }}
        </AppAlert>

        <div>
          <label class="block text-slate-300 font-semibold mb-1">Catégorie *</label>
          <select v-model="paramForm.category" class="input" required>
            <option value="RH_PAIE">RH & Paie Madagascar</option>
            <option value="HEURES_SUP">Heures Supplémentaires & Nuit</option>
            <option value="COMMERCIAL_LOGISTIQUE">Commercial & Logistique</option>
            <option value="GENERAL">Général & Système</option>
          </select>
        </div>

        <AppInput
          id="param-key"
          v-model="paramForm.key"
          label="Clé du paramètre (ex: cnaps_ceiling_amount) *"
          placeholder="ex: cnaps_ceiling_amount"
          :disabled="!!editingParam"
          required
        />

        <AppInput
          id="param-label"
          v-model="paramForm.label"
          label="Libellé / Intitulé *"
          placeholder="ex: Plafond Mensuel CNaPS (Ar)"
          required
        />

        <AppInput
          id="param-val"
          v-model="paramForm.value"
          label="Valeur du paramètre *"
          placeholder="ex: 568000.0"
          required
        />

        <div>
          <label class="block text-slate-300 font-semibold mb-1">Description</label>
          <textarea v-model="paramForm.description" class="input" rows="2" placeholder="Description de l'usage de ce paramètre..."></textarea>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showParamModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="savingParam" @click="saveParam">
          {{ editingParam ? 'Mettre à jour' : 'Enregistrer le Paramètre' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Modal Delete Parameter -->
    <AppModal v-model="showDeleteParamModal" title="Confirmer la suppression" size="sm">
      <p class="text-sm">Êtes-vous sûr de vouloir supprimer le paramètre <strong>{{ deletingParam?.label }}</strong> (<code>{{ deletingParam?.key }}</code>) ?</p>
      <template #footer>
        <AppButton variant="ghost" @click="showDeleteParamModal = false">Annuler</AppButton>
        <AppButton variant="danger" :loading="deletingParam" @click="executeDeleteParam">Supprimer</AppButton>
      </template>
    </AppModal>

    <!-- Modal Confirmation Reset -->
    <AppModal v-model="showResetModal" title="Confirmer la réinitialisation" size="sm">
      <div class="p-4">
        <AppAlert variant="danger" class="mb-4">
          <strong>Attention !</strong> Toutes les données opérationnelles métiers (Ventes, Achats, Stocks, RH, Recrutement, Offres & Candidats) seront intégralement réinitialisées. <strong>Seuls votre compte Administrateur (admin), les rôles et les permissions système seront conservés.</strong>
        </AppAlert>

        <p class="text-sm mb-3 font-semibold">
          Saisissez <code class="sku-badge color-danger">RESET</code> pour confirmer la purge :
        </p>

        <AppInput
          id="confirm-input"
          v-model="confirmText"
          placeholder="Tapez RESET pour valider"
          class="mb-2"
        />
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="cancelReset">Annuler</AppButton>
        <AppButton
          variant="danger"
          :disabled="confirmText.trim().toUpperCase() !== 'RESET'"
          :loading="resetting"
          @click="executeReset"
        >
          Valider la Réinitialisation
        </AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import systemService from '../../services/systemService'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const activeTab = ref('parameters')
const selectedCategory = ref('ALL')

const rawParams = ref([])
const showParamModal = ref(false)
const showDeleteParamModal = ref(false)
const editingParam = ref(null)
const deletingParam = ref(null)

const showResetModal = ref(false)
const confirmText = ref('')
const resetting = ref(false)
const savingParam = ref(false)
const deletingParamStatus = ref(false)

const pageError = ref('')
const pageSuccess = ref('')
const modalError = ref('')

const paramForm = ref({
  category: 'RH_PAIE',
  key: '',
  label: '',
  value: '',
  description: ''
})

const categories = [
  { id: 'ALL', label: 'Tous les Paramètres' },
  { id: 'RH_PAIE', label: 'RH & Paie Madagascar' },
  { id: 'HEURES_SUP', label: 'Heures Sup & Nuit' },
  { id: 'COMMERCIAL_LOGISTIQUE', label: 'Commercial & Logistique' },
  { id: 'GENERAL', label: 'Général & Système' }
]

const filteredParams = computed(() => {
  if (selectedCategory.value === 'ALL') return rawParams.value
  return rawParams.value.filter(p => p.category === selectedCategory.value)
})

function countByCategory(catId) {
  if (catId === 'ALL') return rawParams.value.length
  return rawParams.value.filter(p => p.category === catId).length
}

function getCategoryBadgeClass(cat) {
  if (cat === 'RH_PAIE') return 'badge-warning'
  if (cat === 'HEURES_SUP') return 'badge-info'
  if (cat === 'COMMERCIAL_LOGISTIQUE') return 'badge-success'
  return 'badge-neutral'
}

async function fetchRawParameters() {
  pageError.value = ''
  try {
    const res = await systemService.getParameters()
    rawParams.value = res.data || []
  } catch (e) {
    pageError.value = 'Erreur lors du chargement des paramètres système.'
  }
}

function openCreateParamModal() {
  editingParam.value = null
  modalError.value = ''
  paramForm.value = {
    category: 'RH_PAIE',
    key: '',
    label: '',
    value: '',
    description: ''
  }
  showParamModal.value = true
}

function openEditParamModal(param) {
  editingParam.value = param
  modalError.value = ''
  paramForm.value = {
    category: param.category,
    key: param.key,
    label: param.label,
    value: param.value,
    description: param.description || ''
  }
  showParamModal.value = true
}

async function quickUpdateParam(param) {
  try {
    await systemService.updateParameter(param.id_param, { value: String(param.value) })
    pageSuccess.value = `Paramètre '${param.label}' mis à jour avec succès.`
  } catch (e) {
    pageError.value = 'Erreur lors de la mise à jour rapide.'
  }
}

async function saveParam() {
  if (!paramForm.value.key || !paramForm.value.label || paramForm.value.value === '') {
    modalError.value = 'La clé, le libellé et la valeur sont requis.'
    return
  }

  savingParam.value = true
  modalError.value = ''
  pageSuccess.value = ''

  try {
    if (editingParam.value) {
      await systemService.updateParameter(editingParam.value.id_param, paramForm.value)
      pageSuccess.value = 'Paramètre mis à jour avec succès.'
    } else {
      await systemService.createParameter(paramForm.value)
      pageSuccess.value = 'Nouveau paramètre ajouté avec succès.'
    }
    showParamModal.value = false
    await fetchRawParameters()
  } catch (e) {
    modalError.value = e.response?.data?.detail || 'Erreur lors de l\'enregistrement du paramètre.'
  } finally {
    savingParam.value = false
  }
}

function confirmDeleteParam(param) {
  deletingParam.value = param
  showDeleteParamModal.value = true
}

async function executeDeleteParam() {
  if (!deletingParam.value) return
  deletingParamStatus.value = true
  try {
    await systemService.deleteParameter(deletingParam.value.id_param)
    pageSuccess.value = `Paramètre '${deletingParam.value.label}' supprimé avec succès.`
    showDeleteParamModal.value = false
    await fetchRawParameters()
  } catch (e) {
    pageError.value = 'Erreur lors de la suppression du paramètre.'
  } finally {
    deletingParamStatus.value = false
  }
}

function cancelReset() {
  showResetModal.value = false
  confirmText.value = ''
}

async function executeReset() {
  if (confirmText.value.trim().toUpperCase() !== 'RESET') return

  resetting.value = true
  pageError.value = ''
  pageSuccess.value = ''

  try {
    const res = await systemService.resetAllData(confirmText.value.trim())
    pageSuccess.value = res.data.message || 'Toutes les données métier ont été réinitialisées avec succès.'
    showResetModal.value = false
    confirmText.value = ''
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la réinitialisation.'
  } finally {
    resetting.value = false
  }
}

onMounted(fetchRawParameters)
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
}

.tab-btn--active {
  border-bottom-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-badge {
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-sm);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  font-size: 0.75rem;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-badge--active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
  font-weight: bold;
}

.reset-scope-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.scope-box {
  padding: var(--space-4);
  border-radius: var(--radius-sm);
}

.scope-box--danger {
  background: rgba(220, 38, 38, 0.04);
  border: 1px solid rgba(220, 38, 38, 0.2);
}

.scope-box--success {
  background: rgba(5, 150, 105, 0.04);
  border: 1px solid rgba(5, 150, 105, 0.2);
}

.scope-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.scope-list li {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.danger-zone-card {
  border: 1.5px solid var(--color-danger);
  background: rgba(220, 38, 38, 0.02);
}
</style>
