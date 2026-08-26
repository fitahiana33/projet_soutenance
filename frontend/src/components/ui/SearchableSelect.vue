<template>
  <div ref="root" class="searchable-select">
    <label v-if="label" class="form-label" :for="id">{{ label }}<span v-if="required" class="form-label__required">*</span></label>
    <button :id="id" type="button" class="searchable-select__trigger" :disabled="disabled" @click="open = !open">
      <span :class="{ 'is-placeholder': !selected }">{{ selected ? getLabel(selected) : placeholder }}</span>
      <AppIcon name="chevron-down" size="14" />
    </button>
    <div v-if="open" class="searchable-select__menu">
      <input ref="searchInput" v-model="query" class="searchable-select__search" type="search" :placeholder="searchPlaceholder" @keydown.esc="close" />
      <button v-if="clearable && modelValue != null && modelValue !== ''" type="button" class="searchable-select__option searchable-select__clear" @click="select(null)">Réinitialiser</button>
      <button v-for="option in filteredOptions" :key="String(option[valueKey])" type="button" class="searchable-select__option" :class="{ selected: String(option[valueKey]) === String(modelValue) }" @click="select(option[valueKey])">
        {{ getLabel(option) }}
      </button>
      <p v-if="filteredOptions.length === 0" class="searchable-select__empty">Aucun résultat</p>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  modelValue: { type: [String, Number, null], default: null },
  options: { type: Array, default: () => [] },
  label: { type: String, default: '' },
  placeholder: { type: String, default: 'Sélectionner...' },
  searchPlaceholder: { type: String, default: 'Rechercher par mot-clé...' },
  valueKey: { type: String, default: 'value' },
  labelKey: { type: String, default: 'label' },
  searchKeys: { type: Array, default: () => [] },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
  id: { type: String, default: () => `search-select-${Math.random().toString(36).slice(2)}` }
})
const emit = defineEmits(['update:modelValue', 'change'])
const root = ref(null)
const searchInput = ref(null)
const open = ref(false)
const query = ref('')
const getLabel = option => typeof option === 'string' ? option : String(option?.[props.labelKey] ?? option?.label ?? option?.name ?? '')
const getSearchText = option => [getLabel(option), ...props.searchKeys.map(key => option?.[key])].filter(Boolean).join(' ').toLowerCase()
const selected = computed(() => props.options.find(option => String(option[props.valueKey]) === String(props.modelValue)))
const filteredOptions = computed(() => {
  const term = query.value.trim().toLowerCase()
  return term ? props.options.filter(option => getSearchText(option).includes(term)) : props.options
})
function select(value) { emit('update:modelValue', value); emit('change', value); close() }
function close() { open.value = false; query.value = '' }
function onDocumentClick(event) { if (root.value && !root.value.contains(event.target)) close() }
watch(open, value => { if (value) nextTick(() => searchInput.value?.focus()) })
document.addEventListener('click', onDocumentClick)
onBeforeUnmount(() => document.removeEventListener('click', onDocumentClick))
</script>

<style scoped>
.searchable-select { position: relative; width: 100%; }
.searchable-select__trigger { width: 100%; min-height: 40px; display: flex; align-items: center; justify-content: space-between; gap: .5rem; padding: .65rem .8rem; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); color: var(--color-text); text-align: left; cursor: pointer; }
.searchable-select__trigger:focus { outline: 2px solid var(--color-primary); outline-offset: 1px; }
.is-placeholder { color: var(--color-text-muted); }
.searchable-select__menu { position: absolute; z-index: 30; top: calc(100% + 4px); left: 0; right: 0; max-height: 280px; overflow-y: auto; padding: .4rem; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); box-shadow: var(--shadow-lg); }
.searchable-select__search { width: 100%; margin-bottom: .35rem; padding: .6rem .7rem; border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-bg); color: var(--color-text); }
.searchable-select__option { display: block; width: 100%; padding: .55rem .65rem; border: 0; border-radius: var(--radius-sm); background: transparent; color: var(--color-text); text-align: left; cursor: pointer; }
.searchable-select__option:hover, .searchable-select__option.selected { background: var(--color-primary-light); color: var(--color-primary); }
.searchable-select__clear { color: var(--color-danger); border-bottom: 1px solid var(--color-border); }
.searchable-select__empty { padding: .7rem; color: var(--color-text-muted); text-align: center; }
</style>
