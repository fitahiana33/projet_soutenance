<template>
  <AppLayout>
    <PageHeader
      title="Gestion des Achats & Analyse Fournisseurs"
      subtitle="Workflow complet d'approvisionnement (Demande → Commande → Réception → Facturation) et Scoring IA Fournisseurs"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" @click="handleExportPurchasesExcel">
          <AppIcon name="file-text" size="16" />
          <span>Exporter Excel</span>
        </AppButton>
        <AppButton variant="secondary" size="sm" @click="openCreateSupplierModal">
          <AppIcon name="users" size="16" />
          <span>Nouveau Fournisseur</span>
        </AppButton>
        <AppButton variant="primary" size="sm" @click="openCreateRequisitionModal">
          <AppIcon name="plus" size="16" />
          <span>Nouvelle Demande d'Achat</span>
        </AppButton>
      </template>
    </PageHeader>

    <AppAlert v-if="pageError" variant="danger" dismissible @dismiss="pageError = ''">
      {{ pageError }}
    </AppAlert>

    <AppAlert v-if="pageSuccess" variant="success" dismissible @dismiss="pageSuccess = ''">
      {{ pageSuccess }}
    </AppAlert>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid mb-6">
      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Fournisseurs Actifs</span>
          <span class="kpi-value">{{ overview.total_suppliers || 0 }}</span>
          <span class="kpi-sub font-semibold color-success">Catalogués & Synchronisés</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--primary">
          <AppIcon name="users" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Volume Total Achats</span>
          <span class="kpi-value">{{ formatCurrency(overview.total_purchase_amount) }}</span>
          <span class="kpi-sub text-muted">Sur l'exercice en cours</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--success">
          <AppIcon name="dollar-sign" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Demandes en Attente</span>
          <span class="kpi-value color-warning">{{ overview.pending_requisitions_count || 0 }}</span>
          <span class="kpi-sub color-warning">En attente de validation</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--warning">
          <AppIcon name="clock" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Top Fournisseur IA</span>
          <span class="kpi-value text-lg text-primary">{{ overview.top_performing_supplier || 'N/A' }}</span>
          <span class="kpi-sub color-success">Meilleur Score Global</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--info">
          <AppIcon name="shield" size="24" />
        </div>
      </AppCard>
    </div>

    <!-- Visual Workflow Stepper Bar -->
    <div class="workflow-stepper-bar">
      <div class="workflow-step" :class="{ 'workflow-step--active': activeTab === 'requisitions' }">
        <div class="step-num">1</div>
        <div class="step-info">
          <span class="step-title">1. Demande d'Achat</span>
          <span class="step-sub">Saisie du besoin</span>
        </div>
      </div>
      <div class="workflow-arrow">➔</div>
      <div class="workflow-step" :class="{ 'workflow-step--active': activeTab === 'requisitions' }">
        <div class="step-num">2</div>
        <div class="step-info">
          <span class="step-title">2. Validation Rôle</span>
          <span class="step-sub">Approbation</span>
        </div>
      </div>
      <div class="workflow-arrow">➔</div>
      <div class="workflow-step" :class="{ 'workflow-step--active': activeTab === 'orders' }">
        <div class="step-num">3</div>
        <div class="step-info">
          <span class="step-title">3. Commande</span>
          <span class="step-sub">Négociation</span>
        </div>
      </div>
      <div class="workflow-arrow">➔</div>
      <div class="workflow-step" :class="{ 'workflow-step--active': activeTab === 'orders' }">
        <div class="step-num">4-5</div>
        <div class="step-info">
          <span class="step-title">4-5. Réception & Qualité</span>
          <span class="step-sub">Stock Entrée</span>
        </div>
      </div>
      <div class="workflow-arrow">➔</div>
      <div class="workflow-step" :class="{ 'workflow-step--active': activeTab === 'invoices' }">
        <div class="step-num">6</div>
        <div class="step-info">
          <span class="step-title">6. Facturation</span>
          <span class="step-sub">Comptabilité</span>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-header mb-4">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-btn', { 'tab-btn--active': activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <AppIcon :name="tab.icon" size="16" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- TAB 1: RÉPERTOIRE FOURNISSEURS -->
    <div v-if="activeTab === 'suppliers'">
      <AppTable
        :columns="columnsSuppliers"
        :items="suppliers"
        :loading="loading"
        empty-text="Aucun fournisseur enregistré."
      >
        <template #col-code="{ value }">
          <span class="sku-badge font-mono">{{ value }}</span>
        </template>

        <template #col-status="{ value }">
          <AppBadge
            :variant="value === 'ACTIF' ? 'success' : 'danger'"
            :label="value"
          />
        </template>
        <template #actions="{ item }">
          <div class="actions-group">
            <button type="button" class="icon-btn" title="Modifier le fournisseur" @click="openEditSupplierModal(item)">
              <AppIcon name="edit" size="18" />
            </button>
            <button type="button" class="icon-btn icon-btn--danger" title="Supprimer ou désactiver le fournisseur" @click="confirmDeleteSupplier(item)">
              <AppIcon name="trash" size="18" />
            </button>
          </div>
        </template>
      </AppTable>
    </div>

    <!-- TAB 2: DEMANDES D'ACHAT (WORKFLOW 1 & 2) -->
    <div v-if="activeTab === 'requisitions'">
      <AppTable
        :columns="columnsRequisitions"
        :items="requisitions"
        :loading="loading"
        empty-text="Aucune demande d'achat en cours."
      >
        <template #col-reference="{ value }">
          <span class="sku-badge font-mono">{{ value }}</span>
        </template>

        <template #col-total_estimated="{ value }">
          <strong>{{ formatCurrency(value) }}</strong>
        </template>

        <template #col-status="{ value }">
          <AppBadge
            :variant="value === 'VALIDEE' ? 'success' : value === 'DEMANDE' ? 'warning' : value === 'REJETEE' ? 'danger' : 'info'"
            :label="value"
          />
        </template>

        <template #actions="{ item }">
          <button type="button" class="icon-btn" title="Voir les détails" @click="openPurchaseDetail(item, 'requisition')">
            <AppIcon name="eye" size="18" />
          </button>
          <div v-if="item.status === 'DEMANDE'" class="flex gap-2">
            <AppButton variant="success" size="xs" @click="handleValidateRequisition(item.id_requisition, 'VALIDER')">
              Valider
            </AppButton>
            <AppButton variant="danger" size="xs" @click="handleValidateRequisition(item.id_requisition, 'REJETER')">
              Rejeter
            </AppButton>
          </div>
          <div v-else-if="item.status === 'VALIDEE'">
            <AppButton variant="primary" size="xs" @click="openCreateOrderFromReq(item)">
              Commander
            </AppButton>
          </div>
        </template>
      </AppTable>
    </div>

    <!-- TAB 3: COMMANDES D'ACHAT & RÉCEPTION (WORKFLOW 3, 4 & 5) -->
    <div v-if="activeTab === 'orders'">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Commandes en cours et Réceptions</h3>
        <AppButton variant="primary" size="sm" @click="openCreateOrderModal">
          <AppIcon name="plus" size="14" />
          <span>Créer une Commande Directe</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsOrders"
        :items="orders"
        :loading="loading"
        empty-text="Aucune commande d'achat."
      >
        <template #col-reference="{ value }">
          <span class="sku-badge font-mono">{{ value }}</span>
        </template>

        <template #col-total_amount="{ value }">
          <strong>{{ formatCurrency(value) }}</strong>
        </template>

        <template #col-status="{ value }">
          <AppBadge
            :variant="value === 'RECUE' ? 'success' : value === 'PARTIELLEMENT_RECUE' ? 'warning' : value === 'COMMANDEE' ? 'primary' : 'danger'"
            :label="value"
          />
        </template>

        <template #actions="{ item }">
          <button type="button" class="icon-btn" title="Voir les détails" @click="openPurchaseDetail(item, 'order')">
            <AppIcon name="eye" size="18" />
          </button>
          <AppButton
            v-if="['COMMANDEE', 'PARTIELLEMENT_RECUE'].includes(item.status)"
            variant="warning"
            size="xs"
            @click="openReceiptModal(item)"
          >
            <AppIcon name="box" size="14" />
            <span>Réceptionner & Contrôler</span>
          </AppButton>
          <span v-else class="text-xs text-muted">Réceptionnée</span>
        </template>
      </AppTable>

      <!-- Historique des contrôles de qualité -->
      <div class="mt-8">
        <h4 class="text-md font-semibold mb-3">Journal des Réceptions & Contrôles Qualité</h4>
        <AppTable
          :columns="columnsReceipts"
          :items="receipts"
          :loading="loading"
          empty-text="Aucun contrôle qualité enregistré."
        >
          <template #col-quality_control_status="{ value }">
            <AppBadge
              :variant="value === 'CONFORME' ? 'success' : value === 'AVEC_RESERVES' ? 'warning' : 'danger'"
              :label="value"
            />
          </template>
          <template #actions="{ item }">
            <button type="button" class="icon-btn" title="Voir les détails" @click="openPurchaseDetail(item, 'receipt')">
              <AppIcon name="eye" size="18" />
            </button>
          </template>
        </AppTable>
      </div>
    </div>

    <!-- TAB 4: FACTURATION FOURNISSEURS (WORKFLOW 6) -->
    <div v-if="activeTab === 'invoices'">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Factures Fournisseurs</h3>
        <AppButton variant="primary" size="sm" @click="openCreateInvoiceModal">
          <AppIcon name="plus" size="14" />
          <span>Saisir une Facture Fournisseur</span>
        </AppButton>
      </div>

      <AppTable
        :columns="columnsInvoices"
        :items="invoices"
        :loading="loading"
        empty-text="Aucune facture fournisseur enregistrée."
      >
        <template #col-invoice_number="{ value }">
          <span class="sku-badge font-mono">{{ value }}</span>
        </template>

        <template #col-invoice_date="{ value }">
          <span class="text-muted text-xs">{{ value ? new Date(value).toLocaleDateString('fr-FR') : '—' }}</span>
        </template>

        <template #col-amount_ttc="{ value }">
          <strong class="color-success">{{ formatCurrency(value) }}</strong>
        </template>

        <template #col-status="{ value }">
          <AppBadge
            :variant="value === 'PAYEE' ? 'success' : value === 'VALIDEE' ? 'info' : 'warning'"
            :label="value"
          />
        </template>
        <template #actions="{ item }">
          <button type="button" class="icon-btn" title="Voir les détails" @click="openPurchaseDetail(item, 'invoice')">
            <AppIcon name="eye" size="18" />
          </button>
        </template>
      </AppTable>
    </div>

    <!-- TAB 5: MODULE 6 — ANALYSE & SCORING IA FOURNISSEURS -->
    <div v-if="activeTab === 'analysis'">
      <!-- Assistant IA Card -->
      <AppCard class="mb-6 p-5 border-primary bg-slate-900/40">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <AppIcon name="shield" size="20" class="text-primary" />
              <h3 class="text-lg font-bold text-primary">Assistant Décisionnel IA — Recommandation Fournisseur</h3>
            </div>
            <p v-if="aiRecommendation.ai_explanation" class="text-sm text-gray-300">
              {{ aiRecommendation.ai_explanation }}
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs text-muted mr-2">Critère Prioritaire :</span>
            <AppButton
              v-for="strat in strategies"
              :key="strat.id"
              :variant="selectedStrategy === strat.id ? 'primary' : 'ghost'"
              size="xs"
              @click="changeStrategy(strat.id)"
            >
              {{ strat.label }}
            </AppButton>
          </div>
        </div>
      </AppCard>

      <!-- Score Table -->
      <AppTable
        :columns="columnsAnalysis"
        :items="supplierAnalysis"
        :loading="loading"
        empty-text="Aucune donnée d'analyse disponible."
      >
        <template #col-avg_price="{ value }">
          {{ formatCurrency(value) }}
        </template>

        <template #col-avg_delivery_days="{ value }">
          <span>{{ value }} jours</span>
        </template>

        <template #col-delay_rate_percent="{ value }">
          <span :class="value > 5 ? 'color-danger font-semibold' : 'color-success'">
            {{ value }}%
          </span>
        </template>

        <template #col-conformity_rate_percent="{ value }">
          <span class="color-success font-semibold">{{ value }}%</span>
        </template>

        <template #col-price_trend="{ value }">
          <AppBadge
            :variant="value === 'BAISSE' ? 'success' : value === 'STABLE' ? 'info' : 'warning'"
            :label="value"
          />
        </template>

        <template #col-overall_score_percent="{ value }">
          <span class="text-lg font-bold color-primary">{{ value }}%</span>
        </template>

        <template #col-recommendation_badge="{ value }">
          <AppBadge
            :variant="value === 'RECOMMANDÉ' ? 'success' : value === 'ACCEPTABLE' ? 'warning' : 'danger'"
            :label="value"
          />
        </template>
      </AppTable>
    </div>

    <!-- Modal Nouveau Fournisseur -->
    <AppModal v-model="showSupplierModal" :title="editingSupplier ? 'Modifier le fournisseur' : 'Nouveau Fournisseur'" size="sm">
      <form @submit.prevent="saveSupplier" class="modal-form">
        <AppInput
          id="sup-name"
          v-model="supForm.name"
          label="Nom de l'entreprise *"
          placeholder="ex: TechGlobal France"
          required
        />

        <AppInput
          id="sup-code"
          v-model="supForm.code"
          label="Code Fournisseur"
          placeholder="ex: FOURN-009"
        />

        <AppInput
          id="sup-email"
          v-model="supForm.email"
          type="email"
          label="Email de contact"
          placeholder="contact@fournisseur.com"
        />

        <AppInput
          id="sup-phone"
          v-model="supForm.phone"
          label="Téléphone"
          placeholder="+33 1 23 45 67 89"
        />

        <AppInput
          id="sup-address"
          v-model="supForm.address"
          label="Adresse complète"
          placeholder="Adresse du siège..."
        />

        <AppInput
          id="sup-city"
          v-model="supForm.city"
          label="Ville"
          placeholder="ex: Antananarivo"
        />

        <div class="form-group">
          <label class="form-label" for="sup-status">Statut</label>
          <select id="sup-status" v-model="supForm.status" class="form-select">
            <option value="ACTIF">Actif</option>
            <option value="INACTIF">Inactif</option>
          </select>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showSupplierModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveSupplier">{{ editingSupplier ? 'Enregistrer les modifications' : 'Enregistrer Fournisseur' }}</AppButton>
      </template>
    </AppModal>

    <AppModal v-model="showDeleteSupplierModal" title="Confirmer la suppression" size="sm">
      <p>Voulez-vous supprimer le fournisseur <strong>{{ deletingSupplier?.name }}</strong> ?</p>
      <p class="text-sm text-muted mt-2">Un fournisseur lié à une commande sera désactivé afin de conserver l'historique des achats.</p>
      <template #footer>
        <AppButton variant="ghost" @click="showDeleteSupplierModal = false">Annuler</AppButton>
        <AppButton variant="danger" :loading="saving" @click="handleDeleteSupplier">Confirmer</AppButton>
      </template>
    </AppModal>

    <!-- Modal Nouvelle Demande d'Achat (Workflow Étape 1) -->
    <AppModal v-model="showRequisitionModal" title="Nouvelle Demande d'Achat" size="sm">
      <form @submit.prevent="saveRequisition" class="modal-form">
        <div class="form-group">
          <label class="form-label">Produit à réapprovisionner *</label>
            <SearchableSelect v-model="reqForm.product_id" :options="products" value-key="id_product" label-key="label" :search-keys="['reference']" placeholder="Rechercher un produit..." required />
            <select v-model="reqForm.product_id" class="form-select" style="display: none" aria-hidden="true" required>
            <option :value="null">Sélectionner un produit</option>
            <option v-for="p in products" :key="p.id_product" :value="p.id_product">
              {{ p.reference }} — {{ p.label }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Fournisseur suggéré</label>
            <SearchableSelect v-model="reqForm.supplier_id" :options="suppliers" value-key="id_supplier" label-key="name" :search-keys="['code', 'email']" placeholder="Rechercher un fournisseur..." />
            <select v-model="reqForm.supplier_id" class="form-select" style="display: none" aria-hidden="true">
            <option :value="null">Sélectionner un fournisseur</option>
            <option v-for="s in suppliers" :key="s.id_supplier" :value="s.id_supplier">
              {{ s.name }}
            </option>
          </select>
        </div>

        <AppInput
          id="req-qty"
          v-model.number="reqForm.quantity"
          type="number"
          label="Quantité demandée *"
          required
        />

        <AppInput
          id="req-price"
          v-model.number="reqForm.estimated_unit_price"
          type="number"
          step="0.01"
          label="Prix unitaire estimé (€) *"
          required
        />

        <AppInput
          id="req-reason"
          v-model="reqForm.reason"
          label="Motif / Justification du besoin"
          placeholder="ex: Réassort suite à hausse des ventes"
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showRequisitionModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveRequisition">Soumettre la Demande</AppButton>
      </template>
    </AppModal>

    <!-- Modal Créer / Valider Commande d'Achat (Workflow Étape 3) -->
    <AppModal v-model="showOrderModal" title="Passer une Commande d'Achat" size="sm">
      <form @submit.prevent="saveOrder" class="modal-form">
        <div class="form-group">
          <label class="form-label">Fournisseur *</label>
            <SearchableSelect v-model="orderForm.supplier_id" :options="suppliers" value-key="id_supplier" label-key="name" :search-keys="['code', 'email']" placeholder="Rechercher un fournisseur..." required />
            <select v-model="orderForm.supplier_id" class="form-select" style="display: none" aria-hidden="true" required>
            <option :value="null">Sélectionner le fournisseur</option>
            <option v-for="s in suppliers" :key="s.id_supplier" :value="s.id_supplier">
              {{ s.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Produit *</label>
            <SearchableSelect v-model="orderForm.product_id" :options="products" value-key="id_product" label-key="label" :search-keys="['reference']" placeholder="Rechercher un produit..." required />
            <select v-model="orderForm.product_id" class="form-select" style="display: none" aria-hidden="true" required>
            <option :value="null">Sélectionner le produit</option>
            <option v-for="p in products" :key="p.id_product" :value="p.id_product">
              {{ p.reference }} — {{ p.label }}
            </option>
          </select>
        </div>

        <AppInput
          id="ord-qty"
          v-model.number="orderForm.quantity"
          type="number"
          label="Quantité à commander *"
          required
        />

        <AppInput
          id="ord-price"
          v-model.number="orderForm.unit_price"
          type="number"
          step="0.01"
          label="Prix unitaire d'achat négocié (€) *"
          required
        />

        <AppInput
          id="ord-exp-date"
          v-model="orderForm.expected_delivery_date"
          type="date"
          label="Date de livraison prévue"
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showOrderModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveOrder">Valider la Commande</AppButton>
      </template>
    </AppModal>

    <!-- Modal Réception & Contrôle Qualité (Workflow Étape 4 & 5) -->
    <AppModal v-model="showReceiptModal" title="Réception & Contrôle Qualité" size="sm">
      <form @submit.prevent="saveReceipt" class="modal-form">
        <div class="p-3 bg-slate-800 rounded-lg mb-4 text-sm">
          <div><strong>Commande :</strong> {{ selectedOrderToReceive?.reference }}</div>
          <div><strong>Produit :</strong> {{ selectedOrderToReceive?.product_label }}</div>
          <div><strong>Quantité commandée :</strong> {{ selectedOrderToReceive?.quantity }} unités</div>
          <div><strong>Déjà reçue :</strong> {{ selectedOrderToReceive?.quantity_received || 0 }} unités</div>
          <div><strong>Restante :</strong> {{ selectedOrderToReceive?.quantity_remaining ?? selectedOrderToReceive?.quantity }} unités</div>
        </div>

        <AppInput
          id="rec-qty"
          v-model.number="receiptForm.quantity_received"
          type="number"
          label="Quantité réellement reçue *"
          :min="1"
          :max="selectedOrderToReceive?.quantity_remaining || selectedOrderToReceive?.quantity"
          required
        />

        <div class="form-group">
          <label class="form-label">Contrôle de Conformité Qualité *</label>
          <select v-model="receiptForm.quality_control_status" class="form-select" required>
            <option value="CONFORME">Conforme (Matériel OK)</option>
            <option value="AVEC_RESERVES">Avec Réserves (Emballage abîmé, etc.)</option>
            <option value="NON_CONFORME">Non Conforme (Produit défectueux / erreur)</option>
          </select>
        </div>

        <AppInput
          id="rec-notes"
          v-model="receiptForm.quality_notes"
          label="Remarques / Rapport de contrôle"
          placeholder="Détails de la vérification à la réception..."
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showReceiptModal = false">Annuler</AppButton>
        <AppButton variant="warning" :loading="saving" @click="saveReceipt">Enregistrer Réception & Entrer Stock</AppButton>
      </template>
    </AppModal>

    <!-- Modal Facture Fournisseur (Workflow Étape 6) -->
    <AppModal v-model="showInvoiceModal" title="Enregistrer une Facture Fournisseur" size="sm">
      <form @submit.prevent="saveInvoice" class="modal-form">
        <div class="form-group">
          <label class="form-label">Commande associée *</label>
          <SearchableSelect v-model="invForm.order_id" :options="orders" value-key="id_order" label-key="reference" :search-keys="['supplier_name', 'product_label']" placeholder="Rechercher une commande..." required @change="onOrderSelectForInvoice" />
          <select v-model="invForm.order_id" class="form-select" style="display: none" aria-hidden="true" required @change="onOrderSelectForInvoice">
            <option :value="null">Sélectionner une commande reçue</option>
            <option v-for="o in orders" :key="o.id_order" :value="o.id_order">
              {{ o.reference }} — {{ o.supplier_name }} ({{ formatCurrency(o.total_amount) }})
            </option>
          </select>
        </div>

        <AppInput
          id="inv-num"
          v-model="invForm.invoice_number"
          label="N° Facture Fournisseur *"
          placeholder="ex: FF-2026-9901"
          required
        />

        <AppInput
          id="inv-ht"
          v-model.number="invForm.amount_ht"
          type="number"
          step="0.01"
          label="Montant Hors Taxe (HT €) *"
          required
        />

        <AppInput
          id="inv-vat"
          v-model.number="invForm.vat_rate"
          type="number"
          step="0.1"
          label="Taux de TVA (%)"
        />
        <AppInput
          id="inv-date"
          v-model="invForm.invoice_date"
          type="date"
          label="Date de facture *"
          required
        />
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="showInvoiceModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="saveInvoice">Comptabiliser la Facture</AppButton>
      </template>
    </AppModal>

    <AppModal v-model="showPurchaseDetailModal" :title="purchaseDetailTitle" size="md">
      <div v-if="selectedPurchaseDetail" class="detail-grid text-sm">
        <div><span class="text-muted">Référence</span><strong>{{ selectedPurchaseDetail.reference || selectedPurchaseDetail.invoice_number }}</strong></div>
        <div><span class="text-muted">Date</span><strong>{{ formatDate(selectedPurchaseDetail.invoice_date || selectedPurchaseDetail.received_at || selectedPurchaseDetail.created_at || selectedPurchaseDetail.order_date) }}</strong></div>
        <div><span class="text-muted">Fournisseur</span><strong>{{ selectedPurchaseDetail.supplier_name || '—' }}</strong></div>
        <div><span class="text-muted">Produit</span><strong>{{ selectedPurchaseDetail.product_label || '—' }}</strong></div>
        <div><span class="text-muted">Quantité commandée</span><strong>{{ selectedPurchaseDetail.quantity ?? '—' }}</strong></div>
        <div><span class="text-muted">Quantité reçue</span><strong>{{ selectedPurchaseDetail.quantity_received ?? '—' }}</strong></div>
        <div><span class="text-muted">Montant HT</span><strong>{{ selectedPurchaseDetail.amount_ht !== undefined ? formatCurrency(selectedPurchaseDetail.amount_ht) : selectedPurchaseDetail.total_amount !== undefined ? formatCurrency(selectedPurchaseDetail.total_amount) : '—' }}</strong></div>
        <div><span class="text-muted">TVA</span><strong>{{ selectedPurchaseDetail.amount_tva !== undefined ? formatCurrency(selectedPurchaseDetail.amount_tva) : selectedPurchaseDetail.vat_rate !== undefined ? selectedPurchaseDetail.vat_rate + ' %' : '—' }}</strong></div>
        <div><span class="text-muted">Montant TTC</span><strong>{{ selectedPurchaseDetail.amount_ttc !== undefined ? formatCurrency(selectedPurchaseDetail.amount_ttc) : '—' }}</strong></div>
        <div><span class="text-muted">Statut</span><strong>{{ selectedPurchaseDetail.status || selectedPurchaseDetail.quality_control_status || '—' }}</strong></div>
        <div class="detail-grid__wide"><span class="text-muted">Remarques</span><strong>{{ selectedPurchaseDetail.quality_notes || selectedPurchaseDetail.notes || selectedPurchaseDetail.reason || '—' }}</strong></div>
      </div>
      <template #footer><AppButton variant="ghost" @click="showPurchaseDetailModal = false">Fermer</AppButton></template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import purchaseService from '../../services/purchaseService'
import productService from '../../services/productService'
import { exportToExcel } from '../../utils/excelExport'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppTable from '../../components/ui/AppTable.vue'
import AppBadge from '../../components/ui/AppBadge.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'
import SearchableSelect from '../../components/ui/SearchableSelect.vue'
import { confirmAction } from '../../utils/actionConfirm'

const activeTab = ref('suppliers')
const overview = ref({})
const suppliers = ref([])
const requisitions = ref([])
const orders = ref([])
const receipts = ref([])
const invoices = ref([])
const products = ref([])
const supplierAnalysis = ref([])
const aiRecommendation = ref({})
const selectedStrategy = ref('BALANCED')

const loading = ref(false)
const saving = ref(false)

const pageError = ref('')
const pageSuccess = ref('')

const showSupplierModal = ref(false)
const showDeleteSupplierModal = ref(false)
const showRequisitionModal = ref(false)
const showOrderModal = ref(false)
const showReceiptModal = ref(false)
const showInvoiceModal = ref(false)
const selectedOrderToReceive = ref(null)
const showPurchaseDetailModal = ref(false)
const selectedPurchaseDetail = ref(null)
const purchaseDetailType = ref('')
const editingSupplier = ref(null)
const deletingSupplier = ref(null)

const tabs = [
  { id: 'suppliers', label: 'Répertoire Fournisseurs', icon: 'users' },
  { id: 'requisitions', label: 'Demandes d\'Achat', icon: 'clock' },
  { id: 'orders', label: 'Commandes & Réception', icon: 'package' },
  { id: 'invoices', label: 'Facturation Achats', icon: 'dollar-sign' },
  { id: 'analysis', label: 'Analyse & Scoring IA', icon: 'shield' }
]

const strategies = [
  { id: 'BALANCED', label: 'Équilibré (Standard)' },
  { id: 'PRIX', label: 'Priorité Prix (Moins Cher)' },
  { id: 'DELAI', label: 'Priorité Délai (Plus Rapide)' },
  { id: 'QUALITE', label: 'Priorité Qualité (Conformité)' },
  { id: 'FIABILITE', label: 'Priorité Fiabilité (Zéro Retard)' }
]

const supForm = ref({ name: '', code: '', email: '', phone: '', address: '', city: '', status: 'ACTIF' })
const reqForm = ref({ product_id: null, supplier_id: null, quantity: 10, estimated_unit_price: 100, reason: '' })
const orderForm = ref({ requisition_id: null, supplier_id: null, product_id: null, quantity: 10, unit_price: 100, expected_delivery_date: '' })
const receiptForm = ref({ order_id: null, quantity_received: 10, quality_control_status: 'CONFORME', quality_notes: '' })
const invForm = ref({ order_id: null, invoice_number: '', amount_ht: 0, vat_rate: 20.0, invoice_date: getTodayInput() })

const purchaseDetailTitle = computed(() => {
  const labels = { requisition: "Détails de la demande d'achat", order: "Détails de la commande d'achat", receipt: 'Détails de la réception', invoice: 'Détails de la facture fournisseur' }
  return labels[purchaseDetailType.value] || 'Détails'
})

function getTodayInput() {
  const now = new Date()
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
  return local.toISOString().slice(0, 10)
}

const columnsSuppliers = [
  { key: 'code', label: 'Code', width: '15%' },
  { key: 'name', label: 'Nom de l\'entreprise', width: '30%' },
  { key: 'email', label: 'Email', width: '25%' },
  { key: 'phone', label: 'Téléphone', width: '18%' },
  { key: 'status', label: 'Statut', width: '12%' }
]

const columnsRequisitions = [
  { key: 'reference', label: 'N° Réf', width: '15%' },
  { key: 'product_label', label: 'Produit Demandé', width: '25%' },
  { key: 'supplier_name', label: 'Fournisseur Suggéré', width: '20%' },
  { key: 'quantity', label: 'Qté', width: '10%' },
  { key: 'total_estimated', label: 'Total Estimé', width: '15%' },
  { key: 'status', label: 'Statut Workflow', width: '15%' }
]

const columnsOrders = [
  { key: 'reference', label: 'N° Commande', width: '15%' },
  { key: 'supplier_name', label: 'Fournisseur', width: '22%' },
  { key: 'product_label', label: 'Produit', width: '25%' },
  { key: 'quantity', label: 'Qté', width: '8%' },
  { key: 'total_amount', label: 'Montant HT', width: '15%' },
  { key: 'status', label: 'Statut', width: '15%' }
]

const columnsReceipts = [
  { key: 'reference', label: 'N° Bon Réception', width: '18%' },
  { key: 'order_ref', label: 'N° Commande', width: '15%' },
  { key: 'product_label', label: 'Produit', width: '25%' },
  { key: 'quantity_received', label: 'Qté Reçue', width: '12%' },
  { key: 'quality_control_status', label: 'Contrôle Qualité', width: '20%' }
]

const columnsInvoices = [
  { key: 'invoice_number', label: 'N° Facture', width: '20%' },
  { key: 'order_ref', label: 'N° Commande', width: '18%' },
  { key: 'supplier_name', label: 'Fournisseur', width: '27%' },
  { key: 'amount_ttc', label: 'Montant TTC', width: '20%' },
  { key: 'invoice_date', label: 'Date', width: '13%' },
  { key: 'status', label: 'Statut', width: '15%' }
]

const columnsAnalysis = [
  { key: 'supplier_name', label: 'Fournisseur', width: '20%' },
  { key: 'avg_price', label: 'Prix Moyen', width: '11%' },
  { key: 'avg_delivery_days', label: 'Délai Moyen', width: '11%' },
  { key: 'delay_rate_percent', label: 'Taux Retard', width: '10%' },
  { key: 'conformity_rate_percent', label: 'Conformité', width: '10%' },
  { key: 'price_trend', label: 'Tendance Prix', width: '11%' },
  { key: 'overall_score_percent', label: 'Score IA %', width: '12%' },
  { key: 'recommendation_badge', label: 'Évaluation', width: '15%' }
]

async function loadAllData() {
  loading.value = true
  pageError.value = ''
  try {
    const [ovRes, supRes, reqRes, ordRes, recRes, invRes, prodRes, anaRes] = await Promise.all([
      purchaseService.getOverview(),
      purchaseService.getSuppliers(),
      purchaseService.getRequisitions(),
      purchaseService.getOrders(),
      purchaseService.getReceipts(),
      purchaseService.getInvoices(),
      productService.getProducts(),
      purchaseService.getAnalysis()
    ])

    overview.value = ovRes.data || {}
    suppliers.value = supRes.data || []
    requisitions.value = reqRes.data || []
    orders.value = ordRes.data || []
    receipts.value = recRes.data || []
    invoices.value = invRes.data || []
    products.value = prodRes.data || []
    supplierAnalysis.value = anaRes.data || []

    await fetchAiRecommendation()
  } catch (error) {
    pageError.value = 'Erreur lors du chargement des données des achats.'
  } finally {
    loading.value = false
  }
}

async function fetchAiRecommendation() {
  try {
    const res = await purchaseService.getAiRecommendations({
      priority_criterion: selectedStrategy.value
    })
    aiRecommendation.value = res.data || {}
  } catch (e) {
    // Handling
  }
}

async function changeStrategy(stratId) {
  selectedStrategy.value = stratId
  await fetchAiRecommendation()
}

function openPurchaseDetail(item, type) {
  selectedPurchaseDetail.value = item
  purchaseDetailType.value = type
  showPurchaseDetailModal.value = true
}

function formatCurrency(val) {
  if (val === undefined || val === null) return '0,00 €'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val)
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('fr-FR')
}

// Modals Trigger
function openCreateSupplierModal() {
  editingSupplier.value = null
  supForm.value = { name: '', code: '', email: '', phone: '', address: '', city: '', status: 'ACTIF' }
  showSupplierModal.value = true
}

function openEditSupplierModal(supplier) {
  editingSupplier.value = supplier
  supForm.value = {
    name: supplier.name || '',
    code: supplier.code || '',
    email: supplier.email || '',
    phone: supplier.phone || '',
    address: supplier.address || '',
    city: supplier.city || '',
    status: supplier.status || 'ACTIF'
  }
  showSupplierModal.value = true
}

function confirmDeleteSupplier(supplier) {
  deletingSupplier.value = supplier
  showDeleteSupplierModal.value = true
}

function openCreateRequisitionModal() {
  reqForm.value = {
    product_id: products.value.length ? products.value[0].id_product : null,
    supplier_id: suppliers.value.length ? suppliers.value[0].id_supplier : null,
    quantity: 10,
    estimated_unit_price: 150.0,
    reason: ''
  }
  showRequisitionModal.value = true
}

function openCreateOrderModal() {
  orderForm.value = {
    requisition_id: null,
    supplier_id: suppliers.value.length ? suppliers.value[0].id_supplier : null,
    product_id: products.value.length ? products.value[0].id_product : null,
    quantity: 10,
    unit_price: 150.0,
    expected_delivery_date: ''
  }
  showOrderModal.value = true
}

function openCreateOrderFromReq(reqItem) {
  orderForm.value = {
    requisition_id: reqItem.id_requisition,
    supplier_id: reqItem.supplier_id || (suppliers.value.length ? suppliers.value[0].id_supplier : null),
    product_id: reqItem.product_id,
    quantity: reqItem.quantity,
    unit_price: reqItem.estimated_unit_price,
    expected_delivery_date: ''
  }
  activeTab.value = 'orders'
  showOrderModal.value = true
}

function openReceiptModal(orderItem) {
  selectedOrderToReceive.value = orderItem
  receiptForm.value = {
    order_id: orderItem.id_order,
    quantity_received: orderItem.quantity_remaining || orderItem.quantity,
    quality_control_status: 'CONFORME',
    quality_notes: 'Vérification effectuée à la réception'
  }
  showReceiptModal.value = true
}

function openCreateInvoiceModal() {
  invForm.value = {
    order_id: orders.value.length ? orders.value[0].id_order : null,
    invoice_number: `FF-2026-${Math.floor(1000 + Math.random() * 9000)}`,
    amount_ht: orders.value.length ? orders.value[0].total_amount : 100.0,
    vat_rate: 20.0,
    invoice_date: getTodayInput()
  }
  showInvoiceModal.value = true
}

function onOrderSelectForInvoice() {
  const o = orders.value.find(ord => ord.id_order === invForm.value.order_id)
  if (o) {
    invForm.value.amount_ht = o.total_amount
  }
}

// Submissions
async function saveSupplier() {
  if (!supForm.value.name) return
  saving.value = true
  try {
    if (editingSupplier.value) {
      await purchaseService.updateSupplier(editingSupplier.value.id_supplier, supForm.value)
      pageSuccess.value = 'Fournisseur modifié avec succès !'
    } else {
      await purchaseService.createSupplier(supForm.value)
      pageSuccess.value = 'Nouveau fournisseur enregistré avec succès !'
    }
    showSupplierModal.value = false
    editingSupplier.value = null
    await loadAllData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de l\'enregistrement du fournisseur.'
  } finally {
    saving.value = false
  }
}

async function handleDeleteSupplier() {
  if (!deletingSupplier.value) return
  saving.value = true
  pageError.value = ''
  try {
    await purchaseService.deleteSupplier(deletingSupplier.value.id_supplier)
    pageSuccess.value = 'Fournisseur supprimé ou désactivé avec succès !'
    showDeleteSupplierModal.value = false
    deletingSupplier.value = null
    await loadAllData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la suppression du fournisseur.'
  } finally {
    saving.value = false
  }
}

async function saveRequisition() {
  if (!reqForm.value.product_id || !reqForm.value.quantity) return
  saving.value = true
  try {
    await purchaseService.createRequisition(reqForm.value)
    pageSuccess.value = 'Demande d\'achat soumise au workflow !'
    showRequisitionModal.value = false
    await loadAllData()
  } catch (e) {
    pageError.value = 'Erreur lors de la création de la demande d\'achat.'
  } finally {
    saving.value = false
  }
}

async function handleValidateRequisition(reqId, action) {
  if (!confirmAction(`Confirmer l’action « ${action === 'VALIDER' ? 'valider' : 'rejeter'} » sur cette demande d’achat ?`)) return
  loading.value = true
  try {
    await purchaseService.validateRequisition(reqId, {
      action: action,
      comment: action === 'VALIDER' ? 'Validation effectuée' : 'Rejeté par le responsable'
    })
    pageSuccess.value = `Demande d'achat ${action === 'VALIDER' ? 'validée' : 'rejetée'} avec succès !`
    await loadAllData()
  } catch (e) {
    pageError.value = 'Erreur lors de la validation.'
  } finally {
    loading.value = false
  }
}

async function saveOrder() {
  if (!orderForm.value.supplier_id || !orderForm.value.product_id) return
  saving.value = true
  try {
    await purchaseService.createOrder(orderForm.value)
    pageSuccess.value = 'Commande d\'achat validée et envoyée au fournisseur !'
    showOrderModal.value = false
    await loadAllData()
  } catch (e) {
    pageError.value = 'Erreur lors de la commande.'
  } finally {
    saving.value = false
  }
}

async function saveReceipt() {
  if (!receiptForm.value.order_id || !receiptForm.value.quantity_received) return
  if (!confirmAction('Confirmer cette réception ? Le stock physique sera augmenté.')) return
  saving.value = true
  try {
    await purchaseService.createReceipt(receiptForm.value)
    pageSuccess.value = 'Réception & Contrôle qualité enregistrés. Stock mis à jour !'
    showReceiptModal.value = false
    await loadAllData()
  } catch (e) {
    pageError.value = 'Erreur lors de l\'enregistrement de la réception.'
  } finally {
    saving.value = false
  }
}

async function saveInvoice() {
  if (!invForm.value.order_id || !invForm.value.invoice_number) return
  if (!confirmAction('Confirmer la comptabilisation de cette facture fournisseur ?')) return
  saving.value = true
  try {
    await purchaseService.createInvoice(invForm.value)
    pageSuccess.value = 'Facture fournisseur comptabilisée avec succès !'
    showInvoiceModal.value = false
    await loadAllData()
  } catch (e) {
    pageError.value = 'Erreur lors de l\'enregistrement de la facture.'
  } finally {
    saving.value = false
  }
}

function handleExportPurchasesExcel() {
  if (activeTab.value === 'suppliers') {
    const cols = [
      { header: 'Raison Sociale', key: 'name' },
      { header: 'Catégorie', key: 'category' },
      { header: 'Email', key: 'email' },
      { header: 'Téléphone', key: 'phone' },
      { header: 'Score Fiabilité (%)', key: 'reliability_score' },
      { header: 'Délai Liv. (jours)', key: 'average_delivery_delay_days' },
      { header: 'Taux Qualité (%)', key: 'quality_rating_percent' },
      { header: 'Statut', key: 'status' }
    ]
    exportToExcel('fournisseurs_achats', 'Fournisseurs', cols, suppliers.value)
  } else if (activeTab.value === 'requisitions') {
    const cols = [
      { header: 'Réf. DA', key: 'requisition_ref' },
      { header: 'Demandeur', key: 'requested_by' },
      { header: 'Article', key: 'product_name' },
      { header: 'Qté', key: 'quantity' },
      { header: 'Priorité', key: 'priority' },
      { header: 'Statut', key: 'status' },
      { header: 'Date', key: 'created_at' }
    ]
    exportToExcel('demandes_achats', 'Demandes d\'Achat', cols, requisitions.value)
  } else if (activeTab.value === 'orders') {
    const cols = [
      { header: 'N° Commande', key: 'order_number' },
      { header: 'Fournisseur', key: 'supplier_name' },
      { header: 'Montant HT (€)', key: 'total_amount_ht' },
      { header: 'Montant TTC (€)', key: 'total_amount_ttc' },
      { header: 'Livraison Prévue', key: 'expected_delivery_date' },
      { header: 'Statut', key: 'status' }
    ]
    exportToExcel('commandes_achats', 'Commandes d\'Achat', cols, orders.value)
  } else if (activeTab.value === 'receipts') {
    const cols = [
      { header: 'N° Bon Réception', key: 'receipt_number' },
      { header: 'Commande Réf', key: 'order_id' },
      { header: 'Qté Reçue', key: 'quantity_received' },
      { header: 'Conforme ?', key: 'quality_approved', formatter: (val) => val ? 'Oui' : 'Non' },
      { header: 'Date Réception', key: 'received_date' }
    ]
    exportToExcel('receptions_achats', 'Réceptions & Contrôles', cols, receipts.value)
  } else {
    const cols = [
      { header: 'N° Facture', key: 'invoice_number' },
      { header: 'Fournisseur', key: 'supplier_name' },
      { header: 'Montant HT (€)', key: 'amount_ht' },
      { header: 'Montant TTC (€)', key: 'amount_ttc' },
      { header: 'Paiement', key: 'payment_status' }
    ]
    exportToExcel('factures_achats', 'Factures Fournisseurs', cols, invoices.value)
  }
}

onMounted(() => {
  loadAllData()
})
</script>

<style scoped>
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
}

.detail-grid > div {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-grid__wide {
  grid-column: 1 / -1;
}

@media (max-width: 700px) {
  .detail-grid { grid-template-columns: 1fr; }
  .detail-grid__wide { grid-column: auto; }
}
</style>
