<template>
  <AppLayout>
    <PageHeader
      title="Intégration & Synchronisation Dolibarr"
      subtitle="Connecteur API REST, gestion de la synchronisation des produits, tiers, commandes, factures et employés"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" :loading="testingConn" @click="testConnection">
          <AppIcon name="refresh" size="16" />
          <span>Tester la Connexion API</span>
        </AppButton>
        <AppButton variant="primary" size="sm" :loading="syncing" @click="triggerSync">
          <AppIcon name="download" size="16" />
          <span>Synchronisation Manuelle</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <!-- Connection Status Banner Card -->
    <AppCard class="conn-card">
      <div class="conn-banner">
        <div class="conn-info">
          <div :class="['conn-indicator', connectionStatus.connected ? 'conn-indicator--online' : 'conn-indicator--offline']">
            <AppIcon :name="connectionStatus.connected ? 'check' : 'x'" size="18" />
          </div>
          <div>
            <div class="conn-title-group">
              <h3 class="conn-title">Statut de l'API Dolibarr ERP</h3>
              <AppBadge
                :variant="connectionStatus.connected ? 'success' : 'danger'"
                :label="connectionStatus.connected ? 'Connecté' : 'Hors ligne / Indisponible'"
              />
            </div>
            <p class="conn-desc">
              URL Endpoint : <code>{{ connectionStatus.base_url }}</code>
              <span v-if="connectionStatus.version"> | Version: {{ connectionStatus.version }}</span>
              <span v-if="connectionStatus.response_time_ms"> | Latence: {{ connectionStatus.response_time_ms }} ms</span>
            </p>
          </div>
        </div>

        <div class="conn-meta">
          <span class="last-sync-label">Dernière synchronisation :</span>
          <span class="last-sync-time">{{ formatTime(lastSyncDate) }}</span>
        </div>
      </div>
    </AppCard>

    <!-- Synchronized Entities Cards Grid -->
    <div class="entities-grid">
      <AppCard v-for="item in entityCards" :key="item.key" class="entity-card">
        <div class="entity-card-body">
          <div :class="['entity-icon', `entity-icon--${item.color}`]">
            <AppIcon :name="item.icon" size="22" />
          </div>
          <div class="entity-details">
            <span class="entity-title">{{ item.title }}</span>
            <span class="entity-count">{{ entityCounts[item.key] || 0 }} répercutés</span>
            <span class="entity-subtext">{{ item.description }}</span>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Manual Sync Control & Options Panel -->
    <AppCard title="Panneau de Contrôle de Synchronisation Manuelle" class="control-card">
      <div class="control-content">
        <p class="control-desc">
          Sélectionnez les périmètres de données Dolibarr à récupérer. La synchronisation s'effectue de manière incrémentale selon les données modifiées.
        </p>

        <div class="checkbox-grid">
          <label v-for="ent in availableEntities" :key="ent.key" class="entity-checkbox-label">
            <input type="checkbox" :value="ent.key" v-model="selectedEntities" />
            <AppIcon :name="ent.icon" size="16" />
            <span class="strong">{{ ent.label }}</span>
          </label>
        </div>

        <div class="sync-actions-bar">
          <label class="force-full-checkbox">
            <input type="checkbox" v-model="forceFullSync" />
            <span>Forcer une synchronisation intégrale (Re-télécharger tout)</span>
          </label>

          <AppButton variant="primary" :loading="syncing" @click="triggerSync">
            <AppIcon name="download" size="16" />
            <span>Lancer la Synchronisation</span>
          </AppButton>
        </div>
      </div>
    </AppCard>

    <!-- Synchronization Execution History Log Table -->
    <AppCard title="Journal d'Historique des Synchronisations" class="history-card">
      <div class="table-wrapper">
        <table class="history-table">
          <thead>
            <tr>
              <th>Date & Heure</th>
              <th>Déclenché par</th>
              <th>Durée</th>
              <th>Périmètres</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in syncHistory" :key="log.id">
              <td>{{ formatTime(log.timestamp) }}</td>
              <td><span class="font-semibold">{{ log.triggered_by }}</span></td>
              <td>{{ log.duration_seconds }} s</td>
              <td>
                <div class="chips-group">
                  <span v-for="res in log.results" :key="res.entity" class="history-chip">
                    {{ res.entity }}: {{ res.items_synced }}
                  </span>
                </div>
              </td>
              <td>
                <AppBadge
                  :variant="log.status === 'success' ? 'success' : log.status === 'warning' ? 'warning' : 'danger'"
                  :label="log.status === 'success' ? 'Réussi' : log.status === 'warning' ? 'Partiel' : 'Erreur'"
                />
              </td>
            </tr>
            <tr v-if="syncHistory.length === 0">
              <td colspan="5" class="text-center text-muted">Aucun historique de synchronisation enregistré.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppCard>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppBadge from '../../components/ui/AppBadge.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const testingConn = ref(false)
const syncing = ref(false)
const pageError = ref('')
const pageSuccess = ref('')

const connectionStatus = ref({
  connected: false,
  base_url: 'http://dolibarr:8080',
  message: 'Chargement du statut...',
  version: '',
  response_time_ms: null
})

const lastSyncDate = ref(null)
const entityCounts = ref({
  products: 0,
  thirdparties: 0,
  orders: 0,
  invoices: 0,
  users: 0
})

const selectedEntities = ref(['products', 'thirdparties', 'orders', 'invoices', 'users'])
const forceFullSync = ref(false)
const syncHistory = ref([])

const availableEntities = [
  { key: 'products', label: 'Produits & Stocks', icon: 'package' },
  { key: 'thirdparties', label: 'Fournisseurs & Clients', icon: 'users' },
  { key: 'orders', label: 'Commandes Achats & Ventes', icon: 'shopping-cart' },
  { key: 'invoices', label: 'Factures', icon: 'file-text' },
  { key: 'users', label: 'Employés & Utilisateurs', icon: 'user' }
]

const entityCards = [
  { key: 'products', title: 'Produits & Stocks', color: 'primary', icon: 'package', description: 'Inventaires, références et quantités' },
  { key: 'thirdparties', title: 'Fournisseurs & Clients', color: 'info', icon: 'users', description: 'Comptes tiers, adresses et contacts' },
  { key: 'orders', title: 'Commandes (Achats/Ventes)', color: 'warning', icon: 'shopping-cart', description: 'Bons de commande et approvisionnements' },
  { key: 'invoices', title: 'Factures', color: 'success', icon: 'file-text', description: 'Règlements et pièces comptables' },
  { key: 'users', title: 'Employés Dolibarr', color: 'purple', icon: 'user', description: 'Comptes collaborateurs ERP' }
]

async function loadDolibarrStatus() {
  pageError.value = ''
  try {
    const res = await api.get('/dolibarr/status').catch(() => null)
    if (res && res.data) {
      connectionStatus.value = res.data.connection || connectionStatus.value
      lastSyncDate.value = res.data.last_sync_date
      if (res.data.total_synced_entities) {
        entityCounts.value = res.data.total_synced_entities
      }
    }
  } catch (error) {
    pageError.value = 'Erreur lors du chargement du statut Dolibarr.'
  }
}

async function loadSyncHistory() {
  try {
    const res = await api.get('/dolibarr/sync-history').catch(() => null)
    if (res && res.data && Array.isArray(res.data)) {
      syncHistory.value = res.data
    }
  } catch (error) {
    // History fallback
  }
}

async function testConnection() {
  testingConn.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    const res = await api.get('/dolibarr/test-connection')
    connectionStatus.value = res.data
    if (res.data.connected) {
      pageSuccess.value = 'Connexion à l\'API Dolibarr vérifiée avec succès !'
    } else {
      pageError.value = res.data.message || 'Impossible d\'établir la connexion Dolibarr.'
    }
  } catch (error) {
    pageError.value = 'Échec du test de connexion avec le serveur API Dolibarr.'
  } finally {
    testingConn.value = false
  }
}

async function triggerSync() {
  if (selectedEntities.value.length === 0) {
    pageError.value = 'Veuillez sélectionner au moins une entité à synchroniser.'
    return
  }

  syncing.value = true
  pageError.value = ''
  pageSuccess.value = ''

  try {
    const res = await api.post('/dolibarr/sync', {
      entities: selectedEntities.value,
      force_full: forceFullSync.value
    })

    pageSuccess.value = 'Synchronisation Dolibarr exécutée avec succès !'
    await loadDolibarrStatus()
    await loadSyncHistory()
  } catch (error) {
    pageError.value = 'Une erreur est survenue pendant la synchronisation Dolibarr.'
  } finally {
    syncing.value = false
  }
}

function formatTime(isoStr) {
  if (!isoStr) return 'Jamais'
  try {
    const d = new Date(isoStr)
    return d.toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return isoStr
  }
}

onMounted(() => {
  loadDolibarrStatus()
  loadSyncHistory()
})
</script>

<style scoped>
.conn-card {
  margin-bottom: var(--space-6);
}

.conn-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.conn-info {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.conn-indicator {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}

.conn-indicator--online {
  background-color: var(--color-success);
}

.conn-indicator--offline {
  background-color: var(--color-danger);
}

.conn-title-group {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.conn-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-bold);
  margin: 0;
}

.conn-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 4px 0 0;
}

.conn-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: var(--font-size-xs);
}

.last-sync-label {
  color: var(--color-text-muted);
}

.last-sync-time {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.entities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.entity-card-body {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
}

.entity-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.entity-icon--primary { background: var(--color-primary-light); color: var(--color-primary); }
.entity-icon--info { background: rgba(37, 99, 235, 0.1); color: #1d4ed8; }
.entity-icon--warning { background: var(--color-warning-light); color: var(--color-warning); }
.entity-icon--success { background: var(--color-success-light); color: var(--color-success); }
.entity-icon--purple { background: rgba(147, 51, 234, 0.1); color: #7e22ce; }

.entity-details {
  display: flex;
  flex-direction: column;
}

.entity-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
}

.entity-count {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  margin: 2px 0;
}

.entity-subtext {
  font-size: 0.7rem;
  color: var(--color-text-muted);
}

.control-card {
  margin-bottom: var(--space-6);
}

.control-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.control-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-3);
  background-color: var(--color-bg);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.entity-checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.sync-actions-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.force-full-checkbox {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  cursor: pointer;
}

.history-card {
  margin-top: var(--space-4);
}

.table-wrapper {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.history-table th {
  background-color: var(--color-bg);
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-semibold);
}

.history-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.chips-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.history-chip {
  font-size: 0.7rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  padding: 0.1rem 0.4rem;
  border-radius: var(--radius-sm);
  font-family: monospace;
}

.text-center { text-align: center; }
.text-muted { color: var(--color-text-muted); }
.strong { font-weight: var(--font-weight-semibold); }
.font-semibold { font-weight: var(--font-weight-semibold); }
</style>
