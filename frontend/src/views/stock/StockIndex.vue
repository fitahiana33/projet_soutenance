<template>
  <AppLayout>
    <PageHeader
      title="Gestion de Stock & Inventaire"
      subtitle="Suivi des références articles, mouvements d'entrepôt et réapprovisionnements"
    >
      <template #actions>
        <AppButton variant="primary" size="sm" @click="showStockModal = true">
          <AppIcon name="plus" size="16" />
          <span>Nouvel Article</span>
        </AppButton>
      </template>
    </PageHeader>

    <!-- KPI Summary -->
    <div class="stock-kpis">
      <AppCard class="stock-kpi-card">
        <span class="kpi-lbl">Total Références</span>
        <span class="kpi-num">1,450</span>
        <span class="kpi-sub text-success">Catalogues à jour</span>
      </AppCard>

      <AppCard class="stock-kpi-card">
        <span class="kpi-lbl">Alertes Stock Faible</span>
        <span class="kpi-num text-warning">8</span>
        <span class="kpi-sub text-warning">Réapprovisionnement requis</span>
      </AppCard>

      <AppCard class="stock-kpi-card">
        <span class="kpi-lbl">Entrepôts Actifs</span>
        <span class="kpi-num">3</span>
        <span class="kpi-sub">Paris, Lyon, Marseille</span>
      </AppCard>

      <AppCard class="stock-kpi-card">
        <span class="kpi-lbl">Valeur de l'Inventaire</span>
        <span class="kpi-num">€ 284,500</span>
        <span class="kpi-sub text-success">+4.5% ce mois</span>
      </AppCard>
    </div>

    <!-- Inventory Table -->
    <AppTable
      :columns="columns"
      :items="products"
      empty-text="Aucun article disponible."
    >
      <template #col-sku="{ value }">
        <span class="sku-tag">{{ value }}</span>
      </template>

      <template #col-status="{ item }">
        <AppBadge
          :variant="item.qty === 0 ? 'danger' : item.qty <= item.minQty ? 'warning' : 'success'"
          :label="item.qty === 0 ? 'Rupture' : item.qty <= item.minQty ? 'Stock Faible' : 'En Stock'"
        />
      </template>

      <template #actions="{ item }">
        <div class="actions-flex">
          <AppButton variant="secondary" size="sm" @click="adjustStock(item)">
            <span>Ajuster</span>
          </AppButton>
        </div>
      </template>
    </AppTable>

    <!-- Product Modal -->
    <AppModal v-model="showStockModal" title="Créer une référence produit" size="md">
      <div class="form-grid">
        <AppInput id="prod-sku" v-model="prodForm.sku" label="Code SKU" placeholder="PRD-0098" required />
        <AppInput id="prod-name" v-model="prodForm.name" label="Désignation de l'article" placeholder="Écran Pro 27 Pulses" required />
        <AppInput id="prod-category" v-model="prodForm.category" label="Catégorie" placeholder="Informatique & Périphériques" required />
        <div class="form-row">
          <AppInput id="prod-qty" v-model.number="prodForm.qty" type="number" label="Quantité initiale" placeholder="50" required />
          <AppInput id="prod-min" v-model.number="prodForm.minQty" type="number" label="Seuil d'alerte" placeholder="10" required />
        </div>
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="showStockModal = false">Annuler</AppButton>
        <AppButton variant="primary" @click="saveProduct">Créer la référence</AppButton>
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

const showStockModal = ref(false)

const prodForm = ref({
  sku: '',
  name: '',
  category: 'Informatique',
  qty: 25,
  minQty: 5
})

const columns = [
  { key: 'sku', label: 'SKU / Code', width: '15%' },
  { key: 'name', label: 'Désignation Article', width: '35%' },
  { key: 'category', label: 'Catégorie', width: '20%' },
  { key: 'qty', label: 'Quantité', width: '15%' },
  { key: 'status', label: 'Statut', width: '15%' }
]

const products = ref([
  { id: 1, sku: 'PRD-0102', name: 'Ordinateur Portable Business 15"', category: 'Informatique', qty: 18, minQty: 5 },
  { id: 2, sku: 'PRD-0908', name: 'Écran UltraWide 34"', category: 'Périphériques', qty: 2, minQty: 5 },
  { id: 3, sku: 'PRD-0441', name: 'Clavier Mécanique Sans Fil', category: 'Accessoires', qty: 45, minQty: 10 },
  { id: 4, sku: 'PRD-0711', name: 'Serveur Rack 2U Enterprise', category: 'Infrastructures', qty: 0, minQty: 2 }
])

function saveProduct() {
  products.value.unshift({
    id: Date.now(),
    sku: prodForm.value.sku,
    name: prodForm.value.name,
    category: prodForm.value.category,
    qty: prodForm.value.qty,
    minQty: prodForm.value.minQty
  })
  showStockModal.value = false
  prodForm.value = { sku: '', name: '', category: 'Informatique', qty: 25, minQty: 5 }
}

function adjustStock(item) {
  const newQty = prompt(`Entrez la nouvelle quantité en stock pour ${item.name} :`, item.qty)
  if (newQty !== null && !isNaN(newQty)) {
    item.qty = parseInt(newQty, 10)
  }
}
</script>

<style scoped>
.stock-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.stock-kpi-card {
  display: flex;
  flex-direction: column;
}

.kpi-lbl {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.kpi-num {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  margin: var(--space-1) 0;
}

.kpi-sub {
  font-size: var(--font-size-xs);
}

.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }

.sku-tag {
  font-family: monospace;
  font-size: 0.8rem;
  background-color: var(--color-bg);
  padding: 0.15rem 0.45rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  font-weight: var(--font-weight-semibold);
}

.actions-flex {
  display: flex;
  justify-content: flex-end;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}
</style>
