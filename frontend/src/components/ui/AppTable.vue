<template>
  <div class="app-table-wrapper">
    <div v-if="loading" class="table-loading">
      <AppSpinner size="lg" text="Chargement des données..." center />
    </div>

    <div v-else-if="items.length === 0" class="table-empty">
      <p class="empty-text">{{ emptyText }}</p>
    </div>

    <div v-else class="table-container">
      <table class="app-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key" :style="{ width: col.width }">
              {{ col.label }}
            </th>
            <th v-if="$slots.actions" class="text-right">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(item, index) in items" :key="item.id || index">
            <td v-for="col in columns" :key="col.key">
              <slot :name="`col-${col.key}`" :item="item" :value="item[col.key]">
                {{ item[col.key] }}
              </slot>
            </td>

            <td v-if="$slots.actions" class="text-right actions-cell">
              <slot name="actions" :item="item" :index="index" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import AppSpinner from './AppSpinner.vue'

defineProps({
  columns: { type: Array, required: true }, // [{ key: 'id', label: 'ID', width: '80px' }]
  items: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Aucune donnée disponible.' }
})
</script>

<style scoped>
.app-table-wrapper {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.table-container {
  width: 100%;
  overflow-x: auto;
}

.app-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: var(--font-size-sm);
}

.app-table th {
  background-color: var(--color-bg);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-semibold);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.app-table td {
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
  vertical-align: middle;
}

.app-table tbody tr:last-child td {
  border-bottom: none;
}

.app-table tbody tr:hover {
  background-color: rgba(245, 247, 251, 0.6);
}

.text-right {
  text-align: right;
}

.actions-cell {
  white-space: nowrap;
}

.table-loading,
.table-empty {
  padding: var(--space-8);
  text-align: center;
}

.empty-text {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}
</style>
