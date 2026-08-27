<template>
  <header class="page-header">
    <div class="page-header__titles">
      <nav v-if="breadcrumbs && breadcrumbs.length" class="breadcrumb" aria-label="Fil d'Ariane">
        <span v-for="(crumb, i) in breadcrumbs" :key="i" class="breadcrumb-item">
          <router-link v-if="crumb.path" :to="crumb.path" class="breadcrumb-link">{{ crumb.label }}</router-link>
          <span v-else class="breadcrumb-current">{{ crumb.label }}</span>
          <span v-if="i < breadcrumbs.length - 1" class="breadcrumb-sep" aria-hidden="true">/</span>
        </span>
      </nav>
      <div class="title-with-back">
        <button
          v-if="showBack"
          class="back-btn"
          @click="handleBack"
          title="Retour à la page précédente"
          aria-label="Retour"
        >
          <AppIcon name="arrow-left" size="18" />
        </button>
        <div class="titles-wrapper">
          <h1 class="page-header__title">{{ title }}</h1>
          <p v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</p>
        </div>
      </div>
    </div>
    </div>
    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import AppButton from './AppButton.vue'
import AppIcon from './AppIcon.vue'

const router = useRouter()

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  breadcrumbs: { type: Array, default: () => [] },
  showBack: { type: Boolean, default: false },
  backFallback: { type: String, default: '/' }
})

function handleBack() {
  if (window.history.length > 2) {
    router.back()
  } else {
    router.push(props.backFallback)
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-5);
  border-bottom: 1px solid var(--color-border);
  position: relative;
}

.page-header::before {
  content: '';
  position: absolute;
  left: 0;
  bottom: -1px;
  width: 42px;
  height: 3px;
  border-radius: var(--radius-pill);
  background: var(--color-primary);
}

.page-header__titles {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: var(--space-1);
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.breadcrumb-link {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.breadcrumb-link:hover {
  color: var(--color-primary);
  text-decoration: underline;
}

.breadcrumb-current {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-semibold);
}

.breadcrumb-sep {
  font-size: var(--font-size-xs);
  color: var(--color-border);
}

/* Title */
.page-header__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.page-header__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.5;
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.title-with-back {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
  margin-top: 4px;
}

.back-btn:hover {
  background: var(--color-bg);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.titles-wrapper {
  display: flex;
  flex-direction: column;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
  }
  .page-header__actions {
    width: 100%;
  }
}
</style>
