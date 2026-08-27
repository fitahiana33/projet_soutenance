<template>
  <AppLayout>
    <PageHeader
      :title="isPermissionsPage ? 'Permissions Système' : 'Rôles & Habilitations'"
      :subtitle="isPermissionsPage ? 'Catalogue des droits disponibles dans l’application' : 'Gestion des rôles et affectation des droits d’accès'"
      showBack
      backFallback="/dashboard"
    >
      <template #actions>
        <AppButton v-if="isPermissionsPage" variant="secondary" size="sm" @click="openCreatePermissionModal">
          <AppIcon name="plus" size="16" />
          <span>Nouvelle Permission</span>
        </AppButton>
        <AppButton v-else variant="primary" size="sm" @click="openCreateRoleModal">
          <AppIcon name="plus" size="16" />
          <span>Nouveau Rôle</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <!-- Roles Grid Cards -->
    <div v-if="!isPermissionsPage" class="roles-grid">
      <AppCard v-for="role in paginatedRoles" :key="role.id_role || role.id" class="role-card">
        <template #header>
          <div class="role-card__header">
            <div class="role-title-group">
              <AppIcon name="shield" size="20" class="role-icon" />
              <h3 class="role-name">{{ role.libelle || role.name }}</h3>
            </div>
            <AppBadge variant="primary" :label="`${(role.permissions || []).length} privilèges`" />
          </div>
        </template>

        <p class="role-description">{{ role.description || 'Aucune description' }}</p>

        <div class="permissions-chips">
          <span v-for="perm in (role.permissions || [])" :key="perm.id_permission || perm" class="perm-chip">
            {{ perm.code || perm }}
          </span>
          <span v-if="!(role.permissions && role.permissions.length)" class="perm-chip-empty">
            Aucune permission spécifique
          </span>
        </div>

        <template #footer>
          <div class="role-footer">
            <AppButton variant="ghost" size="sm" @click="openEditRoleModal(role)">
              <AppIcon name="pencil" size="14" />
              <span>Configurer les accès</span>
            </AppButton>
            <button
              v-if="role.libelle !== 'ADMIN'"
              type="button"
              class="delete-btn"
              title="Supprimer ce rôle"
              @click="confirmDeleteRole(role)"
            >
              <AppIcon name="trash" size="14" />
            </button>
          </div>
        </template>
      </AppCard>
    </div>

    <div v-if="!isPermissionsPage" class="list-pagination">
      <span>{{ roleRangeLabel }}</span>
      <div>
        <button type="button" :disabled="rolePage === 1" @click="rolePage--">Précédent</button>
        <strong>Page {{ rolePage }} / {{ roleTotalPages }}</strong>
        <button type="button" :disabled="rolePage === roleTotalPages" @click="rolePage++">Suivant</button>
      </div>
    </div>

    <!-- Permissions Reference Table with Interactive CRUD -->
    <AppCard v-if="isPermissionsPage" class="matrix-card">
      <template #header>
        <div class="matrix-card-header">
          <h3 class="card-title">Catalogue des Permissions Système</h3>
          <AppButton variant="secondary" size="sm" @click="openCreatePermissionModal">
            <AppIcon name="plus" size="14" />
            <span>Ajouter une Permission</span>
          </AppButton>
        </div>
      </template>

      <div class="matrix-table-wrapper">
        <table class="matrix-table">
          <thead>
            <tr>
              <th style="width: 10%;">ID</th>
              <th style="width: 30%;">Code Permission</th>
              <th style="width: 45%;">Description</th>
              <th style="width: 15%; text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="perm in paginatedPermissions" :key="perm.id_permission">
              <td class="res-id">#{{ perm.id_permission }}</td>
              <td class="res-code font-mono"><code>{{ perm.code }}</code></td>
              <td>{{ perm.description || 'Aucune description' }}</td>
              <td>
                <div class="actions-cell">
                  <button
                    type="button"
                    class="action-icon-btn"
                    title="Modifier cette permission"
                    @click="openEditPermissionModal(perm)"
                  >
                    <AppIcon name="pencil" size="14" />
                  </button>
                  <button
                    type="button"
                    class="action-icon-btn action-icon-btn--danger"
                    title="Supprimer cette permission"
                    @click="confirmDeletePermission(perm)"
                  >
                    <AppIcon name="trash" size="14" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="allPermissions.length === 0">
              <td colspan="4" class="text-center text-muted">Aucune permission enregistrée.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="list-pagination matrix-pagination">
        <span>{{ permissionRangeLabel }}</span>
        <div>
          <button type="button" :disabled="permissionPage === 1" @click="permissionPage--">Précédent</button>
          <strong>Page {{ permissionPage }} / {{ permissionTotalPages }}</strong>
          <button type="button" :disabled="permissionPage === permissionTotalPages" @click="permissionPage++">Suivant</button>
        </div>
      </div>
    </AppCard>

    <!-- Role Config Modal -->
    <AppModal
      v-model="showRoleModal"
      :title="editingRole ? 'Configurer le rôle' : 'Créer un nouveau rôle'"
      size="md"
    >
      <form @submit.prevent="saveRole" class="modal-body-content">
        <AppAlert v-if="modalError" variant="danger" dismissible @dismiss="modalError = ''">
          {{ modalError }}
        </AppAlert>

        <AppInput
          id="role-name-input"
          v-model="roleForm.libelle"
          label="Libellé du rôle"
          placeholder="ex: MANAGER_STOCK"
          required
        />

        <AppInput
          id="role-desc-input"
          v-model="roleForm.description"
          label="Description"
          placeholder="Accès aux données de stock et d'inventaire"
        />

        <h4 class="perm-section-title">Attribution des permissions (Role ↔ Permissions) :</h4>
        <div class="perm-options">
          <label
            v-for="perm in allPermissions"
            :key="perm.id_permission"
            class="perm-option"
          >
            <input
              type="checkbox"
              :value="perm.id_permission"
              v-model="roleForm.selectedPermissionIds"
            />
            <span class="font-mono strong">{{ perm.code }}</span>
            <span class="text-muted"> - {{ perm.description }}</span>
          </label>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showRoleModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveRole">
          {{ editingRole ? 'Enregistrer' : 'Créer le rôle' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Permission Create / Edit Modal -->
    <AppModal
      v-model="showPermissionModal"
      :title="editingPermission ? 'Éditer la permission' : 'Créer une nouvelle permission'"
      size="sm"
    >
      <form @submit.prevent="savePermission" class="modal-body-content">
        <AppAlert v-if="permModalError" variant="danger" dismissible @dismiss="permModalError = ''">
          {{ permModalError }}
        </AppAlert>

        <AppInput
          id="perm-code-input"
          v-model="permissionForm.code"
          label="Code de la permission"
          placeholder="ex: report:export"
          required
        />

        <AppInput
          id="perm-desc-input"
          v-model="permissionForm.description"
          label="Description"
          placeholder="Autorise l'exportation des rapports d'activité"
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showPermissionModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="savingPerm" @click="savePermission">
          {{ editingPermission ? 'Mettre à jour' : 'Créer la permission' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Confirm Delete Role Modal -->
    <AppModal v-model="showDeleteModal" title="Confirmer la suppression du rôle" size="sm">
      <p>Êtes-vous sûr de vouloir supprimer le rôle <strong>{{ deletingRole?.libelle }}</strong> ?</p>
      <template #footer>
        <AppButton variant="ghost" @click="showDeleteModal = false">Annuler</AppButton>
        <AppButton variant="danger" :loading="deleting" @click="executeDeleteRole">Supprimer</AppButton>
      </template>
    </AppModal>

    <!-- Confirm Delete Permission Modal -->
    <AppModal v-model="showDeletePermModal" title="Confirmer la suppression de la permission" size="sm">
      <p>Êtes-vous sûr de vouloir supprimer la permission <strong>{{ deletingPermission?.code }}</strong> ?</p>
      <template #footer>
        <AppButton variant="ghost" @click="showDeletePermModal = false">Annuler</AppButton>
        <AppButton variant="danger" :loading="deletingPerm" @click="executeDeletePermission">Supprimer</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import userService from '../../services/userService'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppBadge from '../../components/ui/AppBadge.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const roles = ref([])
const allPermissions = ref([])
const route = useRoute()
const isPermissionsPage = computed(() => route.path === '/permissions')
const rolePage = ref(1)
const permissionPage = ref(1)
const pageSize = 10

const roleTotalPages = computed(() => Math.max(1, Math.ceil(roles.value.length / pageSize)))
const permissionTotalPages = computed(() => Math.max(1, Math.ceil(allPermissions.value.length / pageSize)))
const paginatedRoles = computed(() => roles.value.slice((rolePage.value - 1) * pageSize, rolePage.value * pageSize))
const paginatedPermissions = computed(() => allPermissions.value.slice((permissionPage.value - 1) * pageSize, permissionPage.value * pageSize))
const roleRangeLabel = computed(() => `${roles.value.length ? (rolePage.value - 1) * pageSize + 1 : 0}–${Math.min(rolePage.value * pageSize, roles.value.length)} sur ${roles.value.length}`)
const permissionRangeLabel = computed(() => `${allPermissions.value.length ? (permissionPage.value - 1) * pageSize + 1 : 0}–${Math.min(permissionPage.value * pageSize, allPermissions.value.length)} sur ${allPermissions.value.length}`)

watch(roles, () => { if (rolePage.value > roleTotalPages.value) rolePage.value = roleTotalPages.value })
watch(allPermissions, () => { if (permissionPage.value > permissionTotalPages.value) permissionPage.value = permissionTotalPages.value })

const showRoleModal = ref(false)
const showDeleteModal = ref(false)
const editingRole = ref(null)
const deletingRole = ref(null)

const showPermissionModal = ref(false)
const showDeletePermModal = ref(false)
const editingPermission = ref(null)
const deletingPermission = ref(null)

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const savingPerm = ref(false)
const deletingPerm = ref(false)

const pageError = ref('')
const modalError = ref('')
const permModalError = ref('')

const roleForm = ref({
  libelle: '',
  description: '',
  selectedPermissionIds: []
})

const permissionForm = ref({
  code: '',
  description: ''
})

async function fetchData() {
  loading.value = true
  pageError.value = ''
  try {
    const [rolesRes, permsRes] = await Promise.all([
      userService.getRoles().catch(() => ({ data: [] })),
      userService.getPermissions().catch(() => ({ data: [] }))
    ])
    if (rolesRes.data && Array.isArray(rolesRes.data)) {
      roles.value = rolesRes.data
    }
    if (permsRes.data && Array.isArray(permsRes.data)) {
      allPermissions.value = permsRes.data
    }
  } catch (error) {
    pageError.value = 'Erreur lors du chargement des rôles et permissions.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

// --- ROLE CRUD LOGIC ---

function openCreateRoleModal() {
  editingRole.value = null
  modalError.value = ''
  roleForm.value = {
    libelle: '',
    description: '',
    selectedPermissionIds: []
  }
  showRoleModal.value = true
}

function openEditRoleModal(role) {
  editingRole.value = role
  modalError.value = ''
  const assignedIds = (role.permissions || []).map(p => p.id_permission)
  roleForm.value = {
    libelle: role.libelle || role.name || '',
    description: role.description || '',
    selectedPermissionIds: assignedIds
  }
  showRoleModal.value = true
}

async function saveRole() {
  if (!roleForm.value.libelle) {
    modalError.value = 'Le libellé du rôle est obligatoire.'
    return
  }

  saving.value = true
  modalError.value = ''

  try {
    const payload = {
      libelle: roleForm.value.libelle,
      description: roleForm.value.description,
      permission_ids: roleForm.value.selectedPermissionIds
    }

    if (editingRole.value) {
      await userService.updateRole(editingRole.value.id_role, payload)
      await userService.assignPermissions(editingRole.value.id_role, roleForm.value.selectedPermissionIds)
    } else {
      await userService.createRole(payload)
    }

    showRoleModal.value = false
    await fetchData()
  } catch (error) {
    modalError.value = 'Une erreur s\'est produite lors de l\'enregistrement.'
  } finally {
    saving.value = false
  }
}

function confirmDeleteRole(role) {
  deletingRole.value = role
  showDeleteModal.value = true
}

async function executeDeleteRole() {
  if (!deletingRole.value) return
  deleting.value = true
  try {
    await userService.deleteRole(deletingRole.value.id_role)
    showDeleteModal.value = false
    await fetchData()
  } catch (error) {
    pageError.value = 'Erreur lors de la suppression du rôle.'
  } finally {
    deleting.value = false
  }
}

// --- PERMISSION CRUD LOGIC ---

function openCreatePermissionModal() {
  editingPermission.value = null
  permModalError.value = ''
  permissionForm.value = {
    code: '',
    description: ''
  }
  showPermissionModal.value = true
}

function openEditPermissionModal(perm) {
  editingPermission.value = perm
  permModalError.value = ''
  permissionForm.value = {
    code: perm.code || '',
    description: perm.description || ''
  }
  showPermissionModal.value = true
}

async function savePermission() {
  if (!permissionForm.value.code) {
    permModalError.value = 'Le code de la permission est obligatoire.'
    return
  }

  savingPerm.value = true
  permModalError.value = ''

  try {
    const payload = {
      code: permissionForm.value.code,
      description: permissionForm.value.description
    }

    if (editingPermission.value) {
      await userService.updatePermission(editingPermission.value.id_permission, payload)
    } else {
      await userService.createPermission(payload)
    }

    showPermissionModal.value = false
    await fetchData()
  } catch (error) {
    permModalError.value = 'Erreur lors de l\'enregistrement de la permission.'
  } finally {
    savingPerm.value = false
  }
}

function confirmDeletePermission(perm) {
  deletingPermission.value = perm
  showDeletePermModal.value = true
}

async function executeDeletePermission() {
  if (!deletingPermission.value) return
  deletingPerm.value = true
  try {
    await userService.deletePermission(deletingPermission.value.id_permission)
    showDeletePermModal.value = false
    await fetchData()
  } catch (error) {
    pageError.value = 'Erreur lors de la suppression de la permission.'
  } finally {
    deletingPerm.value = false
  }
}
</script>

<style scoped>
.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.list-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0 1.5rem;
  color: var(--color-text-muted);
  font-size: 0.8rem;
}
.list-pagination > div {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.list-pagination button {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.45rem 0.7rem;
  background: var(--color-bg-card);
  color: var(--color-text);
  cursor: pointer;
}
.list-pagination button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.matrix-pagination {
  margin: 1rem 0 0;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.role-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.role-title-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.role-icon {
  color: var(--color-primary);
}

.role-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  margin: 0;
}

.role-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
  line-height: 1.4;
}

.permissions-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.perm-chip {
  font-size: 0.7rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-sm);
  font-family: monospace;
  color: var(--color-text);
}

.perm-chip-empty {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-style: italic;
}

.role-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.delete-btn {
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-danger);
  border-radius: var(--radius-sm);
  padding: 0.35rem 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.delete-btn:hover {
  background-color: var(--color-danger-light);
}

.matrix-card {
  margin-top: var(--space-4);
}

.matrix-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.card-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.matrix-table-wrapper {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.matrix-table th {
  background-color: var(--color-bg);
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-semibold);
}

.matrix-table td {
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.actions-cell {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-2);
}

.action-icon-btn {
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

.action-icon-btn:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.action-icon-btn--danger:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.modal-body-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.perm-section-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin-top: var(--space-2);
}

.perm-options {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-height: 220px;
  overflow-y: auto;
  padding: var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
}

.perm-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.font-mono {
  font-family: monospace;
}

.text-muted {
  color: var(--color-text-muted);
}

.text-center {
  text-align: center;
}
</style>
