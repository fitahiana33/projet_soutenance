<template>
  <AppLayout>
    <PageHeader
      title="Ressources Humaines"
      subtitle="Gestion du personnel, contrats, congés et suivi des recrutements"
    >
      <template #actions>
        <AppButton variant="primary" size="sm" @click="showEmpModal = true">
          <AppIcon name="plus" size="16" />
          <span>Nouveau Collaborateur</span>
        </AppButton>
      </template>
    </PageHeader>

    <!-- KPI Summary -->
    <div class="rh-kpis">
      <AppCard class="rh-kpi-card">
        <span class="rh-kpi-label">Effectif Total</span>
        <span class="rh-kpi-val">42</span>
        <span class="rh-kpi-sub">+3 ce trimestre</span>
      </AppCard>

      <AppCard class="rh-kpi-card">
        <span class="rh-kpi-label">En Congé Aujourd'hui</span>
        <span class="rh-kpi-val">4</span>
        <span class="rh-kpi-sub">9.5% de l'effectif</span>
      </AppCard>

      <AppCard class="rh-kpi-card">
        <span class="rh-kpi-label">Postes Ouverts</span>
        <span class="rh-kpi-val">5</span>
        <span class="rh-kpi-sub">Recrutements en cours</span>
      </AppCard>

      <AppCard class="rh-kpi-card">
        <span class="rh-kpi-label">Taux Présence</span>
        <span class="rh-kpi-val">96.2%</span>
        <span class="rh-kpi-sub">Conforme aux objectifs</span>
      </AppCard>
    </div>

    <!-- Employee Table -->
    <AppTable
      :columns="columns"
      :items="employees"
      empty-text="Aucun collaborateur trouvé."
    >
      <template #col-name="{ item }">
        <div class="emp-cell">
          <div class="emp-avatar">{{ getInitials(item.name) }}</div>
          <div>
            <span class="emp-name">{{ item.name }}</span>
            <span class="emp-email">{{ item.email }}</span>
          </div>
        </div>
      </template>

      <template #col-status="{ value }">
        <AppBadge
          :variant="value === 'Actif' ? 'success' : value === 'En congé' ? 'warning' : 'default'"
          :label="value"
        />
      </template>

      <template #actions="{ item }">
        <AppButton variant="ghost" size="sm" @click="viewEmployee(item)">
          <AppIcon name="pencil" size="14" />
          <span>Fiche</span>
        </AppButton>
      </template>
    </AppTable>

    <!-- Modal Employee -->
    <AppModal v-model="showEmpModal" title="Ajouter un Collaborateur" size="md">
      <div class="form-grid">
        <AppInput id="emp-name" v-model="empForm.name" label="Nom & Prénom" placeholder="Claire Vallet" required />
        <AppInput id="emp-email" v-model="empForm.email" type="email" label="Email Professionnel" placeholder="c.vallet@smarterp.com" required />
        <AppInput id="emp-position" v-model="empForm.position" label="Poste occupé" placeholder="Développeuse Fullstack" required />
        <AppInput id="emp-department" v-model="empForm.department" label="Département" placeholder="Technologie & SI" required />
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="showEmpModal = false">Annuler</AppButton>
        <AppButton variant="primary" @click="addEmployee">Créer la fiche</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppTable from '../../components/ui/AppTable.vue'
import AppBadge from '../../components/ui/AppBadge.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'

const showEmpModal = ref(false)

const empForm = ref({
  name: '',
  email: '',
  position: '',
  department: 'Technologie & SI'
})

const columns = [
  { key: 'name', label: 'Collaborateur', width: '30%' },
  { key: 'position', label: 'Poste', width: '25%' },
  { key: 'department', label: 'Département', width: '20%' },
  { key: 'status', label: 'Statut', width: '15%' }
]

const employees = ref([
  { id: 1, name: 'Alice Morel', email: 'a.morel@smarterp.com', position: 'Chef de Projet SI', department: 'Management', status: 'Actif' },
  { id: 2, name: 'Thomas Girard', email: 't.girard@smarterp.com', position: 'Développeur Senior', department: 'Technologie & SI', status: 'Actif' },
  { id: 3, name: 'Camille Leroy', email: 'c.leroy@smarterp.com', position: 'Responsable RH', department: 'Ressources Humaines', status: 'En congé' },
  { id: 4, name: 'Nicolas Roux', email: 'n.roux@smarterp.com', position: 'Analyste Métier ERP', department: 'Consulting', status: 'Actif' }
])

function getInitials(name) {
  const parts = name.split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.substring(0, 2).toUpperCase()
}

function addEmployee() {
  employees.value.unshift({
    id: Date.now(),
    name: empForm.value.name,
    email: empForm.value.email,
    position: empForm.value.position,
    department: empForm.value.department,
    status: 'Actif'
  })
  showEmpModal.value = false
  empForm.value = { name: '', email: '', position: '', department: 'Technologie & SI' }
}

function viewEmployee(item) {
  return item
}
</script>

<style scoped>
.rh-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.rh-kpi-card {
  display: flex;
  flex-direction: column;
}

.rh-kpi-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.rh-kpi-val {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  margin: var(--space-1) 0;
}

.rh-kpi-sub {
  font-size: var(--font-size-xs);
  color: var(--color-success);
}

.emp-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.emp-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.emp-name {
  display: block;
  font-weight: var(--font-weight-semibold);
}

.emp-email {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
</style>
