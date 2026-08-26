<template>
  <div class="app-layout">
    <AppHeader @toggle-sidebar="toggleSidebar" />
    <div class="app-body">
      <AppSidebar :collapsed="sidebarCollapsed" />
      <main class="app-content">
        <div class="container-xl">
          <slot />
        </div>
      </main>
    </div>
    <AppFooter />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from '../components/layout/AppHeader.vue'
import AppSidebar from '../components/layout/AppSidebar.vue'
import AppFooter from '../components/layout/AppFooter.vue'

const sidebarCollapsed = ref(false)

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg);
}

.app-body {
  display: flex;
  flex: 1;
  min-width: 0;
}

.app-content {
  flex: 1;
  padding: var(--space-6);
  max-width: 100%;
  overflow-x: auto;
  min-width: 0;
}

@media (max-width: 768px) {
  .app-content {
    padding: var(--space-4);
  }
}
</style>
