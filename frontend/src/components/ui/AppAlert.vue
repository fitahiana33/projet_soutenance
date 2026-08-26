<template>
  <div :class="['app-alert', `app-alert--${variant}`, { 'app-alert--dismissible': dismissible }]" role="alert">
    <div class="alert-icon" aria-hidden="true">
      <svg v-if="variant === 'danger' || variant === 'error'" viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd"/>
      </svg>
      <svg v-else-if="variant === 'success'" viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd"/>
      </svg>
      <svg v-else-if="variant === 'warning'" viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
        <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
      </svg>
      <svg v-else viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd"/>
      </svg>
    </div>

    <div class="alert-content">
      <p v-if="title" class="alert-title">{{ title }}</p>
      <div class="alert-body"><slot /></div>
    </div>

    <button
      v-if="dismissible"
      type="button"
      class="alert-dismiss"
      @click="$emit('dismiss')"
      aria-label="Fermer"
    >
      <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
        <path d="M4.22 4.22a.75.75 0 011.06 0L8 6.94l2.72-2.72a.75.75 0 111.06 1.06L9.06 8l2.72 2.72a.75.75 0 11-1.06 1.06L8 9.06l-2.72 2.72a.75.75 0 01-1.06-1.06L6.94 8 4.22 5.28a.75.75 0 010-1.06z"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'info', validator: v => ['info', 'success', 'warning', 'danger', 'error'].includes(v) },
  title: { type: String, default: '' },
  dismissible: { type: Boolean, default: false }
})
defineEmits(['dismiss'])
</script>

<style scoped>
.app-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border-left: 4px solid;
  margin-bottom: var(--space-4);
  font-size: var(--font-size-sm);
}

.app-alert--info {
  background-color: rgba(37, 99, 235, 0.08);
  border-color: var(--color-primary);
  color: var(--color-text);
}
.app-alert--info .alert-icon { color: var(--color-primary); }

.app-alert--success {
  background-color: rgba(16, 185, 129, 0.08);
  border-color: var(--color-success);
  color: var(--color-text);
}
.app-alert--success .alert-icon { color: var(--color-success); }

.app-alert--warning {
  background-color: rgba(245, 158, 11, 0.08);
  border-color: #f59e0b;
  color: var(--color-text);
}
.app-alert--warning .alert-icon { color: #f59e0b; }

.app-alert--danger, .app-alert--error {
  background-color: rgba(239, 68, 68, 0.08);
  border-color: var(--color-danger);
  color: var(--color-text);
}
.app-alert--danger .alert-icon, .app-alert--error .alert-icon { color: var(--color-danger); }

.alert-icon {
  flex-shrink: 0;
  margin-top: 1px;
}

.alert-content {
  flex: 1;
  line-height: 1.5;
}

.alert-title {
  font-weight: var(--font-weight-semibold);
  margin: 0 0 2px;
}

.alert-body {
  color: var(--color-text-muted);
}

.alert-dismiss {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  color: var(--color-text-muted);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  transition: color 0.15s ease;
  flex-shrink: 0;
}

.alert-dismiss:hover {
  color: var(--color-text);
}
</style>
