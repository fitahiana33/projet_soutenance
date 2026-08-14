<template>
  <span :class="['badge', `badge--${variant}`]">
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup>
defineProps({
  label: { type: String, default: '' },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(value)
  }
})
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  line-height: 1.4;
  white-space: nowrap;
}

.badge--default {
  background-color: var(--color-bg);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}

.badge--primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.badge--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.badge--warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.badge--danger {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

.badge--info {
  background-color: var(--color-primary-light);
  color: var(--color-primary-hover);
}
</style>
