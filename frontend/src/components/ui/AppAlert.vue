<template>
  <div v-if="visible" :class="['alert', `alert--${variant}`]" role="alert">
    <div class="alert__content">
      <slot>{{ message }}</slot>
    </div>
    <button
      v-if="dismissible"
      type="button"
      class="alert__close"
      aria-label="Fermer"
      @click="dismiss"
    >
      &times;
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  message: { type: String, default: '' },
  variant: {
    type: String,
    default: 'info',
    validator: (val) => ['info', 'success', 'warning', 'danger'].includes(val)
  },
  dismissible: { type: Boolean, default: false }
})

const emit = defineEmits(['dismiss'])
const visible = ref(true)

function dismiss() {
  visible.value = false
  emit('dismiss')
}
</script>

<style scoped>
.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  line-height: 1.4;
  border: 1px solid transparent;
}

.alert--info {
  background-color: var(--color-primary-light);
  color: var(--color-primary-hover);
  border-color: rgba(37, 99, 235, 0.2);
}

.alert--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border-color: rgba(5, 150, 105, 0.2);
}

.alert--warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
  border-color: rgba(217, 119, 6, 0.2);
}

.alert--danger {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
  border-color: rgba(220, 38, 38, 0.2);
}

.alert__content {
  flex: 1;
}

.alert__close {
  background: none;
  border: none;
  font-size: 1.25rem;
  line-height: 1;
  color: inherit;
  cursor: pointer;
  padding: 0;
  opacity: 0.7;
  transition: opacity 0.15s ease;
}

.alert__close:hover {
  opacity: 1;
}
</style>
