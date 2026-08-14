<template>
  <div :class="['spinner-container', { 'spinner-container--center': center }]">
    <div :class="['spinner', `spinner--${size}`]" role="status">
      <span class="sr-only">Chargement...</span>
    </div>
    <span v-if="text" class="spinner-text">{{ text }}</span>
  </div>
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (val) => ['sm', 'md', 'lg'].includes(val)
  },
  text: { type: String, default: '' },
  center: { type: Boolean, default: false }
})
</script>

<style scoped>
.spinner-container {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
}

.spinner-container--center {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: var(--space-6);
}

.spinner {
  border: 3px solid rgba(37, 99, 235, 0.15);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner--sm {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

.spinner--md {
  width: 28px;
  height: 28px;
  border-width: 3px;
}

.spinner--lg {
  width: 44px;
  height: 44px;
  border-width: 4px;
}

.spinner-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
