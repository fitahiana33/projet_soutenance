<template>
  <AppLayout>
    <PageHeader
      title="Référentiel Produits & Mouvements"
      subtitle="Catalogue centralisé, gestion des prix, références SKU, état et suivi des mouvements de stock"
      showBack
      backFallback="/dashboard"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" @click="handleExportProductsExcel">
          <AppIcon name="file-text" size="16" />
          <span>Exporter Excel</span>
        </AppButton>
        <AppButton variant="secondary" size="sm" @click="openCreateCategoryModal">
          <AppIcon name="plus" size="16" />
          <span>Nouvelle Catégorie</span>
        </AppButton>
        <AppButton variant="primary" size="sm" @click="openCreateProductModal">
          <AppIcon name="plus" size="16" />
          <span>Nouveau Produit</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <!-- Compact Single-Line Filters Bar -->
    <div class="filters-card-compact">
      <div class="filters-row">
        <!-- Search Input -->
        <div class="filter-search-compact">
          <AppIcon name="search" size="15" class="filter-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher par référence SKU, désignation..."
            class="filter-input-compact"
          />
        </div>

        <!-- Filter Selects inline -->
        <div class="filter-group-compact">
          <select v-model="selectedCategory" class="filter-select-compact">
            <option value="">Toutes catégories</option>
            <option v-for="cat in categories" :key="cat.id_category" :value="cat.id_category">
              {{ cat.name }}
            </option>
          </select>

          <select v-model="selectedStatus" class="filter-select-compact">
            <option value="">Tous les états</option>
            <option value="ACTIF">Actif</option>
            <option value="INACTIF">Inactif</option>
            <option value="REAPPRO">Réappro</option>
          </select>

          <select v-model="selectedStockFilter" class="filter-select-compact">
            <option value="">Tous les stocks</option>
            <option value="ok">Stock OK</option>
            <option value="low">Alerte Stock</option>
            <option value="out">Rupture</option>
          </select>

          <button
            type="button"
            class="reset-btn-compact"
            title="Réinitialiser les filtres"
            @click="resetFilters"
          >
            <AppIcon name="refresh" size="14" />
            <span>Réinitialiser</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Products Table -->
    <AppTable
      :columns="columns"
      :items="filteredProducts"
      :loading="loading"
      empty-text="Aucun produit ne correspond à vos critères de recherche."
    >
      <!-- Reference SKU Column -->
      <template #col-reference="{ item }">
        <div class="sku-cell">
          <span class="sku-badge font-mono">{{ item.reference }}</span>
        </div>
      </template>

      <!-- Label & Category Column -->
      <template #col-label="{ item }">
        <div class="product-cell">
          <span class="product-name">{{ item.label }}</span>
          <div class="product-meta">
            <AppBadge
              v-if="item.category || item.categories?.length"
              variant="primary"
              :label="item.categories?.length ? item.categories.map(category => category.name).join(', ') : item.category.name"
            />
            <span v-else class="text-muted text-xs">Sans catégorie</span>
          </div>
        </div>
      </template>

      <!-- Prices & Margin Column -->
      <template #col-price_purchase="{ item }">
        <div class="prices-cell">
          <span class="price-buy">Achat: {{ formatCurrency(item.price_purchase) }}</span>
          <span class="price-sell">Vente: {{ formatCurrency(item.price_sell) }}</span>
          <span class="price-margin font-semibold" :class="getMarginClass(item)">
            Marge: {{ calculateMargin(item) }}%
          </span>
        </div>
      </template>

      <!-- Stock Quantities Column -->
      <template #col-stock_quantity="{ item }">
        <div class="stock-cell">
          <div class="stock-badges">
            <AppBadge
              :variant="getStockBadgeVariant(item)"
              :label="getStockStatusLabel(item)"
            />
          </div>
          <div class="stock-counts">
            <span>Physique: <strong>{{ item.stock_quantity }}</strong></span>
            <span>Disponible: <strong class="color-success">{{ item.stock_available ?? (item.stock_quantity - item.stock_reserved) }}</strong></span>
          </div>
        </div>
      </template>

      <!-- Status Column -->
      <template #col-status="{ value }">
        <AppBadge
          :variant="value === 'ACTIF' ? 'success' : value === 'REAPPRO' ? 'warning' : 'danger'"
          :label="value === 'ACTIF' ? 'Actif' : value === 'REAPPRO' ? 'Réappro' : 'Inactif'"
        />
      </template>

      <!-- Actions Column -->
      <template #actions="{ item }">
        <div class="actions-group">
          <button
            type="button"
            class="icon-btn"
            title="Historique des mouvements"
            @click="openMovementsModal(item)"
          >
            <AppIcon name="clock" size="16" />
          </button>

          <button
            type="button"
            class="icon-btn"
            title="Ajuster le stock"
            @click="openAddMovementModal(item)"
          >
            <AppIcon name="refresh" size="16" />
          </button>

          <button
            type="button"
            class="icon-btn"
            title="Éditer le produit"
            @click="openEditProductModal(item)"
          >
            <AppIcon name="pencil" size="16" />
          </button>

          <button
            type="button"
            class="icon-btn icon-btn--danger"
            title="Supprimer"
            @click="confirmDeleteProduct(item)"
          >
            <AppIcon name="trash" size="16" />
          </button>
        </div>
      </template>
    </AppTable>

    <!-- Modal Create / Edit Product -->
    <AppModal
      v-model="showProductModal"
      :title="editingProduct ? 'Éditer le produit' : 'Créer un nouveau produit'"
      size="md"
    >
      <form @submit.prevent="saveProduct" class="modal-form">
        <AppAlert v-if="modalError" variant="danger" dismissible @dismiss="modalError = ''">
          {{ modalError }}
        </AppAlert>

        <div class="form-row">
          <AppInput
            id="prod-ref"
            v-model="productForm.reference"
            label="Référence SKU *"
            placeholder="ex: PRD-ELE-001"
            required
          />
          <AppInput
            id="prod-label"
            v-model="productForm.label"
            label="Désignation du produit *"
            placeholder="Capteur de température"
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Catégorie</label>
            <div class="category-select" @click.stop>
              <button type="button" class="category-select__trigger" :aria-expanded="showCategoryDropdown" @click="showCategoryDropdown = !showCategoryDropdown">
                <span v-if="!productForm.category_ids.length" class="text-muted">Choisir une ou plusieurs catégories</span>
                <span v-else>{{ selectedCategoryNames }}</span>
                <AppIcon name="chevron-down" size="16" />
              </button>
              <div v-if="showCategoryDropdown" class="category-select__menu" role="listbox" aria-multiselectable="true">
                <label v-for="cat in categories" :key="cat.id_category" class="category-option">
                  <input type="checkbox" :value="cat.id_category" :checked="isCategorySelected(cat.id_category)" @change="toggleCategory(cat.id_category)" />
                  <span>{{ cat.name }}</span>
                </label>
                <p v-if="!categories.length" class="category-option category-option--empty">Aucune catégorie disponible</p>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">État du produit</label>
            <select v-model="productForm.status" class="form-select">
              <option value="ACTIF">Actif</option>
              <option value="REAPPRO">En réapprovisionnement</option>
              <option value="INACTIF">Inactif</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <AppInput
            id="prod-price-purchase"
            v-model.number="productForm.price_purchase"
            type="number"
            step="0.01"
            label="Prix d'achat HT (€)"
          />
          <AppInput
            id="prod-price-sell"
            v-model.number="productForm.price_sell"
            type="number"
            step="0.01"
            label="Prix de vente HT (€)"
          />
        </div>

        <div class="form-row grid-4">
          <AppInput
            id="prod-stock-qty"
            v-model.number="productForm.stock_quantity"
            type="number"
            label="Stock physique initial"
          />
          <AppInput
            id="prod-stock-res"
            v-model.number="productForm.stock_reserved"
            type="number"
            label="Stock réservé"
          />
          <AppInput
            id="prod-stock-min"
            v-model.number="productForm.stock_min"
            type="number"
            label="Seuil min (Alerte)"
          />
          <AppInput
            id="prod-stock-max"
            v-model.number="productForm.stock_max"
            type="number"
            label="Capacité max"
          />
        </div>

        <AppInput
          id="prod-desc"
          v-model="productForm.description"
          label="Description / Fiche technique"
          placeholder="Spécifications techniques et informations complémentaires..."
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showProductModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="savingProduct" @click="saveProduct">
          {{ editingProduct ? 'Mettre à jour' : 'Créer le produit' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Modal Create Category -->
    <AppModal v-model="showCategoryModal" title="Ajouter une nouvelle catégorie" size="sm">
      <form @submit.prevent="saveCategory" class="modal-form">
        <AppAlert v-if="catModalError" variant="danger" dismissible @dismiss="catModalError = ''">
          {{ catModalError }}
        </AppAlert>

        <AppInput
          id="cat-name"
          v-model="categoryForm.name"
          label="Nom de la catégorie *"
          placeholder="ex: Outillage Industriel"
          required
        />
        <AppInput
          id="cat-desc"
          v-model="categoryForm.description"
          label="Description"
          placeholder="Description succincte de la catégorie..."
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showCategoryModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="savingCategory" @click="saveCategory">Créer la catégorie</AppButton>
      </template>
    </AppModal>

    <!-- Modal Stock Movements History Log -->
    <AppModal
      v-model="showMovementsModal"
      :title="`Historique des mouvements — ${selectedProductForMovements?.label}`"
      size="md"
    >
      <div class="movements-header">
        <div class="mvt-stock-summary">
          <span>Stock Physique Actuel : <strong>{{ selectedProductForMovements?.stock_quantity }}</strong></span>
          <span>Stock Disponible Net : <strong class="color-success">{{ selectedProductForMovements?.stock_available }}</strong></span>
        </div>
        <AppButton variant="secondary" size="sm" @click="openAddMovementModal(selectedProductForMovements)">
          <AppIcon name="plus" size="14" />
          <span>Nouveau Mouvement</span>
        </AppButton>
      </div>

      <div class="movements-list">
        <div v-for="mvt in productMovements" :key="mvt.id_movement" class="mvt-item">
          <div :class="['mvt-badge', `mvt-badge--${mvt.movement_type}`]">
            {{ mvt.movement_type }}
          </div>
          <div class="mvt-details">
            <div class="mvt-title">
              <span class="mvt-qty" :class="mvt.movement_type === 'ENTREE' ? 'color-success' : 'color-danger'">
                {{ mvt.movement_type === 'ENTREE' ? '+' : '-' }}{{ Math.abs(mvt.quantity) }} unités
              </span>
              <span v-if="mvt.reference_doc" class="mvt-ref">Ref: {{ mvt.reference_doc }}</span>
            </div>
            <p v-if="mvt.comment" class="mvt-comment">{{ mvt.comment }}</p>
            <span class="mvt-date">{{ formatDate(mvt.created_at) }}</span>
          </div>
        </div>

        <div v-if="productMovements.length === 0" class="text-center text-muted py-4">
          Aucun mouvement de stock enregistré pour ce produit.
        </div>
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="showMovementsModal = false">Fermer</AppButton>
      </template>
    </AppModal>

    <!-- Modal Add Stock Movement -->
    <AppModal
      v-model="showAddMovementModal"
      :title="`Ajustement de stock — ${targetProductForAddMvt?.label}`"
      size="sm"
    >
      <form @submit.prevent="saveStockMovement" class="modal-form">
        <AppAlert v-if="mvtModalError" variant="danger" dismissible @dismiss="mvtModalError = ''">
          {{ mvtModalError }}
        </AppAlert>

        <div class="form-group">
          <label class="form-label">Type de Mouvement *</label>
          <select v-model="movementForm.movement_type" class="form-select">
            <option value="ENTREE">Entrée en stock (+)</option>
            <option value="SORTIE">Sortie de stock (-)</option>
            <option value="AJUSTEMENT">Ajustement d'inventaire</option>
          </select>
        </div>

        <AppInput
          id="mvt-qty"
          v-model.number="movementForm.quantity"
          type="number"
          label="Quantité *"
          placeholder="ex: 10"
          required
        />

        <AppInput
          id="mvt-ref"
          v-model="movementForm.reference_doc"
          label="Référence / N° Document"
          placeholder="ex: BL-2026-0042"
        />

        <AppInput
          id="mvt-comment"
          v-model="movementForm.comment"
          label="Motif / Commentaire"
          placeholder="ex: Réception commande fournisseur"
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showAddMovementModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="savingMvt" @click="saveStockMovement">Enregistrer le mouvement</AppButton>
      </template>
    </AppModal>

    <!-- Modal Confirm Delete Product -->
    <AppModal v-model="showDeleteProductModal" title="Confirmer la suppression" size="sm">
      <p>Êtes-vous sûr de vouloir supprimer le produit <strong>{{ deletingProduct?.label }}</strong> (Ref: {{ deletingProduct?.reference }}) ?</p>
      <template #footer>
        <AppButton variant="ghost" @click="showDeleteProductModal = false">Annuler</AppButton>
        <AppButton variant="danger" :loading="deletingProd" @click="executeDeleteProduct">Supprimer</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import productService from '../../services/productService'
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
import { confirmAction } from '../../utils/actionConfirm'
import { exportToExcel } from '../../utils/excelExport'

const products = ref([])
const categories = ref([])

const searchQuery = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const selectedStockFilter = ref('')

const loading = ref(false)
const savingProduct = ref(false)
const savingCategory = ref(false)
const savingMvt = ref(false)
const deletingProd = ref(false)

const pageError = ref('')
const pageSuccess = ref('')
const modalError = ref('')
const catModalError = ref('')
const mvtModalError = ref('')

const showProductModal = ref(false)
const showCategoryModal = ref(false)
const showMovementsModal = ref(false)
const showAddMovementModal = ref(false)
const showDeleteProductModal = ref(false)
const showCategoryDropdown = ref(false)

const editingProduct = ref(null)
const deletingProduct = ref(null)
const selectedProductForMovements = ref(null)
const targetProductForAddMvt = ref(null)
const productMovements = ref([])

const productForm = ref({
  reference: '',
  label: '',
  description: '',
  category_ids: [],
  price_purchase: 0,
  price_sell: 0,
  status: 'ACTIF',
  stock_quantity: 0,
  stock_reserved: 0,
  stock_min: 5,
  stock_max: 100
})

const selectedCategoryNames = computed(() => {
  const selected = new Set((productForm.value.category_ids || []).map(Number))
  return categories.value
    .filter(category => selected.has(Number(category.id_category)))
    .map(category => category.name)
    .join(', ')
})

const categoryForm = ref({
  name: '',
  description: ''
})

const movementForm = ref({
  movement_type: 'ENTREE',
  quantity: 1,
  reference_doc: '',
  comment: ''
})

const columns = [
  { key: 'reference', label: 'Référence SKU', width: '15%' },
  { key: 'label', label: 'Désignation & Catégorie', width: '25%' },
  { key: 'price_purchase', label: 'Prix & Marges', width: '20%' },
  { key: 'stock_quantity', label: 'Stocks (Physique / Dispo)', width: '22%' },
  { key: 'status', label: 'État', width: '10%' }
]

async function fetchData() {
  loading.value = true
  pageError.value = ''
  try {
    const [prodRes, catRes] = await Promise.all([
      productService.getProducts().catch(() => ({ data: [] })),
      productService.getCategories().catch(() => ({ data: [] }))
    ])
    if (prodRes.data && Array.isArray(prodRes.data)) {
      products.value = prodRes.data
    }
    if (catRes.data && Array.isArray(catRes.data)) {
      categories.value = catRes.data
    }
  } catch (error) {
    pageError.value = 'Erreur lors du chargement des produits ou catégories.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

function handleExportProductsExcel() {
  const cols = [
    { header: 'Référence SKU', key: 'reference' },
    { header: 'Désignation', key: 'label' },
    { header: 'Catégorie', key: 'category_name' },
    { header: 'Prix d\'Achat (€)', key: 'price_purchase' },
    { header: 'Prix de Vente (€)', key: 'price_sell' },
    { header: 'Stock Physique', key: 'stock_quantity' },
    { header: 'Stock Réservé', key: 'stock_reserved' },
    { header: 'Stock Dispo', key: 'stock_available' },
    { header: 'Statut', key: 'status' }
  ]
  exportToExcel('referentiel_produits', 'Catalogue Produits', cols, filteredProducts.value)
}

const filteredProducts = computed(() => {
  return products.value.filter((p) => {
    const q = searchQuery.value.toLowerCase()
    const matchSearch = !q || (p.label && p.label.toLowerCase().includes(q)) || (p.reference && p.reference.toLowerCase().includes(q))
    const categoryIds = p.category_ids || (p.category_id ? [p.category_id] : [])
    const matchCategory = !selectedCategory.value || categoryIds.includes(parseInt(selectedCategory.value))
    const matchStatus = !selectedStatus.value || p.status === selectedStatus.value

    let matchStock = true
    if (selectedStockFilter.value === 'ok') {
      matchStock = p.stock_quantity > p.stock_min
    } else if (selectedStockFilter.value === 'low') {
      matchStock = p.stock_quantity > 0 && p.stock_quantity <= p.stock_min
    } else if (selectedStockFilter.value === 'out') {
      matchStock = p.stock_quantity === 0
    }

    return matchSearch && matchCategory && matchStatus && matchStock
  })
})

function formatCurrency(val) {
  if (val === undefined || val === null) return '0,00 €'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val)
}

function calculateMargin(item) {
  if (!item.price_purchase || item.price_purchase === 0) return 100
  const margin = ((item.price_sell - item.price_purchase) / item.price_purchase) * 100
  return margin.toFixed(1)
}

function getMarginClass(item) {
  const margin = calculateMargin(item)
  return margin >= 30 ? 'color-success' : margin >= 10 ? 'color-warning' : 'color-danger'
}

function getStockBadgeVariant(item) {
  if (item.stock_quantity === 0) return 'danger'
  if (item.stock_quantity <= item.stock_min) return 'warning'
  return 'success'
}

function getStockStatusLabel(item) {
  if (item.stock_quantity === 0) return 'Rupture'
  if (item.stock_quantity <= item.stock_min) return 'Stock Critique'
  return 'Stock OK'
}

function resetFilters() {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedStatus.value = ''
  selectedStockFilter.value = ''
}

function isCategorySelected(categoryId) {
  return (productForm.value.category_ids || []).map(Number).includes(Number(categoryId))
}

function toggleCategory(categoryId) {
  const id = Number(categoryId)
  const selected = new Set((productForm.value.category_ids || []).map(Number))
  if (selected.has(id)) selected.delete(id)
  else selected.add(id)
  productForm.value.category_ids = [...selected]
}

// --- CREATE / EDIT PRODUCT ---

function openCreateProductModal() {
  editingProduct.value = null
  modalError.value = ''
  showCategoryDropdown.value = false
  productForm.value = {
    reference: '',
    label: '',
    description: '',
    category_ids: [],
    price_purchase: 0,
    price_sell: 0,
    status: 'ACTIF',
    stock_quantity: 0,
    stock_reserved: 0,
    stock_min: 5,
    stock_max: 100
  }
  showProductModal.value = true
}

function openEditProductModal(item) {
  editingProduct.value = item
  modalError.value = ''
  showCategoryDropdown.value = false
  productForm.value = {
    reference: item.reference || '',
    label: item.label || '',
    description: item.description || '',
    category_ids: (item.category_ids || (item.category_id ? [item.category_id] : [])).map(Number),
    price_purchase: item.price_purchase || 0,
    price_sell: item.price_sell || 0,
    status: item.status || 'ACTIF',
    stock_quantity: item.stock_quantity || 0,
    stock_reserved: item.stock_reserved || 0,
    stock_min: item.stock_min || 5,
    stock_max: item.stock_max || 100
  }
  showProductModal.value = true
}

async function saveProduct() {
  if (!productForm.value.reference || !productForm.value.label) {
    modalError.value = 'La référence SKU et la désignation sont obligatoires.'
    return
  }

  savingProduct.value = true
  modalError.value = ''

  const payload = {
    ...productForm.value,
    category_ids: (productForm.value.category_ids || []).map(Number),
    price_purchase: Number(productForm.value.price_purchase || 0),
    price_sell: Number(productForm.value.price_sell || 0),
    stock_quantity: Number(productForm.value.stock_quantity || 0),
    stock_reserved: Number(productForm.value.stock_reserved || 0),
    stock_min: Number(productForm.value.stock_min || 0),
    stock_max: Number(productForm.value.stock_max || 100)
  }

  try {
    if (editingProduct.value) {
      await productService.updateProduct(editingProduct.value.id_product, payload)
      pageSuccess.value = 'Produit mis à jour avec succès !'
    } else {
      await productService.createProduct(payload)
      pageSuccess.value = 'Nouveau produit créé avec succès !'
    }

    showProductModal.value = false
    await fetchData()
  } catch (error) {
    modalError.value = error?.response?.data?.detail?.[0]?.msg || error?.response?.data?.detail || 'Erreur lors de l\'enregistrement du produit.'
  } finally {
    savingProduct.value = false
  }
}

// --- CREATE CATEGORY ---

function openCreateCategoryModal() {
  catModalError.value = ''
  categoryForm.value = { name: '', description: '' }
  showCategoryModal.value = true
}

async function saveCategory() {
  if (!categoryForm.value.name) {
    catModalError.value = 'Le nom de la catégorie est obligatoire.'
    return
  }

  savingCategory.value = true
  catModalError.value = ''

  try {
    await productService.createCategory(categoryForm.value)
    pageSuccess.value = 'Catégorie créée avec succès !'
    showCategoryModal.value = false
    await fetchData()
  } catch (error) {
    catModalError.value = 'Erreur lors de la création de la catégorie.'
  } finally {
    savingCategory.value = false
  }
}

// --- MOVEMENTS LOG & ADJUSTMENT ---

async function openMovementsModal(item) {
  selectedProductForMovements.value = item
  productMovements.value = []
  showMovementsModal.value = true
  try {
    const res = await productService.getProductMovements(item.id_product)
    if (res.data) productMovements.value = res.data
  } catch (error) {
    // Error handling
  }
}

function openAddMovementModal(item) {
  targetProductForAddMvt.value = item
  mvtModalError.value = ''
  movementForm.value = {
    movement_type: 'ENTREE',
    quantity: 1,
    reference_doc: '',
    comment: ''
  }
  showAddMovementModal.value = true
}

async function saveStockMovement() {
  if (!movementForm.value.quantity || movementForm.value.quantity === 0) {
    mvtModalError.value = 'Veuillez saisir une quantité non nulle.'
    return
  }
  if (!confirmAction('Confirmer ce mouvement de stock ? La quantité sera modifiée.')) return

  savingMvt.value = true
  mvtModalError.value = ''

  try {
    await productService.createProductMovement(targetProductForAddMvt.value.id_product, movementForm.value)
    pageSuccess.value = 'Mouvement de stock enregistré avec succès !'
    showAddMovementModal.value = false
    await fetchData()
  } catch (error) {
    mvtModalError.value = 'Erreur lors de l\'enregistrement du mouvement.'
  } finally {
    savingMvt.value = false
  }
}

// --- DELETE PRODUCT ---

function confirmDeleteProduct(item) {
  deletingProduct.value = item
  showDeleteProductModal.value = true
}

async function executeDeleteProduct() {
  if (!deletingProduct.value) return
  deletingProd.value = true
  try {
    await api.delete(`/products/${deletingProduct.value.id_product}`)
    pageSuccess.value = 'Produit supprimé avec succès !'
    showDeleteProductModal.value = false
    await fetchData()
  } catch (error) {
    pageError.value = 'Erreur lors de la suppression du produit.'
  } finally {
    deletingProd.value = false
  }
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  try {
    return new Date(isoStr).toLocaleString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    })
  } catch (e) {
    return isoStr
  }
}
</script>

<style scoped>
.filters-card-compact {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 0.5rem 0.85rem;
  margin-bottom: var(--space-4);
}

.filters-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
}

.filter-search-compact {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 220px;
}

.filter-icon {
  position: absolute;
  left: 10px;
  color: var(--color-text-muted);
}

.filter-input-compact {
  width: 100%;
  padding: 0.4rem 0.75rem 0.4rem 2.1rem;
  font-size: var(--font-size-xs);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  color: var(--color-text);
  height: 34px;
  outline: none;
  transition: border-color 0.15s ease;
}

.filter-input-compact:focus {
  border-color: var(--color-primary);
}

.filter-group-compact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.filter-select-compact {
  padding: 0.35rem 0.65rem;
  font-size: var(--font-size-xs);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  color: var(--color-text);
  height: 34px;
  cursor: pointer;
  outline: none;
}

.filter-select-compact:focus {
  border-color: var(--color-primary);
}

.reset-btn-compact {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.65rem;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  height: 34px;
  transition: all 0.15s ease;
}

.reset-btn-compact:hover {
  background-color: var(--color-bg);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.sku-badge {
  font-size: 0.75rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-sm);
  color: var(--color-primary);
}

.product-cell {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.product-meta {
  margin-top: 2px;
}

.prices-cell {
  display: flex;
  flex-direction: column;
  font-size: var(--font-size-xs);
}

.price-buy { color: var(--color-text-muted); }
.price-sell { font-weight: var(--font-weight-semibold); }
.price-margin { margin-top: 2px; }

.stock-cell {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stock-counts {
  display: flex;
  flex-direction: column;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
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

.grid-4 {
  grid-template-columns: repeat(4, 1fr);
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

.category-select {
  position: relative;
  width: 100%;
}

.category-select__trigger {
  width: 100%;
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
}

.category-select__trigger:hover,
.category-select__trigger:focus-visible {
  border-color: var(--color-primary);
}

.category-select__menu {
  position: absolute;
  z-index: 20;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  max-height: 220px;
  overflow-y: auto;
  padding: var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-md);
}

.category-option {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 40px;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  cursor: pointer;
}

.category-option:hover {
  background: var(--color-primary-light);
}

.category-option input {
  width: 17px;
  height: 17px;
  accent-color: var(--color-primary);
}

.category-option--empty {
  color: var(--color-text-muted);
  cursor: default;
}

.form-help {
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

.movements-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.mvt-stock-summary {
  display: flex;
  gap: var(--space-4);
  font-size: var(--font-size-sm);
}

.movements-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  max-height: 280px;
  overflow-y: auto;
}

.mvt-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
}

.mvt-badge {
  font-size: 0.65rem;
  font-weight: bold;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}

.mvt-badge--ENTREE { background: var(--color-success-light); color: var(--color-success); }
.mvt-badge--SORTIE { background: var(--color-danger-light); color: var(--color-danger); }
.mvt-badge--AJUSTEMENT { background: var(--color-warning-light); color: var(--color-warning); }

.mvt-details { flex: 1; }

.mvt-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--font-size-sm);
}

.mvt-qty { font-weight: bold; }
.mvt-ref { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.mvt-comment { font-size: var(--font-size-xs); margin: 2px 0 0; color: var(--color-text); }
.mvt-date { font-size: 0.7rem; color: var(--color-text-muted); opacity: 0.8; }

.color-success { color: var(--color-success); }
.color-warning { color: var(--color-warning); }
.color-danger { color: var(--color-danger); }
.font-mono { font-family: monospace; }
.font-semibold { font-weight: var(--font-weight-semibold); }
.text-muted { color: var(--color-text-muted); }
.text-xs { font-size: var(--font-size-xs); }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }
</style>
