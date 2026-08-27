<template>
  <div class="forbidden-page">
    <div class="forbidden-card text-center">
      <div class="icon-circle mb-4">
        <AppIcon name="shield" size="48" class="text-rose-500" />
      </div>
      <h1 class="text-2xl font-bold text-white mb-2">Accès Refusé (403 Forbidden)</h1>
      <p class="text-slate-400 text-sm max-w-md mx-auto mb-6">
        Vous ne possédez pas les habilitations ou privilèges nécessaires (RBAC) pour accéder à cette fonctionnalité. 
        Veuillez contacter votre Administrateur Système si vous pensez qu'il s'agit d'une erreur.
      </p>
      <div class="flex justify-center gap-3">
        <AppButton variant="secondary" @click="goBack">
          <AppIcon name="arrow-left" size="16" />
          <span>Retour</span>
        </AppButton>
        <AppButton variant="primary" @click="goToAllowedPage">
          <AppIcon name="dashboard" size="16" />
          <span>Accéder à mon espace</span>
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import AppIcon from '../../components/ui/AppIcon.vue'
import AppButton from '../../components/ui/AppButton.vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { getFirstAllowedPath } from '../../utils/access'

const router = useRouter()
const authStore = useAuthStore()

function goBack() {
  if (window.history.length > 2) {
    router.back()
  } else {
    goToAllowedPage()
  }
}

function goToAllowedPage() {
  router.push(getFirstAllowedPath(authStore.currentUser))
}
</script>

<style scoped>
.forbidden-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #090d16;
  padding: 1.5rem;
}

.forbidden-card {
  background-color: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  max-width: 500px;
  width: 100%;
}

.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: rgba(244, 63, 94, 0.1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
