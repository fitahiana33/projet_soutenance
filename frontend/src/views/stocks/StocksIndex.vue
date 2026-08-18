<template>
  <AppLayout>
    <PageHeader
      title="Gestion des Stocks & Inventaires"
      subtitle="Analyse globale, valorisation CUMP/FIFO, taux de rotation et traçabilité des lots (FEFO)"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" @click="handleExportStocksExcel">
          <AppIcon name="file-text" size="16" />
          <span>Exporter Excel</span>
        </AppButton>
        <AppButton variant="secondary" size="sm" @click="openCreateLotModal">
          <AppIcon name="box" size="16" />
          <span>Nouveau Lot / Série</span>
        </AppButton>
        <AppButton variant="primary" size="sm" @click="openNewMovementModal">
          <AppIcon name="plus" size="16" />
          <span>Nouveau Mouvement</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <!-- Stock KPI Summary Cards -->
    <div class="kpi-grid mb-6">
      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Stock Physique Total</span>
          <span class="kpi-value">{{ overview.total_physical_stock || 0 }} <span class="kpi-unit">unités</span></span>
          <span class="kpi-sub font-semibold color-success">{{ overview.total_available_stock || 0 }} disponibles</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--primary">
          <AppIcon name="box" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Valeur Inventaire Totale</span>
          <span class="kpi-value">{{ formatCurrency(overview.total_stock_value || 0) }}</span>
          <span class="kpi-sub text-muted">Coût d'achat catalogue</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--success">
          <AppIcon name="refresh" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Alertes & Ruptures</span>
          <span class="kpi-value color-danger">{{ overview.out_of_stock_count || 0 }} <span class="kpi-unit">ruptures</span></span>
          <span class="kpi-sub color-warning">{{ overview.low_stock_count || 0 }} stocks critiques</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--danger">
          <AppIcon name="alert-circle" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Références Cataloguées</span>
          <span class="kpi-value">{{ overview.total_products || 0 }}</span>
          <span class="kpi-sub text-muted">Synchronisées Dolibarr</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--info">
          <AppIcon name="package" size="24" />
        </div>
      </AppCard>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-header mb-4">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-btn', { 'tab-btn--active': activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <AppIcon :name="tab.icon" size="16" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- TAB 1: SYNTHÈSE DU STOCK -->
    <div v-if="activeTab === 'overview'">
      <AppTable
        :columns="columnsOverview"
        :items="products"
        :loading="loading"
        empty-text="Aucun produit enregistré."
      >
        <template #col-reference="{ item }">
          <span class="sku-badge font-mono">{{ item.reference }}</span>
        </template>

        <template #col-label="{ item }">
          <span class="font-semibold text-color">{{ item.label }}</span>
        </template>

        <template #col-stock_quantity="{ item }">
          <div class="stock-levels">
            <span>Physique: <strong>{{ item.stock_quantity }}</strong></span>
            <span>Disponible: <strong class="color-success">{{ item.stock_available }}</strong></span>
            <span class="text-xs text-muted">Réservé: {{ item.stock_reserved }}</span>
          </div>
        </template>

        <template #col-stock_min="{ item }">
          <div class="stock-limits">
            <span>Min: {{ item.stock_min }}</span>
            <span>Max: {{ item.stock_max }}</span>
          </div>
        </template>

        <template #col-status="{ item }">
          <AppBadge
            :variant="item.stock_quantity === 0 ? 'danger' : item.stock_quantity <= item.stock_min ? 'warning' : 'success'"
            :label="item.stock_quantity === 0 ? 'Rupture' : item.stock_quantity <= item.stock_min ? 'Alerte' : 'Stock OK'"
          />
        </template>

        <template #actions="{ item }">
          <AppButton variant="ghost" size="xs" @click="openQuickMovementModal(item)">
            <AppIcon name="refresh" size="14" />
            <span>Ajuster</span>
          </AppButton>
        </template>
      </AppTable>
    </div>

    <!-- TAB 2: JOURNAL DES MOUVEMENTS -->
    <div v-if="activeTab === 'movements'">
      <div class="filters-card-compact mb-4">
        <div class="filters-row">
          <div class="filter-group-compact">
            <select v-model="selectedMovementType" class="filter-select-compact" @change="fetchMovements">
              <option value="">Tous les types</option>
              <option value="ENTREE">Entrées (+)</option>
              <option value="SORTIE">Sorties (-)</option>
              <option value="TRANSFERT">Transferts (↔)</option>
              <option value="AJUSTEMENT">Ajustements (⚙)</option>
            </select>
          </div>
        </div>
      </div>

      <AppTable
        :columns="columnsMovements"
        :items="movements"
        :loading="loadingMovements"
        empty-text="Aucun mouvement de stock enregistré."
      >
        <template #col-movement_type="{ value }">
          <AppBadge
            :variant="value === 'ENTREE' ? 'success' : value === 'SORTIE' ? 'danger' : 'warning'"
            :label="value"
          />
        </template>

        <template #col-quantity="{ item }">
          <span :class="['font-bold', item.movement_type === 'ENTREE' ? 'color-success' : 'color-danger']">
            {{ item.movement_type === 'ENTREE' ? '+' : '-' }}{{ item.quantity }}
          </span>
        </template>
      </AppTable>
    </div>

    <!-- TAB 3: VALORISATION FINANCIÈRE (CUMP / FIFO) -->
    <div v-if="activeTab === 'valuation'">
      <AppTable
        :columns="columnsValuation"
        :items="valuationData.products || []"
        :loading="loadingValuation"
        empty-text="Aucune donnée de valorisation disponible."
      >
        <template #col-unit_cost_price="{ value }">
          {{ formatCurrency(value) }}
        </template>

        <template #col-total_value_cump="{ value }">
          <strong class="color-primary">{{ formatCurrency(value) }}</strong>
        </template>

        <template #col-total_value_fifo="{ value }">
          <strong class="color-success">{{ formatCurrency(value) }}</strong>
        </template>

        <template #col-variance_cump_fifo="{ value }">
          <span :class="value >= 0 ? 'color-success' : 'color-danger'">
            {{ value >= 0 ? '+' : '' }}{{ formatCurrency(value) }}
          </span>
        </template>
      </AppTable>
    </div>

    <!-- TAB 4: ROTATION ET VITESSE DE STOCK -->
    <div v-if="activeTab === 'rotation'">
      <AppTable
        :columns="columnsRotation"
        :items="rotationData"
        :loading="loadingRotation"
        empty-text="Aucune donnée de rotation."
      >
        <template #col-turnover_rate="{ value }">
          <span class="font-bold">{{ value }}x / an</span>
        </template>

        <template #col-average_retention_days="{ value }">
          <span>{{ value }} jours</span>
        </template>

        <template #col-rotation_speed="{ value }">
          <AppBadge
            :variant="value === 'RAPIDE' ? 'success' : value === 'MOYENNE' ? 'info' : value === 'LENTE' ? 'warning' : 'danger'"
            :label="value"
          />
        </template>
      </AppTable>
    </div>

    <!-- TAB 5: LOTS & SÉRIES (TRAÇABILITÉ FEFO) -->
    <div v-if="activeTab === 'lots'">
      <AppTable
        :columns="columnsLots"
        :items="lots"
        :loading="loadingLots"
        empty-text="Aucun lot ou numéro de série enregistré."
      >
        <template #col-batch_number="{ item }">
          <span class="sku-badge font-mono">{{ item.batch_number }}</span>
        </template>

        <template #col-status="{ item }">
          <AppBadge
            :variant="item.is_blocked ? 'danger' : item.status === 'ALERTE_PROCHE' ? 'warning' : 'success'"
            :label="item.is_blocked ? 'EXPIRÉ / BLOQUÉ' : item.status === 'ALERTE_PROCHE' ? 'Expire bientot' : 'Valide (FEFO)'"
          />
        </template>
      </AppTable>
    </div>

    <!-- Modal Nouveau Mouvement de Stock -->
    <AppModal v-model="showMovementModal" title="Enregistrer un Mouvement de Stock" size="sm">
      <form @submit.prevent="saveMovement" class="modal-form">
        <AppAlert v-if="modalError" variant="danger" dismissible @dismiss="modalError = ''">
          {{ modalError }}
        </AppAlert>

        <div class="form-group">
          <label class="form-label">Produit *</label>
          <select v-model="mvtForm.product_id" class="form-select" required>
            <option :value="null">Sélectionner un produit</option>
            <option v-for="p in products" :key="p.id_product" :value="p.id_product">
              {{ p.reference }} — {{ p.label }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Type de Mouvement *</label>
          <select v-model="mvtForm.movement_type" class="form-select" required>
            <option value="ENTREE">Entrée (+)</option>
            <option value="SORTIE">Sortie (-)</option>
            <option value="TRANSFERT">Transfert d'entrepôt</option>
            <option value="AJUSTEMENT">Ajustement inventaire</option>
          </select>
        </div>

        <AppInput
          id="mvt-qty"
          v-model.number="mvtForm.quantity"
          type="number"
          label="Quantité *"
          placeholder="ex: 10"
          required
        />

        <AppInput
          id="mvt-ref"
          v-model="mvtForm.reference_doc"
          label="N° Référence / Bon"
          placeholder="ex: BL-2026-089"
        />

        <AppInput
          id="mvt-comment"
          v-model="mvtForm.comment"
          label="Commentaire / Motif"
          placeholder="Motif de l'opération..."
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showMovementModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="savingMvt" @click="saveMovement">Valider Mouvement</AppButton>
      </template>
    </AppModal>

    <!-- Modal Nouveau Lot / Série (FEFO) -->
    <AppModal v-model="showLotModal" title="Nouveau Lot / Numéro de Série" size="sm">
      <form @submit.prevent="saveLot" class="modal-form">
        <AppAlert v-if="lotModalError" variant="danger" dismissible @dismiss="lotModalError = ''">
          {{ lotModalError }}
        </AppAlert>

        <div class="form-group">
          <label class="form-label">Produit *</label>
          <select v-model="lotForm.product_id" class="form-select" required>
            <option :value="null">Sélectionner un produit</option>
            <option v-for="p in products" :key="p.id_product" :value="p.id_product">
              {{ p.reference }} — {{ p.label }}
            </option>
          </select>
        </div>

        <AppInput
          id="lot-batch"
          v-model="lotForm.batch_number"
          label="Numéro de Lot *"
          placeholder="ex: LOT-2026-X9"
          required
        />

        <AppInput
          id="lot-serial"
          v-model="lotForm.serial_number"
          label="Numéro de Série (Optionnel)"
          placeholder="ex: SN-987654321"
        />

        <AppInput
          id="lot-exp"
          v-model="lotForm.expiration_date"
          type="date"
          label="Date d'expiration (FEFO)"
        />

        <AppInput
          id="lot-qty"
          v-model.number="lotForm.quantity"
          type="number"
          label="Quantité dans le lot"
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showLotModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="savingLot" @click="saveLot">Enregistrer le Lot</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import stockService from '../../services/stockService'
import { exportToExcel } from '../../utils/excelExport'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppTable from '../../components/ui/AppTable.vue'
import AppBadge from '../../components/ui/AppBadge.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const activeTab = ref('overview')
const overview = ref({})
const products = ref([])
const movements = ref([])
const valuationData = ref({})
const rotationData = ref([])
const lots = ref([])

const loading = ref(false)
const loadingMovements = ref(false)
const loadingValuation = ref(false)
const loadingRotation = ref(false)
const loadingLots = ref(false)

const savingMvt = ref(false)
const savingLot = ref(false)

const pageError = ref('')
const pageSuccess = ref('')
const modalError = ref('')
const lotModalError = ref('')

const showMovementModal = ref(false)
const showLotModal = ref(false)
const selectedMovementType = ref('')

const tabs = [
  { id: 'overview', label: 'Synthèse des Stocks', icon: 'box' },
  { id: 'movements', label: 'Journal des Mouvements', icon: 'refresh' },
  { id: 'valuation', label: 'Valorisation CUMP / FIFO', icon: 'shield' },
  { id: 'rotation', label: 'Taux de Rotation', icon: 'clock' },
  { id: 'lots', label: 'Lots & Traçabilité FEFO', icon: 'package' }
]

const mvtForm = ref({
  product_id: null,
  movement_type: 'ENTREE',
  quantity: 1,
  reference_doc: '',
  comment: ''
})

const lotForm = ref({
  product_id: null,
  batch_number: '',
  serial_number: '',
  expiration_date: '',
  quantity: 10
})

const columnsOverview = [
  { key: 'reference', label: 'SKU', width: '15%' },
  { key: 'label', label: 'Désignation', width: '30%' },
  { key: 'stock_quantity', label: 'Niveaux de Stock', width: '25%' },
  { key: 'stock_min', label: 'Seuils (Min/Max)', width: '15%' },
  { key: 'status', label: 'Statut', width: '15%' }
]

const columnsMovements = [
  { key: 'created_at', label: 'Date', width: '18%' },
  { key: 'product_ref', label: 'SKU', width: '15%' },
  { key: 'product_label', label: 'Produit', width: '25%' },
  { key: 'movement_type', label: 'Type Mouvement', width: '15%' },
  { key: 'quantity', label: 'Quantité', width: '12%' },
  { key: 'reference_doc', label: 'Réf Document', width: '15%' }
]

const columnsValuation = [
  { key: 'reference', label: 'SKU', width: '15%' },
  { key: 'label', label: 'Produit', width: '25%' },
  { key: 'stock_quantity', label: 'Stock', width: '10%' },
  { key: 'unit_cost_price', label: 'Coût Unitaire', width: '15%' },
  { key: 'total_value_cump', label: 'Valeur CUMP', width: '15%' },
  { key: 'total_value_fifo', label: 'Valeur FIFO', width: '15%' },
  { key: 'variance_cump_fifo', label: 'Écart', width: '10%' }
]

const columnsRotation = [
  { key: 'reference', label: 'SKU', width: '15%' },
  { key: 'label', label: 'Produit', width: '30%' },
  { key: 'turnover_rate', label: 'Taux de Rotation', width: '18%' },
  { key: 'average_retention_days', label: 'Rétention Moyenne', width: '20%' },
  { key: 'rotation_speed', label: 'Vitesse', width: '17%' }
]

const columnsLots = [
  { key: 'batch_number', label: 'N° de Lot', width: '20%' },
  { key: 'product_label', label: 'Produit', width: '25%' },
  { key: 'serial_number', label: 'N° de Série', width: '18%' },
  { key: 'expiration_date', label: 'Expiration (FEFO)', width: '20%' },
  { key: 'status', label: 'État & Blocage', width: '17%' }
]

async function loadData() {
  loading.value = true
  pageError.value = ''
  try {
    const [ovRes, prodRes] = await Promise.all([
      stockService.getOverview(),
      stockService.getProducts()
    ])
    overview.value = ovRes.data || {}
    products.value = prodRes.data || []
  } catch (error) {
    pageError.value = 'Erreur lors du chargement des données de stock.'
  } finally {
    loading.value = false
  }
}

async function fetchMovements() {
  loadingMovements.value = true
  try {
    const params = selectedMovementType.value ? { movement_type: selectedMovementType.value } : {}
    const res = await stockService.getMovements(params)
    movements.value = res.data || []
  } catch (e) {
    // Handling
  } finally {
    loadingMovements.value = false
  }
}

async function fetchValuation() {
  loadingValuation.value = true
  try {
    const res = await stockService.getValuation()
    valuationData.value = res.data || {}
  } catch (e) {
    // Handling
  } finally {
    loadingValuation.value = false
  }
}

async function fetchRotation() {
  loadingRotation.value = true
  try {
    const res = await stockService.getRotation()
    rotationData.value = res.data || []
  } catch (e) {
    // Handling
  } finally {
    loadingRotation.value = false
  }
}

async function fetchLots() {
  loadingLots.value = true
  try {
    const res = await stockService.getLots()
    lots.value = res.data || []
  } catch (e) {
    // Handling
  } finally {
    loadingLots.value = false
  }
}

onMounted(async () => {
  await loadData()
  await Promise.all([fetchMovements(), fetchValuation(), fetchRotation(), fetchLots()])
})

function handleExportStocksExcel() {
  if (activeTab.value === 'movements') {
    const cols = [
      { header: 'ID', key: 'id_movement' },
      { header: 'Article', key: 'product_name' },
      { header: 'Type Mouvement', key: 'movement_type' },
      { header: 'Quantité', key: 'quantity' },
      { header: 'Stock Avant', key: 'stock_before' },
      { header: 'Stock Après', key: 'stock_after' },
      { header: 'Référence Doc', key: 'reference_doc' },
      { header: 'Date', key: 'created_at' }
    ]
    exportToExcel('mouvements_stock', 'Mouvements Stock', cols, movements.value)
  } else if (activeTab.value === 'lots') {
    const cols = [
      { header: 'N° Lot', key: 'lot_number' },
      { header: 'Article', key: 'product_name' },
      { header: 'Qté Initiale', key: 'quantity_initial' },
      { header: 'Qté Restante', key: 'quantity_remaining' },
      { header: 'Fabrication', key: 'manufacturing_date' },
      { header: 'Expiration (FEFO)', key: 'expiration_date' },
      { header: 'Statut', key: 'status' }
    ]
    exportToExcel('lots_stock', 'Lots & Séries', cols, lots.value)
  } else {
    const cols = [
      { header: 'Code SKU', key: 'sku' },
      { header: 'Désignation', key: 'name' },
      { header: 'Stock Physique', key: 'physical_stock' },
      { header: 'Stock Réservé', key: 'reserved_stock' },
      { header: 'Stock Disponible', key: 'available_stock' },
      { header: 'PUMP (€)', key: 'cump' },
      { header: 'Valeur Stock (€)', key: 'stock_value' },
      { header: 'Statut Alert', key: 'alert_status' }
    ]
    exportToExcel('etat_stock_articles', 'État des Stocks', cols, products.value)
  }
}

function formatCurrency(val) {
  if (val === undefined || val === null) return '0,00 €'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val)
}

function openNewMovementModal() {
  mvtForm.value = {
    product_id: products.value.length ? products.value[0].id_product : null,
    movement_type: 'ENTREE',
    quantity: 1,
    reference_doc: '',
    comment: ''
  }
  modalError.value = ''
  showMovementModal.value = true
}

function openQuickMovementModal(item) {
  mvtForm.value = {
    product_id: item.id_product,
    movement_type: 'ENTREE',
    quantity: 1,
    reference_doc: '',
    comment: 'Ajustement rapide'
  }
  modalError.value = ''
  showMovementModal.value = true
}

async function saveMovement() {
  if (!mvtForm.value.product_id || !mvtForm.value.quantity) {
    modalError.value = 'Veuillez sélectionner un produit et saisir une quantité.'
    return
  }

  savingMvt.value = true
  modalError.value = ''
  
  const payload = {
    ...mvtForm.value,
    product_id: Number(mvtForm.value.product_id),
    quantity: Number(mvtForm.value.quantity)
  }

  try {
    await stockService.createMovement(payload)
    pageSuccess.value = 'Mouvement de stock enregistré avec succès !'
    showMovementModal.value = false
    await loadData()
    await fetchMovements()
    await fetchValuation()
    await fetchRotation()
  } catch (error) {
    modalError.value = error?.response?.data?.detail?.[0]?.msg || error?.response?.data?.detail || 'Erreur lors de l\'enregistrement.'
  } finally {
    savingMvt.value = false
  }
}

function openCreateLotModal() {
  lotForm.value = {
    product_id: products.value.length ? products.value[0].id_product : null,
    batch_number: '',
    serial_number: '',
    expiration_date: '',
    quantity: 10
  }
  lotModalError.value = ''
  showLotModal.value = true
}

async function saveLot() {
  if (!lotForm.value.product_id || !lotForm.value.batch_number) {
    lotModalError.value = 'Le produit et le numéro de lot sont obligatoires.'
    return
  }

  savingLot.value = true
  lotModalError.value = ''
  
  const payload = {
    ...lotForm.value,
    product_id: Number(lotForm.value.product_id),
    quantity: Number(lotForm.value.quantity || 0)
  }

  try {
    await stockService.createLot(payload)
    pageSuccess.value = 'Nouveau lot / série enregistré avec succès !'
    showLotModal.value = false
    await fetchLots()
  } catch (error) {
    lotModalError.value = error?.response?.data?.detail?.[0]?.msg || error?.response?.data?.detail || 'Erreur lors de la création du lot.'
  } finally {
    savingLot.value = false
  }
}
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
}

.kpi-card {
  padding: var(--space-4);
  position: relative;
}

.kpi-content {
  display: flex;
  flex-direction: column;
}

.kpi-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-value {
  font-size: 1.5rem;
  font-weight: var(--font-weight-bold);
  margin-top: 0.2rem;
}

.kpi-unit {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-normal);
  color: var(--color-text-muted);
}

.kpi-sub {
  font-size: var(--font-size-xs);
  margin-top: 0.25rem;
}

.kpi-icon-wrapper {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  opacity: 0.85;
}

.kpi-icon--primary { background: rgba(37, 99, 235, 0.15); color: #3b82f6; }
.kpi-icon--success { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.kpi-icon--danger { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.kpi-icon--info { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }

.tabs-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.5rem;
  overflow-x: auto;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-muted);
  background: none;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--color-text);
  background-color: var(--color-bg);
}

.tab-btn--active {
  color: var(--color-primary);
  background-color: var(--color-surface);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  font-weight: var(--font-weight-semibold);
}

.sku-badge {
  font-size: 0.75rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-sm);
  color: var(--color-primary);
}

.stock-levels, .stock-limits {
  display: flex;
  flex-direction: column;
  font-size: var(--font-size-xs);
}

.filters-card-compact {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 0.5rem 0.85rem;
}

.filters-row {
  display: flex;
  align-items: center;
}

.filter-select-compact {
  padding: 0.35rem 0.65rem;
  font-size: var(--font-size-xs);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  color: var(--color-text);
  height: 34px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.form-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.form-select {
  padding: 0.5rem 0.8rem;
  font-size: var(--font-size-xs);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  color: var(--color-text);
}
</style>
