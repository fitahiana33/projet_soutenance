<template>
  <main class="login-page">
    <div class="login-container">
      <AppCard class="login-card" flat>
        <template #header>
          <div class="login-card__header">
            <h1 class="login-title">Connexion</h1>
            <p class="login-subtitle">Smart ERP Intelligent</p>
          </div>
        </template>

        <form @submit.prevent="handleSubmit" novalidate class="login-form">
          <AppAlert
            v-if="error"
            variant="danger"
            dismissible
            class="login-alert"
            @dismiss="error = ''"
          >
            {{ error }}
          </AppAlert>

          <AppInput
            id="email"
            v-model="email"
            type="email"
            label="Adresse Email"
            placeholder="admin@erp.com"
            required
            :disabled="loading"
          />

          <AppInput
            id="password"
            v-model="password"
            type="password"
            label="Mot de passe"
            placeholder="Admin@123"
            required
            :disabled="loading"
          />

          <AppButton
            type="submit"
            variant="primary"
            size="lg"
            block
            :loading="loading"
          >
            Se connecter
          </AppButton>
        </form>
      </AppCard>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import AppCard from '../../components/ui/AppCard.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Valeurs de connexion d'administration réelles générées par le seed backend
const email = ref('admin@erp.com')
const password = ref('Admin@123')
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!email.value || !password.value) {
    error.value = 'Veuillez renseigner votre email et votre mot de passe.'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const result = await authStore.login(email.value, password.value)

    if (result.success) {
      const redirect = route.query.redirect || '/dashboard'
      router.push(redirect)
    } else {
      error.value = result.message || 'Identifiants invalides.'
    }
  } catch (err) {
    error.value = 'Erreur de connexion au serveur.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background-color: var(--color-bg);
  padding: var(--space-4);
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-card {
  padding: var(--space-4);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.login-card__header {
  text-align: center;
  width: 100%;
  padding-bottom: var(--space-2);
}

.login-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  margin: 0;
}

.login-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.login-alert {
  margin-bottom: var(--space-2);
}
</style>
