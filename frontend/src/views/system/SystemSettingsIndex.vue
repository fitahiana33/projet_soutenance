<template>
  <AppLayout>
    <PageHeader
      title="Réinitialisation des Données"
      subtitle="Purge et remise à zéro intégrale des données métiers Dolibarr & PostgreSQL"
    />

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <AppCard class="mb-6">
      <div class="p-6">
        <h3 class="text-lg font-bold mb-4 flex items-center gap-2 color-primary">
          <AppIcon name="shield" size="22" />
          <span>Périmètre de Réinitialisation</span>
        </h3>

        <div class="reset-scope-grid">
          <div class="scope-box scope-box--danger">
            <h4 class="font-bold color-danger mb-3 flex items-center gap-2">
              <AppIcon name="trash" size="18" />
              <span>Données Réinitialisées & Purgées</span>
            </h4>
            <ul class="scope-list">
              <li><strong>Produits & Catégories</strong> (Dolibarr REST API)</li>
              <li><strong>Tiers & Fournisseurs</strong> (Dolibarr REST API)</li>
              <li><strong>Workflow Achats</strong> (Demandes, Commandes, Réceptions, Factures)</li>
              <li><strong>Ressources Humaines</strong> (Employés, Congés, Paie, Évaluations)</li>
              <li><strong>Stocks & Traçabilité</strong> (Mouvements & Lots temporaires)</li>
              <li><strong>Comptes secondaires</strong> (Utilisateurs secondaires PostgreSQL)</li>
            </ul>
          </div>

          <div class="scope-box scope-box--success">
            <h4 class="font-bold color-success mb-3 flex items-center gap-2">
              <AppIcon name="shield" size="18" />
              <span>Données Conservées & Sécurisées</span>
            </h4>
            <ul class="scope-list">
              <li><strong>Compte Administrateur</strong> (<code>admin@erp.com</code>)</li>
              <li><strong>Rôles système par défaut</strong> (8 rôles système)</li>
              <li><strong>Permissions & Matrice de sécurité</strong> (Contrôle d'accès RBAC)</li>
              <li><strong>Configuration du serveur Dolibarr</strong></li>
            </ul>
          </div>
        </div>
      </div>
    </AppCard>

    <!-- Danger Zone Block -->
    <AppCard class="danger-zone-card">
      <div class="p-6 flex justify-between items-center">
        <div>
          <h3 class="text-lg font-bold color-danger mb-1 flex items-center gap-2">
            <AppIcon name="alert-circle" size="20" />
            <span>Zone de Purge des Données</span>
          </h3>
          <p class="text-sm text-muted">
            Cette action effacera définitivement l'ensemble des données d'essai métier.
          </p>
        </div>
        <AppButton variant="danger" size="md" @click="showResetModal = true">
          <AppIcon name="trash" size="18" />
          <span>Réinitialiser toutes les données</span>
        </AppButton>
      </div>
    </AppCard>

    <!-- Modal Confirmation Reset -->
    <AppModal v-model="showResetModal" title="Confirmer la réinitialisation" size="sm">
      <div class="p-4">
        <AppAlert variant="danger" class="mb-4">
          <strong>Attention !</strong> Toutes les données métier de Dolibarr et PostgreSQL seront supprimées. Seul votre compte Administrateur sera conservé.
        </AppAlert>

        <p class="text-sm mb-3 font-semibold">
          Saisissez <code class="sku-badge color-danger">RESET</code> pour confirmer la purge :
        </p>

        <AppInput
          id="confirm-input"
          v-model="confirmText"
          placeholder="Tapez RESET pour valider"
          class="mb-2"
        />
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="cancelReset">Annuler</AppButton>
        <AppButton
          variant="danger"
          :disabled="confirmText.trim().toUpperCase() !== 'RESET'"
          :loading="resetting"
          @click="executeReset"
        >
          Valider la Réinitialisation
        </AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import api from '../../services/api'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const showResetModal = ref(false)
const confirmText = ref('')
const resetting = ref(false)
const pageError = ref('')
const pageSuccess = ref('')

function cancelReset() {
  showResetModal.value = false
  confirmText.value = ''
}

async function executeReset() {
  if (confirmText.value.trim().toUpperCase() !== 'RESET') return

  resetting.value = true
  pageError.value = ''
  pageSuccess.value = ''

  try {
    const res = await api.post('/system/reset-data', {
      confirm_text: confirmText.value.trim()
    })

    pageSuccess.value = res.data.message || 'Toutes les données métier ont été réinitialisées avec succès.'
    showResetModal.value = false
    confirmText.value = ''
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la réinitialisation.'
  } finally {
    resetting.value = false
  }
}
</script>

<style scoped>
.reset-scope-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.scope-box {
  padding: var(--space-4);
  border-radius: var(--radius-sm);
}

.scope-box--danger {
  background: rgba(220, 38, 38, 0.04);
  border: 1px solid rgba(220, 38, 38, 0.2);
}

.scope-box--success {
  background: rgba(5, 150, 105, 0.04);
  border: 1px solid rgba(5, 150, 105, 0.2);
}

.scope-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.scope-list li {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.danger-zone-card {
  border: 1.5px solid var(--color-danger);
  background: rgba(220, 38, 38, 0.02);
}
</style>
