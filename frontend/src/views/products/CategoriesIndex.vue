<template>
  <AppLayout>
    <PageHeader
      title="Gestion des Catégories de Produits"
      subtitle="Gestion de la classification du catalogue et des sous-familles de produits"
    >
      <template #actions>
        <AppButton variant="primary" size="sm" @click="openCreateCategoryModal">
          <AppIcon name="plus" size="16" />
          <span>Nouvelle Catégorie</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <!-- Categories Data Table -->
    <AppTable
      :columns="columns"
      :items="categories"
      :loading="loading"
      empty-text="Aucune catégorie enregistrée pour le moment."
    >
      <!-- Name Column -->
      <template #col-name="{ item }">
        <div class="category-name-cell">
          <AppIcon name="folder" size="18" class="cat-icon" />
          <span class="cat-title">{{ item.name }}</span>
        </div>
      </template>

      <!-- Description Column -->
      <template #col-description="{ value }">
        <span class="text-muted">{{ value || 'Aucune description' }}</span>
      </template>

      <!-- Actions Column -->
      <template #actions="{ item }">
        <div class="actions-group">
          <button
            type="button"
            class="icon-btn"
            title="Éditer"
            @click="openEditCategoryModal(item)"
          >
            <AppIcon name="pencil" size="16" />
          </button>
          <button
            type="button"
            class="icon-btn icon-btn--danger"
            title="Supprimer"
            @click="confirmDeleteCategory(item)"
          >
            <AppIcon name="trash" size="16" />
          </button>
        </div>
      </template>
    </AppTable>

    <!-- Modal Create / Edit Category -->
    <AppModal
      v-model="showModal"
      :title="editingCategory ? 'Éditer la catégorie' : 'Nouvelle catégorie de produit'"
      size="sm"
    >
      <form @submit.prevent="saveCategory" class="modal-form">
        <AppAlert v-if="modalError" variant="danger" dismissible @dismiss="modalError = ''">
          {{ modalError }}
        </AppAlert>

        <AppInput
          id="cat-name-input"
          v-model="categoryForm.name"
          label="Nom de la catégorie *"
          placeholder="ex: Électronique & Composants"
          required
        />

        <AppInput
          id="cat-desc-input"
          v-model="categoryForm.description"
          label="Description"
          placeholder="Brève description de la catégorie..."
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveCategory">
          {{ editingCategory ? 'Mettre à jour' : 'Créer' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Modal Confirm Delete Category -->
    <AppModal v-model="showDeleteModal" title="Confirmer la suppression" size="sm">
      <p>Êtes-vous sûr de vouloir supprimer la catégorie <strong>{{ deletingCategory?.name }}</strong> ?</p>
      <template #footer>
        <AppButton variant="ghost" @click="showDeleteModal = false">Annuler</AppButton>
        <AppButton variant="danger" :loading="deleting" @click="executeDeleteCategory">Supprimer</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppTable from '../../components/ui/AppTable.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

const pageError = ref('')
const pageSuccess = ref('')
const modalError = ref('')

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingCategory = ref(null)
const deletingCategory = ref(null)

const categoryForm = ref({
  name: '',
  description: ''
})

const columns = [
  { key: 'name', label: 'Nom de la catégorie', width: '35%' },
  { key: 'description', label: 'Description', width: '50%' }
]

async function fetchCategories() {
  loading.value = true
  pageError.value = ''
  try {
    const res = await api.get('/products/categories')
    if (res.data && Array.isArray(res.data)) {
      categories.value = res.data
    }
  } catch (error) {
    pageError.value = 'Erreur lors de la récupération des catégories.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCategories()
})

function openCreateCategoryModal() {
  editingCategory.value = null
  modalError.value = ''
  categoryForm.value = { name: '', description: '' }
  showModal.value = true
}

function openEditCategoryModal(item) {
  editingCategory.value = item
  modalError.value = ''
  categoryForm.value = { name: item.name, description: item.description || '' }
  showModal.value = true
}

async function saveCategory() {
  if (!categoryForm.value.name) {
    modalError.value = 'Le nom de la catégorie est requis.'
    return
  }

  saving.value = true
  modalError.value = ''

  try {
    await api.post('/products/categories', categoryForm.value)
    pageSuccess.value = 'Catégorie enregistrée avec succès !'
    showModal.value = false
    await fetchCategories()
  } catch (error) {
    modalError.value = error?.response?.data?.detail || 'Erreur lors de l\'enregistrement.'
  } finally {
    saving.value = false
  }
}

function confirmDeleteCategory(item) {
  deletingCategory.value = item
  showDeleteModal.value = true
}

async function executeDeleteCategory() {
  if (!deletingCategory.value) return
  deleting.value = true
  try {
    categories.value = categories.value.filter(c => c.id_category !== deletingCategory.value.id_category)
    pageSuccess.value = 'Catégorie supprimée.'
    showDeleteModal.value = false
  } catch (error) {
    pageError.value = 'Erreur lors de la suppression.'
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.category-name-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.cat-icon {
  color: var(--color-primary);
}

.cat-title {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.actions-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-2);
}

.icon-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.35rem;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.icon-btn:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.icon-btn--danger:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.text-muted {
  color: var(--color-text-muted);
}
</style>
