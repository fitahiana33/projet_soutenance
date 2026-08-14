<template>
  <div :class="['form-group', { 'form-group--error': !!error }]">
    <label v-if="label" :for="id" class="form-label">
      {{ label }}
      <span v-if="required" class="form-label__required" aria-hidden="true">*</span>
    </label>

    <div class="input-wrapper">
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${id}-error` : helperText ? `${id}-helper` : undefined"
        class="form-input"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      />
    </div>

    <p v-if="error" :id="`${id}-error`" class="form-feedback form-feedback--error" role="alert">
      {{ error }}
    </p>
    <p v-else-if="helperText" :id="`${id}-helper`" class="form-feedback form-feedback--helper">
      {{ helperText }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  id: { type: String, default: () => `input-${Math.random().toString(36).substring(2, 9)}` },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  error: { type: String, default: '' },
  helperText: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'blur', 'focus'])
</script>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  width: 100%;
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.form-label__required {
  color: var(--color-danger);
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  color: var(--color-text);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.form-input:disabled {
  background-color: var(--color-bg);
  cursor: not-allowed;
  opacity: 0.7;
}

.form-group--error .form-input {
  border-color: var(--color-danger);
}

.form-group--error .form-input:focus {
  box-shadow: 0 0 0 3px var(--color-danger-light);
}

.form-feedback {
  font-size: var(--font-size-xs);
  margin-top: var(--space-1);
}

.form-feedback--error {
  color: var(--color-danger);
}

.form-feedback--helper {
  color: var(--color-text-muted);
}
</style>
