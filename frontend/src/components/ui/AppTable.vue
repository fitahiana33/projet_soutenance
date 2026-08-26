<template>
  <div class="app-table-wrapper">
    <!-- Toolbar: search + filters + count -->
    <div v-if="title || searchable || $slots.filters" class="table-toolbar">
      <div class="toolbar-left">
        <h3 v-if="title" class="table-title">{{ title }}</h3>
        <span v-if="!loading && items.length >= 0" class="table-count">
          {{ filteredCount !== undefined ? filteredCount : items.length }} résultat{{ (filteredCount !== undefined ? filteredCount : items.length) !== 1 ? 's' : '' }}
        </span>
      </div>
      <div class="toolbar-right">
        <slot name="toolbar" />
        <div v-if="searchable" class="table-search">
          <svg class="search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="8.5" cy="8.5" r="5.5"/><path d="M16 16l-3-3"/>
          </svg>
          <input
            :value="searchValue"
            @input="$emit('update:searchValue', $event.target.value)"
            type="search"
            :placeholder="searchPlaceholder"
            class="search-input"
            aria-label="Rechercher"
          />
        </div>
      </div>
    </div>

    <!-- Filters slot -->
    <div v-if="$slots.filters" class="table-filters">
      <slot name="filters" />
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="table-loading" role="status" aria-label="Chargement en cours">
      <div class="skeleton-rows">
        <div v-for="n in 5" :key="n" class="skeleton-row">
          <div class="skeleton-cell skeleton-cell--wide"></div>
          <div class="skeleton-cell"></div>
          <div class="skeleton-cell skeleton-cell--short"></div>
          <div class="skeleton-cell skeleton-cell--short"></div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="items.length === 0" class="table-empty" role="status">
      <div class="empty-icon">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
          <rect x="8" y="8" width="32" height="32" rx="4" stroke="currentColor" stroke-width="2"/>
          <path d="M16 20h16M16 27h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="empty-title">{{ emptyTitle }}</p>
      <p class="empty-text">{{ emptyText }}</p>
      <slot name="empty-action" />
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="table-error" role="alert">
      <p class="error-text">{{ error }}</p>
      <button @click="$emit('retry')" class="retry-btn">Reessayer</button>
    </div>

    <!-- Table -->
    <div v-else class="table-container">
      <table class="app-table" role="grid">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :style="{ width: col.width }"
              :class="['table-th', { 'sortable': col.sortable }]"
              :aria-sort="sortKey === col.key ? (sortDir === 'asc' ? 'ascending' : 'descending') : undefined"
              @click="col.sortable && handleSort(col.key)"
              scope="col"
            >
              <span class="th-content">
                {{ col.label }}
                <span v-if="col.sortable" class="sort-icon" aria-hidden="true">
                  <svg viewBox="0 0 12 16" fill="currentColor" width="10" height="14">
                    <path v-if="sortKey !== col.key" d="M6 2L2 7h8L6 2zM6 14l4-5H2l4 5z" opacity="0.4"/>
                    <path v-else-if="sortDir === 'asc'" d="M6 2L2 7h8L6 2z"/>
                    <path v-else d="M6 14l4-5H2l4 5z"/>
                  </svg>
                </span>
              </span>
            </th>
            <th v-if="$slots.actions" class="table-th text-right" scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in paginatedItems"
            :key="item.id || item.id_user || item.id_employee || index"
            class="table-row"
          >
            <td v-for="col in columns" :key="col.key" class="table-td">
              <slot :name="`col-${col.key}`" :item="item" :value="item[col.key]">
                {{ item[col.key] !== null && item[col.key] !== undefined ? item[col.key] : '—' }}
              </slot>
            </td>
            <td v-if="$slots.actions" class="table-td text-right actions-cell">
              <slot name="actions" :item="item" :index="index" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && !error && items.length > 0 && paginate" class="table-pagination">
      <span class="pagination-info">
        {{ paginationStart }}–{{ paginationEnd }} sur {{ items.length }}
      </span>
      <div class="pagination-controls">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
          aria-label="Page précédente"
        >‹</button>
        <button
          v-for="p in visiblePages"
          :key="p"
          :class="['page-btn', { 'page-btn--active': p === currentPage }]"
          @click="currentPage = p"
          :aria-label="`Page ${p}`"
          :aria-current="p === currentPage ? 'page' : undefined"
        >{{ p }}</button>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
          aria-label="Page suivante"
        >›</button>
      </div>
      <select
        v-model="pageSize"
        class="page-size-select"
        aria-label="Lignes par page"
      >
        <option v-for="s in [10, 20, 50, 100]" :key="s" :value="s">{{ s }} / page</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  items: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  emptyText: { type: String, default: 'Aucune donnée ne correspond à votre recherche.' },
  emptyTitle: { type: String, default: 'Aucun résultat' },
  title: { type: String, default: '' },
  searchable: { type: Boolean, default: false },
  searchValue: { type: String, default: '' },
  searchPlaceholder: { type: String, default: 'Rechercher...' },
  paginate: { type: Boolean, default: true },
  defaultPageSize: { type: Number, default: 10 },
  filteredCount: { type: Number, default: undefined }
})

const emit = defineEmits(['update:searchValue', 'retry'])

const currentPage = ref(1)
const pageSize = ref(props.defaultPageSize)
const sortKey = ref('')
const sortDir = ref('asc')

watch(() => props.items, () => { currentPage.value = 1 })
watch(() => props.searchValue, () => { currentPage.value = 1 })

function handleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const sortedItems = computed(() => {
  if (!sortKey.value) return props.items
  return [...props.items].sort((a, b) => {
    const va = a[sortKey.value] ?? ''
    const vb = b[sortKey.value] ?? ''
    const cmp = String(va).localeCompare(String(vb), 'fr', { numeric: true })
    return sortDir.value === 'asc' ? cmp : -cmp
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedItems.value.length / pageSize.value)))
const paginationStart = computed(() => (currentPage.value - 1) * pageSize.value + 1)
const paginationEnd = computed(() => Math.min(currentPage.value * pageSize.value, sortedItems.value.length))

const paginatedItems = computed(() => {
  if (!props.paginate) return sortedItems.value
  return sortedItems.value.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = new Set([1, total, cur])
  for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) pages.add(i)
  return Array.from(pages).sort((a, b) => a - b)
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

/* --- Toolbar --- */
.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-4) var(--space-3);
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
}

.table-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  margin: 0;
}

.table-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0.1rem 0.5rem;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* --- Search --- */
.table-search {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 10px;
  width: 14px;
  height: 14px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  padding: 0.45rem 0.75rem 0.45rem 2rem;
  font-size: var(--font-size-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  color: var(--color-text);
  min-width: 220px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

/* --- Filters slot --- */
.table-filters {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg);
}

/* --- Skeleton Loading --- */
.table-loading {
  padding: var(--space-2);
}

.skeleton-rows {
  display: flex;
  flex-direction: column;
}

.skeleton-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.skeleton-cell {
  height: 14px;
  background: linear-gradient(90deg, var(--color-border) 25%, var(--color-bg) 50%, var(--color-border) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  flex: 1;
}

.skeleton-cell--wide { flex: 2; }
.skeleton-cell--short { flex: 0.5; max-width: 80px; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* --- Empty State --- */
.table-empty {
  padding: var(--space-12) var(--space-8);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.empty-icon {
  color: var(--color-text-muted);
  opacity: 0.4;
}

.empty-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  margin: 0;
}

.empty-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
  max-width: 300px;
}

/* --- Error State --- */
.table-error {
  padding: var(--space-8);
  text-align: center;
}

.error-text {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-3);
}

.retry-btn {
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  padding: 0.5rem 1rem;
  font-size: var(--font-size-sm);
  cursor: pointer;
}

/* --- Table Core --- */
.table-container {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.app-table {
  width: 100%;
  border: 1px solid var(--color-border);
  border-collapse: separate;
  border-spacing: 0;
  text-align: left;
  font-size: var(--font-size-sm);
}

.table-th {
  background-color: var(--color-bg);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-semibold);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  border-right: 1px solid var(--color-border);
  white-space: nowrap;
  user-select: none;
}

.table-th.sortable {
  cursor: pointer;
}

.table-th.sortable:hover {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.th-content {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sort-icon {
  opacity: 0.5;
  flex-shrink: 0;
}

.table-td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  border-right: 1px solid var(--color-border);
  color: var(--color-text);
  vertical-align: middle;
}

.table-th:last-child,
.table-td:last-child {
  border-right: none;
}

.table-row:last-child .table-td {
  border-bottom: none;
}

.table-row:hover .table-td {
  background-color: rgba(37, 99, 235, 0.03);
}

.table-row {
  transition: background-color 0.1s ease;
}

.text-right { text-align: right; }
.actions-cell { white-space: nowrap; }

/* --- Pagination --- */
.table-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.pagination-info {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: var(--font-size-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
  font-weight: var(--font-weight-semibold);
}

.page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.page-size-select {
  font-size: var(--font-size-xs);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.3rem 0.5rem;
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
}

@media (max-width: 640px) {
  .table-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .toolbar-right {
    flex-direction: column;
    align-items: stretch;
  }
  .search-input {
    min-width: 0;
    width: 100%;
  }
  .table-pagination {
    flex-direction: column;
    align-items: center;
  }
}
</style>
