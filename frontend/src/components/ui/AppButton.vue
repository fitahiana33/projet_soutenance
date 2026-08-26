<template>
  <component
    :is="componentTag"
    :class="classes"
    :type="nativeType"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="btn__spinner" aria-hidden="true"></span>
    <slot>{{ label }}</slot>
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, default: '' },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) =>
      ['primary', 'secondary', 'success', 'danger', 'warning', 'ghost'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg'].includes(value)
  },
  to: { type: [String, Object], default: null },
  type: { type: String, default: 'button' },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false }
})

const emit = defineEmits(['click'])

const componentTag = computed(() => (props.to ? 'router-link' : 'button'))
const nativeType = computed(() => (props.to ? undefined : props.type))

const classes = computed(() => ({
  btn: true,
  [`btn--${props.variant}`]: true,
  [`btn--${props.size}`]: true,
  'btn--block': props.block,
  'btn--loading': props.loading
}))

function handleClick(event) {
  if (props.disabled || props.loading) {
    event.preventDefault()
    return
  }
  emit('click', event)
}
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
  line-height: 1;
  transition: background-color 0.15s ease, border-color 0.15s ease, opacity 0.15s ease;
  text-decoration: none;
  min-height: 40px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--xs {
  padding: 0.25rem 0.5rem;
  font-size: var(--font-size-xs);
  min-height: 32px;
}

.btn--sm {
  padding: var(--space-2) var(--space-3);
  font-size: var(--font-size-sm);
  min-height: 36px;
}

.btn--md {
  padding: var(--space-3) var(--space-5);
  font-size: var(--font-size-base);
}

.btn--lg {
  padding: var(--space-4) var(--space-6);
  font-size: var(--font-size-lg);
}

.btn--block {
  width: 100%;
}

.btn--primary {
  background-color: var(--color-primary);
  color: #fff;
}

.btn--primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.btn--secondary {
  background-color: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text);
}

.btn--secondary:hover:not(:disabled) {
  background-color: var(--color-bg);
}

.btn--success {
  background-color: var(--color-success);
  color: #fff;
}

.btn--success:hover:not(:disabled) {
  opacity: 0.9;
}

.btn--danger {
  background-color: var(--color-danger);
  color: #fff;
}

.btn--danger:hover:not(:disabled) {
  background-color: var(--color-danger-hover);
}

.btn--warning {
  background-color: var(--color-warning);
  color: #fff;
}

.btn--warning:hover:not(:disabled) {
  opacity: 0.9;
}

.btn--ghost {
  background-color: transparent;
  color: var(--color-primary);
}

.btn--ghost:hover:not(:disabled) {
  background-color: var(--color-primary-light);
}

.btn__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: btn-spin 0.7s linear infinite;
}

.btn--secondary .btn__spinner,
.btn--ghost .btn__spinner {
  border-color: rgba(17, 24, 39, 0.2);
  border-top-color: var(--color-text);
}

@keyframes btn-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
