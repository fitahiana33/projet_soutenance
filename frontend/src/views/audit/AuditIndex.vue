<template>
  <AppLayout>
    <PageHeader
      title="Journal d'Audit & Traçabilité de Sécurité"
      subtitle="Traçabilité inaltérable des actions utilisateurs, historique des modifications et journal de sécurité"
      showBack
      backFallback="/dashboard"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" @click="fetchLogs">
          <AppIcon name="refresh" size="16" />
          <span>Actualiser</span>
        </AppButton>
        <AppButton variant="secondary" size="sm" @click="handleExportExcel">
          <AppIcon name="file-text" size="16" />
          <span>Exporter Excel</span>
        </AppButton>
      </template>
    </PageHeader>

    <!-- Top Stats -->
    <div class="kpi-grid mb-6">
      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Total Événements Audit</span>
          <span class="kpi-value color-primary">{{ stats.total_logs || logs.length }}</span>
          <span class="kpi-sub text-muted">Traces enregistrées</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--primary">
          <AppIcon name="clock" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Créations / Ajouts</span>
          <span class="kpi-value color-success">{{ stats.actions_count?.CREATE || 0 }}</span>
          <span class="kpi-sub color-success">Nouvelles entités</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--success">
          <AppIcon name="shield" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Modifications / Purges</span>
          <span class="kpi-value color-warning">{{ (stats.actions_count?.UPDATE || 0) + (stats.actions_count?.DELETE || 0) }}</span>
          <span class="kpi-sub color-warning">Actions critiques</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--warning">
          <AppIcon name="box" size="24" />
        </div>
      </AppCard>
    </div>

    <!-- Filters & Table -->
    <AppCard>
      <div class="flex flex-wrap gap-3 p-4 border-b">
        <input 
          v-model="filterUser" 
          type="text" 
          placeholder="Filtrer par utilisateur..." 
          class="input text-xs w-48" 
          @input="fetchLogs"
        />
        <select v-model="filterModule" class="input text-xs w-44" @change="fetchLogs">
          <option value="">Tous les modules</option>
          <option value="VENTES">Ventes</option>
          <option value="ACHATS">Achats</option>
          <option value="STOCKS">Stocks</option>
          <option value="RH">Ressources Humaines</option>
          <option value="SYSTEME">Système</option>
        </select>
        <select v-model="filterAction" class="input text-xs w-44" @change="fetchLogs">
          <option value="">Toutes les actions</option>
          <option value="CREATE">CREATE</option>
          <option value="UPDATE">UPDATE</option>
          <option value="DELETE">DELETE</option>
          <option value="PURGE">PURGE</option>
        </select>
      </div>

      <div class="table-responsive p-4">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Horodatage</th>
              <th>Utilisateur</th>
              <th>Module</th>
              <th>Action</th>
              <th>Cible / Entité</th>
              <th>Détails</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id_audit">
              <td class="font-mono text-xs text-muted">#{{ log.id_audit }}</td>
              <td class="text-xs font-semibold text-white">{{ formatDateTime(log.created_at) }}</td>
              <td>
                <span class="font-bold color-primary">{{ log.username }}</span>
                <span v-if="log.user_role" class="text-xs text-muted block">{{ log.user_role }}</span>
              </td>
              <td><span class="badge badge-info">{{ log.module }}</span></td>
              <td><span :class="['badge', getActionBadgeClass(log.action)]">{{ log.action }}</span></td>
              <td class="font-semibold text-xs text-white">{{ log.target_entity || '-' }}</td>
              <td class="text-xs text-slate-300 max-w-xs truncate">{{ log.details || '-' }}</td>
              <td>
                <div class="flex justify-end">
                  <AppButton variant="secondary" size="xs" @click="inspectLog(log)">
                    <AppIcon name="shield" size="12" />
                    <span>Inspecter</span>
                  </AppButton>
                </div>
              </td>
            </tr>
            <tr v-if="logs.length === 0">
              <td colspan="8" class="text-center py-6 text-muted">Aucun log d'audit trouvé.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppCard>

    <!-- Inspection Modal -->
    <AppModal v-model="showInspectModal" title="Inspection Détallée de l'Événement d'Audit" size="md">
      <div v-if="selectedLog" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3 bg-slate-900 p-4 rounded border border-slate-800">
          <div><span class="text-slate-400 block mb-1">ID Événement:</span> <strong class="text-amber-400 font-mono text-sm">#{{ selectedLog.id_audit }}</strong></div>
          <div><span class="text-slate-400 block mb-1">Horodatage:</span> <strong class="text-white font-mono">{{ formatDateTime(selectedLog.created_at) }}</strong></div>
          <div><span class="text-slate-400 block mb-1">Opérateur:</span> <strong class="text-white">{{ selectedLog.username }} ({{ selectedLog.user_role || 'ADMIN' }})</strong></div>
          <div><span class="text-slate-400 block mb-1">Module & Action:</span> <strong class="color-primary">{{ selectedLog.module }} / {{ selectedLog.action }}</strong></div>
        </div>

        <div>
          <span class="font-bold text-slate-300 block mb-1">Cible concernée :</span>
          <p class="p-2 bg-slate-900 rounded border border-slate-800 text-white font-semibold">{{ selectedLog.target_entity || 'N/A' }}</p>
        </div>

        <div>
          <span class="font-bold text-slate-300 block mb-1">Détails textuels de l'opération :</span>
          <p class="p-3 bg-slate-900 rounded border border-slate-800 text-slate-200 leading-relaxed">{{ selectedLog.details || 'Aucun détail textuel supplémentaire.' }}</p>
        </div>

        <div v-if="selectedLog.old_values || selectedLog.new_values" class="grid grid-cols-2 gap-3">
          <div>
            <span class="font-bold text-rose-400 block mb-1">Valeurs Antérieures (Avant):</span>
            <pre class="p-3 bg-slate-950 rounded border border-rose-900/50 text-rose-300 overflow-x-auto text-xs">{{ JSON.stringify(selectedLog.old_values || {}, null, 2) }}</pre>
          </div>
          <div>
            <span class="font-bold text-emerald-400 block mb-1">Nouvelles Valeurs (Après):</span>
            <pre class="p-3 bg-slate-950 rounded border border-emerald-900/50 text-emerald-300 overflow-x-auto text-xs">{{ JSON.stringify(selectedLog.new_values || {}, null, 2) }}</pre>
          </div>
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showInspectModal = false">Fermer</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import auditService from '../../services/auditService'
import { exportToExcel } from '../../utils/excelExport'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppModal from '../../components/ui/AppModal.vue'

const logs = ref([])
const stats = ref({})
const filterModule = ref('')
const filterAction = ref('')
const filterUser = ref('')
const selectedLog = ref(null)
const showInspectModal = ref(false)

async function fetchLogs() {
  try {
    const [logsRes, statsRes] = await Promise.all([
      auditService.getLogs({
        module: filterModule.value,
        action: filterAction.value,
        username: filterUser.value
      }),
      auditService.getStats()
    ])
    logs.value = logsRes.data || []
    stats.value = statsRes.data || {}
  } catch (e) {
    console.error('Erreur chargement audit:', e)
  }
}

function inspectLog(log) {
  selectedLog.value = log
  showInspectModal.value = true
}

function handleExportExcel() {
  const cols = [
    { header: 'ID', key: 'id_audit' },
    { header: 'Horodatage', key: 'created_at', formatter: (val) => formatDateTime(val) },
    { header: 'Utilisateur', key: 'username' },
    { header: 'Rôle', key: 'user_role' },
    { header: 'Module', key: 'module' },
    { header: 'Action', key: 'action' },
    { header: 'Cible', key: 'target_entity' },
    { header: 'Détails', key: 'details' }
  ]
  exportToExcel('journal_audit_securite', 'Journal d\'Audit', cols, logs.value)
}

function formatDateTime(str) {
  if (!str) return '-'
  return new Date(str).toLocaleString('fr-FR')
}

function getActionBadgeClass(act) {
  if (act === 'CREATE') return 'badge-success'
  if (act === 'UPDATE') return 'badge-warning'
  if (act === 'DELETE' || act === 'PURGE') return 'badge-danger'
  return 'badge-neutral'
}

onMounted(fetchLogs)
</script>

<style scoped>
.table {
  width: 100%;
}
</style>
