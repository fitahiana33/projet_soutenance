<template>
  <footer class="app-footer">
    <div class="footer-container">
      <span>Smart ERP &copy; {{ currentYear }} — Plateforme d'Intelligence d'Entreprise</span>
      <div class="footer-links">
        <a href="#" target="_blank" rel="noopener">Documentation</a>
        <span class="separator">•</span>
        <a href="#" target="_blank" rel="noopener">Support</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.app-footer {
  background-color: var(--color-footer-bg);
  border-top: 1px solid var(--color-border);
  padding: var(--space-4) var(--space-6);
  font-size: var(--font-size-xs);
  color: var(--color-footer-text);
  margin-top: auto;
}

.footer-container {
  max-width: var(--max-content-width);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
}

.footer-links {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.footer-links a {
  color: var(--color-footer-text);
  transition: color 0.15s ease;
}

.footer-links a:hover {
  color: var(--color-primary);
}

.separator {
  opacity: 0.5;
}
</style>
