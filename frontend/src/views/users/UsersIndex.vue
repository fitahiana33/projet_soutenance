<template>
  <AppLayout>
    <PageHeader
      title="Annuaire des Utilisateurs"
      subtitle="Administration des comptes utilisateurs, statuts de connexion et attribution des rôles"
      :breadcrumbs="[{ label: 'Accueil', path: '/dashboard' }, { label: 'Utilisateurs' }]"
      showBack
      backFallback="/dashboard"
    >
      <template #actions>
        <AppButton variant="primary" size="sm" @click="openCreateModal">
          <AppIcon name="plus" size="16" />
          <span>Nouvel Utilisateur</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <!-- Users Table with Integrated Search & Filter slot -->
    <AppTable
      title="Liste des comptes enregistrés"
      :columns="columns"
      :items="filteredUsers"
      :loading="loading"
      searchable
      v-model:searchValue="searchQuery"
      searchPlaceholder="Rechercher par nom, prénom ou email..."
      emptyTitle="Aucun utilisateur trouvé"
      emptyText="Aucun compte ne correspond aux critères de recherche ou de filtre sélectionnés."
    >
      <template #filters>
        <div class="filters-row">
          <div class="filter-group">
            <label class="filter-label">Rôle système :</label>
            <select v-model="selectedRole" class="filter-select">
              <option value="">Tous les rôles</option>
              <option v-for="r in availableRoles" :key="r.id_role" :value="r.id_role">
                {{ r.libelle }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label class="filter-label">Statut du compte :</label>
            <select v-model="selectedStatus" class="filter-select">
              <option value="">Tous les statuts</option>
              <option value="active">Actifs uniquement</option>
              <option value="inactive">Inactifs uniquement</option>
            </select>
          </div>

          <AppButton v-if="selectedRole || selectedStatus || searchQuery" variant="ghost" size="sm" @click="resetFilters">
            <span>Réinitialiser les filtres</span>
          </AppButton>
        </div>
      </template>

      <!-- Custom User Column -->
      <template #col-name="{ item }">
        <div class="user-cell">
          <div class="user-avatar">{{ getUserInitials(item) }}</div>
          <div class="user-details">
            <span class="user-fullname">{{ item.first_name }} {{ item.name }}</span>
            <span class="user-email">{{ item.email }}</span>
          </div>
        </div>
      </template>

      <!-- Custom Roles Column -->
      <template #col-roles="{ item }">
        <div class="roles-tags">
          <AppBadge
            v-for="r in (item.roles || [])"
            :key="r.id_role"
            :variant="r.libelle === 'ADMIN' ? 'danger' : 'primary'"
            :label="r.libelle"
          />
          <span v-if="!(item.roles && item.roles.length)" class="text-muted text-xs">
            Aucun rôle attribué
          </span>
        </div>
      </template>

      <!-- Custom Status Column -->
      <template #col-is_active="{ item, value }">
        <div class="status-cell">
          <AppBadge
            :variant="value ? 'success' : 'danger'"
            :label="value ? 'Actif' : 'Désactivé'"
          />
          <button
            type="button"
            class="toggle-status-btn"
            :title="value ? 'Désactiver le compte' : 'Réactiver le compte'"
            @click="toggleStatus(item)"
          >
            {{ value ? 'Désactiver' : 'Activer' }}
          </button>
        </div>
      </template>

      <!-- Table Actions Slot -->
      <template #actions="{ item }">
        <div class="actions-group">
          <button type="button" class="icon-btn" title="Modifier le compte" @click="openEditModal(item)">
            <AppIcon name="pencil" size="16" />
          </button>
          <button type="button" class="icon-btn icon-btn--danger" title="Supprimer définitivement" @click="confirmDelete(item)">
            <AppIcon name="trash" size="16" />
          </button>
        </div>
      </template>
    </AppTable>

    <!-- Modal Create / Edit User -->
    <AppModal
      v-model="showUserModal"
      :title="editingUser ? 'Modifier l\'utilisateur' : 'Créer un nouvel utilisateur'"
      size="md"
    >
      <form @submit.prevent="saveUser" class="modal-form">
        <AppAlert v-if="modalError" variant="danger" dismissible @dismiss="modalError = ''">
          {{ modalError }}
        </AppAlert>

        <div class="form-row">
          <AppInput
            id="user-firstname"
            v-model="form.first_name"
            label="Prénom"
            placeholder="Jean"
          />
          <AppInput
            id="user-lastname"
            v-model="form.name"
            label="Nom *"
            placeholder="Dupont"
            required
          />
        </div>

        <AppInput
          id="user-email"
          v-model="form.email"
          type="email"
          label="Adresse Email professionnelle *"
          placeholder="jean.dupont@smarterp.com"
          required
        />

        <AppInput
          id="user-password"
          v-model="form.password"
          type="password"
          :label="editingUser ? 'Nouveau mot de passe (laisser vide pour ne pas modifier)' : 'Mot de passe initial *'"
          placeholder="••••••••"
          :required="!editingUser"
        />

        <!-- User ↔ Roles Multi-Assignment -->
        <div class="form-group">
          <label class="form-label">Rôles système attribués</label>
          <div class="roles-checkboxes">
            <label
              v-for="r in availableRoles"
              :key="r.id_role"
              class="checkbox-label"
            >
              <input
                type="checkbox"
                :value="r.id_role"
                v-model="form.selectedRoleIds"
              />
              <span class="font-semibold">{{ r.libelle }}</span>
              <span class="role-desc">— {{ r.description || 'Rôle standard' }}</span>
            </label>
          </div>
        </div>

        <div class="form-checkbox">
          <label class="checkbox-label">
            <input v-model="form.is_active" type="checkbox" />
            <span>Compte actif et autorisé à se connecter</span>
          </label>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showUserModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveUser">
          {{ editingUser ? 'Enregistrer les modifications' : 'Créer l\'utilisateur' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Delete Confirmation Modal -->
    <AppModal v-model="showDeleteModal" title="Confirmer la suppression" size="sm">
      <AppAlert variant="warning" title="Attention : Action irréversible">
        Êtes-vous sûr de vouloir supprimer l'utilisateur <strong>{{ deletingUser?.first_name }} {{ deletingUser?.name }}</strong> ({{ deletingUser?.email }}) ?
      </AppAlert>
      <template #footer>
        <AppButton variant="ghost" @click="showDeleteModal = false">Annuler</AppButton>
        <AppButton variant="danger" :loading="deleting" @click="executeDelete">Supprimer le compte</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import userService from '../../services/userService'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppTable from '../../components/ui/AppTable.vue'
import AppBadge from '../../components/ui/AppBadge.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const searchQuery = ref('')
const selectedRole = ref('')
const selectedStatus = ref('')
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const pageError = ref('')
const modalError = ref('')

const showUserModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)

const users = ref([])
const availableRoles = ref([])

const form = ref({
  first_name: '',
  name: '',
  email: '',
  password: '',
  selectedRoleIds: [],
  is_active: true
})

const columns = [
  { key: 'name', label: 'Utilisateur', width: '30%', sortable: true },
  { key: 'roles', label: 'Rôles Attribués', width: '25%' },
  { key: 'is_active', label: 'Statut & Action', width: '25%', sortable: true },
  { key: 'created_at', label: 'Date de Création', width: '20%', sortable: true }
]

async function fetchData() {
  loading.value = true
  pageError.value = ''
  try {
    const [usersRes, rolesRes] = await Promise.all([
      userService.getUsers().catch(() => ({ data: [] })),
      userService.getRoles().catch(() => ({ data: [] }))
    ])
    if (usersRes.data && Array.isArray(usersRes.data)) {
      users.value = usersRes.data
    }
    if (rolesRes.data && Array.isArray(rolesRes.data)) {
      availableRoles.value = rolesRes.data
    }
  } catch (error) {
    pageError.value = 'Erreur lors du chargement des utilisateurs ou rôles.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

const filteredUsers = computed(() => {
  try {
    return users.value.filter((user) => {
      const nameMatch = user.name ? user.name.toLowerCase() : ''
      const firstNameMatch = user.first_name ? user.first_name.toLowerCase() : ''
      const emailMatch = user.email ? user.email.toLowerCase() : ''
      const q = searchQuery.value.toLowerCase()

      const matchesSearch = !q || nameMatch.includes(q) || firstNameMatch.includes(q) || emailMatch.includes(q)
      const matchesRole = !selectedRole.value || (user.roles || []).some(r => r.id_role === parseInt(selectedRole.value))
      const matchesStatus = !selectedStatus.value || (selectedStatus.value === 'active' ? user.is_active : !user.is_active)

      return matchesSearch && matchesRole && matchesStatus
    })
  } catch (err) {
    return users.value
  }
})

function getUserInitials(user) {
  try {
    const f = user.first_name ? user.first_name[0] : (user.name ? user.name[0] : 'U')
    const l = user.name ? user.name[0] : ''
    return (f + l).toUpperCase()
  } catch (err) {
    return 'U'
  }
}

function resetFilters() {
  searchQuery.value = ''
  selectedRole.value = ''
  selectedStatus.value = ''
}

async function toggleStatus(user) {
  try {
    await userService.setUserStatus(user.id_user, !user.is_active)
    user.is_active = !user.is_active
  } catch (err) {
    pageError.value = 'Erreur lors du changement de statut de l\'utilisateur.'
  }
}

function openCreateModal() {
  editingUser.value = null
  modalError.value = ''
  form.value = {
    first_name: '',
    name: '',
    email: '',
    password: '',
    selectedRoleIds: [],
    is_active: true
  }
  showUserModal.value = true
}

function openEditModal(user) {
  editingUser.value = user
  modalError.value = ''
  const assignedRoleIds = (user.roles || []).map(r => r.id_role)
  form.value = {
    first_name: user.first_name || '',
    name: user.name || '',
    email: user.email || '',
    password: '',
    selectedRoleIds: assignedRoleIds,
    is_active: user.is_active
  }
  showUserModal.value = true
}

async function saveUser() {
  if (!form.value.name || !form.value.email) {
    modalError.value = 'Le nom et l\'adresse email sont obligatoires.'
    return
  }

  saving.value = true
  modalError.value = ''

  try {
    const payload = {
      name: form.value.name,
      first_name: form.value.first_name,
      email: form.value.email,
      is_active: form.value.is_active,
      role_ids: form.value.selectedRoleIds
    }
    if (form.value.password) {
      payload.password = form.value.password
    }

    if (editingUser.value) {
      await userService.updateUser(editingUser.value.id_user, payload)
      await userService.assignRoles(editingUser.value.id_user, form.value.selectedRoleIds)
    } else {
      payload.password = form.value.password || 'password123'
      await userService.createUser(payload)
    }

    showUserModal.value = false
    await fetchData()
  } catch (error) {
    const message = error?.response?.data?.detail || 'Une erreur s\'est produite lors de l\'enregistrement.'
    modalError.value = message
  } finally {
    saving.value = false
  }
}

function confirmDelete(user) {
  deletingUser.value = user
  showDeleteModal.value = true
}

async function executeDelete() {
  if (!deletingUser.value) return
  deleting.value = true
  try {
    await userService.deleteUser(deletingUser.value.id_user)
    showDeleteModal.value = false
    await fetchData()
  } catch (error) {
    pageError.value = 'Erreur lors de la suppression de l\'utilisateur.'
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.filters-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.filter-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
}

.filter-select {
  padding: 0.4rem 0.8rem;
  font-size: var(--font-size-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-surface);
  color: var(--color-text);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-fullname {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.user-email {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.roles-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.status-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.toggle-status-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.15rem 0.4rem;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.toggle-status-btn:hover {
  background-color: var(--color-bg);
  color: var(--color-primary);
  border-color: var(--color-primary);
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.roles-checkboxes {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-height: 160px;
  overflow-y: auto;
  padding: var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
}

.role-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.form-checkbox {
  margin-top: var(--space-2);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.text-xs {
  font-size: var(--font-size-xs);
}
</style>
