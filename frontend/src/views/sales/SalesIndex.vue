<template>
  <AppLayout>
    <PageHeader
      title="Gestion des Ventes & Relation Client"
      subtitle="Suivi du chiffre d'affaires, devis pro-forma, commandes client et facturation"
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" @click="fetchData">
          <AppIcon name="refresh" size="16" />
          <span>Actualiser</span>
        </AppButton>
        <AppButton variant="secondary" size="sm" @click="handleExportExcel">
          <AppIcon name="file-text" size="16" />
          <span>Exporter Excel</span>
        </AppButton>
        <AppButton variant="secondary" size="sm" @click="showOrderModal = true">
          <AppIcon name="plus" size="16" />
          <span>Nouvelle Commande</span>
        </AppButton>
        <AppButton variant="primary" size="sm" @click="showInvoiceModal = true">
          <AppIcon name="dollar-sign" size="16" />
          <span>Émettre une Vente</span>
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
          <span class="kpi-title">Chiffre d'Affaires Réalisé</span>
          <span class="kpi-value color-success">{{ formatCurrency(overview.total_revenue || 0) }}</span>
          <span class="kpi-sub text-muted">Factures encaissées</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--success">
          <AppIcon name="dollar-sign" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Portefeuille Clients</span>
          <span class="kpi-value">{{ overview.total_customers || 0 }} <span class="kpi-unit">actifs</span></span>
          <span class="kpi-sub color-info">Tiers enregistrés</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--primary">
          <AppIcon name="users" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Commandes en Cours</span>
          <span class="kpi-value color-warning">{{ overview.pending_orders_count || 0 }}</span>
          <span class="kpi-sub color-warning">En attente de livraison</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--warning">
          <AppIcon name="box" size="24" />
        </div>
      </AppCard>

      <AppCard class="kpi-card">
        <div class="kpi-content">
          <span class="kpi-title">Panier Moyen</span>
          <span class="kpi-value color-primary">{{ formatCurrency(overview.average_order_value || 0) }}</span>
          <span class="kpi-sub text-muted">Par commande validée</span>
        </div>
        <div class="kpi-icon-wrapper kpi-icon--info">
          <AppIcon name="shield" size="24" />
        </div>
      </AppCard>
    </div>

    <!-- Main Content Tabs -->
    <AppCard>
      <div class="tabs-header border-b p-4 flex gap-4">
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'sales' }]" 
          @click="activeTab = 'sales'"
        >
          💰 Ventes Réalisées
        </button>
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'orders' }]" 
          @click="activeTab = 'orders'"
        >
          🛒 Pipeline Commandes
        </button>
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'quotes' }]" 
          @click="activeTab = 'quotes'"
        >
          📑 Devis & Pro-formas
        </button>
        <button 
          :class="['tab-btn', { 'tab-btn--active': activeTab === 'customers' }]" 
          @click="activeTab = 'customers'"
        >
          👥 Référentiel Clients
        </button>
      </div>

      <!-- Tab 1: Ventes Réalisées (Factures) -->
      <div v-if="activeTab === 'sales'" class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold color-primary flex items-center gap-2">
            <AppIcon name="dollar-sign" size="20" />
            <span>Registre des Ventes Réalisées &amp; Règlements</span>
          </h3>
          <AppButton variant="primary" size="sm" @click="showInvoiceModal = true">
            <AppIcon name="plus" size="14" />
            <span>Émettre une Facture</span>
          </AppButton>
        </div>

        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Réf. Facture</th>
                <th>Réf. Commande</th>
                <th>Client</th>
                <th>Montant HT</th>
                <th>Montant TTC</th>
                <th>Montant Payé</th>
                <th>Mode Règlement</th>
                <th>Statut</th>
                <th>Date Émission</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inv in invoices" :key="inv.id_invoice">
                <td class="font-bold color-primary">{{ inv.invoice_ref }}</td>
                <td class="font-semibold text-slate-300">{{ inv.order_ref }}</td>
                <td class="font-semibold text-white">{{ inv.customer_name }}</td>
                <td>{{ formatCurrency(inv.total_amount_ht) }}</td>
                <td class="font-bold text-amber-400">{{ formatCurrency(inv.total_amount_ttc) }}</td>
                <td class="font-bold color-success">{{ formatCurrency(inv.amount_paid) }}</td>
                <td><span class="badge badge-info">{{ inv.payment_mode || 'VIREMENT' }}</span></td>
                <td>
                  <span :class="['badge', inv.status === 'PAYE' ? 'badge-success' : inv.status === 'ANNULEE' ? 'badge-danger' : 'badge-warning']">
                    {{ inv.status }}
                  </span>
                </td>
                <td class="text-muted text-xs">{{ formatDate(inv.created_at) }}</td>
                <td>
                  <AppButton variant="ghost" size="xs" @click="openDetailModal(inv, 'invoice')">
                    <AppIcon name="eye" size="12" />
                    <span>Détails</span>
                  </AppButton>
                </td>
              </tr>
              <tr v-if="invoices.length === 0">
                <td colspan="10" class="text-center py-6 text-muted">Aucune vente enregistrée. Créez une commande puis émettez une facture.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab 2: Pipeline Commandes -->
      <div v-if="activeTab === 'orders'" class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold color-primary flex items-center gap-2">
            <AppIcon name="box" size="20" />
            <span>Pipeline Commandes Clients</span>
          </h3>
          <AppButton variant="primary" size="sm" @click="showOrderModal = true">
            <AppIcon name="plus" size="14" />
            <span>Créer une Commande</span>
          </AppButton>
        </div>

        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Réf. Commande</th>
                <th>Client</th>
                <th>Articles</th>
                <th>Montant HT</th>
                <th>Montant TTC</th>
                <th>Réservation Stock</th>
                <th>Statut</th>
                <th>Date</th>
                <th>Actions ERP</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ord in orders" :key="ord.id_order">
                <td class="font-bold color-primary">{{ ord.order_ref }}</td>
                <td class="font-semibold text-white">{{ ord.customer_name }}</td>
                <td>{{ ord.items_count || (ord.items ? ord.items.length : 1) }} ligne(s)</td>
                <td>{{ formatCurrency(ord.total_amount_ht) }}</td>
                <td class="font-bold text-amber-400">{{ formatCurrency(ord.total_amount_ttc) }}</td>
                <td>
                  <span :class="['badge', ord.stock_reserved ? 'badge-success' : 'badge-neutral']">
                    {{ ord.stock_reserved ? 'Réservé' : 'Non réservé' }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', getStatusBadgeClass(ord.status)]">
                    {{ ord.status }}
                  </span>
                </td>
                <td class="text-muted text-xs">{{ formatDate(ord.created_at) }}</td>
                <td>
                  <div class="flex items-center gap-1">
                    <AppButton variant="ghost" size="xs" @click="openDetailModal(ord, 'order')">
                      <AppIcon name="eye" size="12" />
                      <span>Détails</span>
                    </AppButton>

                    <AppButton 
                      v-if="ord.status === 'BROUILLON' || ord.status === 'EN_ATTENTE'"
                      variant="success" 
                      size="xs" 
                      @click="changeOrderStatus(ord.id_order, 'VALIDEE')"
                    >
                      <AppIcon name="check" size="12" />
                      <span>Valider</span>
                    </AppButton>

                    <AppButton 
                      v-if="ord.status !== 'FACTUREE' && ord.status !== 'ANNULEE'"
                      variant="secondary" 
                      size="xs" 
                      @click="openInvoiceModalForOrder(ord)"
                    >
                      <AppIcon name="file-text" size="12" />
                      <span>Facturer</span>
                    </AppButton>

                    <AppButton 
                      v-if="ord.status !== 'ANNULEE' && ord.status !== 'FACTUREE'"
                      variant="danger" 
                      size="xs" 
                      @click="changeOrderStatus(ord.id_order, 'ANNULEE')"
                    >
                      <AppIcon name="x" size="12" />
                      <span>Annuler</span>
                    </AppButton>

                    <span v-if="ord.status === 'FACTUREE'" class="text-xs text-emerald-400 font-semibold ml-1">Facturée</span>
                    <span v-if="ord.status === 'ANNULEE'" class="text-xs text-rose-400 font-semibold ml-1">Annulée</span>
                  </div>
                </td>
              </tr>
              <tr v-if="orders.length === 0">
                <td colspan="9" class="text-center py-6 text-muted">Aucune commande client enregistrée.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab 2: Devis -->
      <div v-if="activeTab === 'quotes'" class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold color-primary flex items-center gap-2">
            <AppIcon name="file-text" size="20" />
            <span>Offres Commerciales & Devis Pro-Formas</span>
          </h3>
          <AppButton variant="primary" size="sm" @click="showQuoteModal = true">
            <AppIcon name="plus" size="14" />
            <span>Nouveau Devis</span>
          </AppButton>
        </div>

        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Réf. Devis</th>
                <th>Client</th>
                <th>Montant HT</th>
                <th>Montant TTC</th>
                <th>Statut</th>
                <th>Date Émission</th>
                <th>Actions ERP</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="q in quotes" :key="q.id_quote">
                <td class="font-bold color-primary">{{ q.quote_ref }}</td>
                <td class="font-semibold text-white">{{ q.customer_name }}</td>
                <td>{{ formatCurrency(q.total_amount_ht || q.total_amount_ttc / 1.2) }}</td>
                <td class="font-bold text-amber-400">{{ formatCurrency(q.total_amount_ttc) }}</td>
                <td><span class="badge badge-warning">{{ q.status }}</span></td>
                <td class="text-muted text-xs">{{ formatDate(q.created_at) }}</td>
                <td>
                  <div class="flex items-center gap-1">
                    <AppButton variant="ghost" size="xs" @click="openDetailModal(q, 'quote')">
                      <AppIcon name="eye" size="12" />
                      <span>Détails</span>
                    </AppButton>

                    <AppButton 
                      v-if="q.status !== 'ACCEPTE'"
                      variant="success" 
                      size="xs" 
                      @click="convertQuoteToOrder(q)"
                    >
                      <AppIcon name="check" size="12" />
                      <span>Convertir</span>
                    </AppButton>
                    <span v-else class="text-xs text-emerald-400 font-semibold ml-1">Converti</span>
                  </div>
                </td>
              </tr>
              <tr v-if="quotes.length === 0">
                <td colspan="7" class="text-center py-6 text-muted">Aucun devis créé.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>



      <!-- Tab 4: Clients -->
      <div v-if="activeTab === 'customers'" class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold color-primary flex items-center gap-2">
            <AppIcon name="users" size="20" />
            <span>Répertoire Général des Clients</span>
          </h3>
          <AppButton variant="primary" size="sm" @click="showCustomerModal = true">
            <AppIcon name="plus" size="14" />
            <span>Ajouter un Client</span>
          </AppButton>
        </div>

        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Raison Sociale</th>
                <th>Email / Tél</th>
                <th>Ville</th>
                <th>Conditions Règlement</th>
                <th>CA Généré</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in customers" :key="c.id_customer">
                <td class="font-bold color-primary">{{ c.code_client }}</td>
                <td class="font-semibold text-white">{{ c.name }}</td>
                <td class="text-xs">{{ c.email || c.phone || 'N/A' }}</td>
                <td class="text-xs">{{ c.city || 'Antananarivo' }}</td>
                <td><span class="badge badge-info">{{ c.payment_terms }}</span></td>
                <td class="font-bold color-success">{{ formatCurrency(c.total_revenue_generated) }}</td>
                <td><span class="badge badge-success">{{ c.status }}</span></td>
              </tr>
              <tr v-if="customers.length === 0">
                <td colspan="7" class="text-center py-6 text-muted">Aucun client répertorié.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </AppCard>

    <!-- Modal Nouveau Client -->
    <AppModal v-model="showCustomerModal" title="Nouveau Client Tiers" size="sm">
      <form @submit.prevent="handleCreateCustomer" class="space-y-4 text-xs">
        <AppInput
          id="cust-name"
          v-model="customerForm.name"
          label="Nom de l'entreprise / Raison Sociale *"
          placeholder="ex: Malagasy Enterprise"
          required
        />
        <AppInput
          id="cust-email"
          v-model="customerForm.email"
          label="Email de contact"
          placeholder="ex: contact@entreprise.mg"
        />
        <AppInput
          id="cust-phone"
          v-model="customerForm.phone"
          label="Téléphone"
          placeholder="ex: +261 34 00 000 00"
        />
        <AppInput
          id="cust-city"
          v-model="customerForm.city"
          label="Ville"
          placeholder="ex: Antananarivo"
        />
        <div>
          <label class="block text-slate-300 font-semibold mb-1">Conditions de Règlement *</label>
          <select v-model="customerForm.payment_terms" class="input" required>
            <option value="CASH">Comptant à la livraison</option>
            <option value="30_DAYS">30 jours fin de mois</option>
            <option value="60_DAYS">60 jours net</option>
          </select>
        </div>
      </form>
      <template #footer>
        <AppButton variant="ghost" @click="showCustomerModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleCreateCustomer">Enregistrer le Client</AppButton>
      </template>
    </AppModal>

    <!-- Modal Nouvelle Commande -->
    <AppModal v-model="showOrderModal" title="Nouvelle Commande Client (Multi-Produits)" size="lg">
      <form @submit.prevent="handleCreateOrder" class="space-y-4 text-xs">
        <div>
          <label class="block text-slate-300 font-semibold mb-1">Sélectionner le Client *</label>
          <select v-model="orderForm.customer_id" class="input" required>
            <option v-for="c in customers" :key="c.id_customer" :value="c.id_customer">
              {{ c.name }} ({{ c.code_client }})
            </option>
          </select>
        </div>

        <div class="border border-slate-700/60 rounded-lg p-3 bg-slate-800/40 space-y-3">
          <div class="flex justify-between items-center">
            <span class="font-semibold text-slate-200">Articles de la commande</span>
            <AppButton type="button" variant="secondary" size="xs" @click="addOrderLine">
              <AppIcon name="plus" size="12" />
              <span>Ajouter un produit</span>
            </AppButton>
          </div>

          <div v-for="(line, idx) in orderForm.items" :key="idx" class="grid grid-cols-12 gap-2 items-center bg-slate-900/50 p-2 rounded border border-slate-700/30">
            <div class="col-span-5">
              <label class="block text-[10px] text-muted mb-0.5" v-if="idx === 0">Produit SKU</label>
              <select v-model="line.product_id" class="input" @change="onOrderLineProductSelect(line)" required>
                <option v-for="p in products" :key="p.id_product" :value="p.id_product">
                  {{ p.reference }} — {{ p.label }} ({{ p.price }} €)
                </option>
              </select>
            </div>
            <div class="col-span-3">
              <label class="block text-[10px] text-muted mb-0.5" v-if="idx === 0">Quantité</label>
              <input v-model.number="line.quantity" type="number" min="1" class="input" placeholder="Qté" required />
            </div>
            <div class="col-span-3">
              <label class="block text-[10px] text-muted mb-0.5" v-if="idx === 0">PU HT (€)</label>
              <input v-model.number="line.unit_price" type="number" min="0" step="0.01" class="input" placeholder="Prix" required />
            </div>
            <div class="col-span-1 text-center pt-2">
              <button type="button" class="text-rose-400 hover:text-rose-300 font-bold p-1 text-sm" @click="removeOrderLine(idx)" v-if="orderForm.items.length > 1" title="Supprimer la ligne">
                ✕
              </button>
            </div>
          </div>

          <div class="flex justify-between items-center text-xs text-slate-300 pt-2 border-t border-slate-700/40">
            <span>Total HT : <strong class="text-amber-400">{{ formatCurrency(orderTotalHt) }}</strong></span>
            <span>Total TTC (TVA 20%) : <strong class="text-emerald-400 font-bold text-sm">{{ formatCurrency(orderTotalTtc) }}</strong></span>
          </div>
        </div>
      </form>
      <template #footer>
        <AppButton variant="ghost" @click="showOrderModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleCreateOrder">Créer la Commande</AppButton>
      </template>
    </AppModal>

    <!-- Modal Nouveau Devis -->
    <AppModal v-model="showQuoteModal" title="Créer un Devis Commercial (Multi-Produits)" size="lg">
      <form @submit.prevent="handleCreateQuote" class="space-y-4 text-xs">
        <div>
          <label class="block text-slate-300 font-semibold mb-1">Client Destinataire *</label>
          <select v-model="quoteForm.customer_id" class="input" required>
            <option v-for="c in customers" :key="c.id_customer" :value="c.id_customer">
              {{ c.name }} ({{ c.code_client }})
            </option>
          </select>
        </div>

        <div class="border border-slate-700/60 rounded-lg p-3 bg-slate-800/40 space-y-3">
          <div class="flex justify-between items-center">
            <span class="font-semibold text-slate-200">Articles du devis</span>
            <AppButton type="button" variant="secondary" size="xs" @click="addQuoteLine">
              <AppIcon name="plus" size="12" />
              <span>Ajouter un produit</span>
            </AppButton>
          </div>

          <div v-for="(line, idx) in quoteForm.items" :key="idx" class="grid grid-cols-12 gap-2 items-center bg-slate-900/50 p-2 rounded border border-slate-700/30">
            <div class="col-span-5">
              <label class="block text-[10px] text-muted mb-0.5" v-if="idx === 0">Produit SKU</label>
              <select v-model="line.product_id" class="input" @change="onQuoteLineProductSelect(line)" required>
                <option v-for="p in products" :key="p.id_product" :value="p.id_product">
                  {{ p.reference }} — {{ p.label }} ({{ p.price }} €)
                </option>
              </select>
            </div>
            <div class="col-span-3">
              <label class="block text-[10px] text-muted mb-0.5" v-if="idx === 0">Quantité</label>
              <input v-model.number="line.quantity" type="number" min="1" class="input" placeholder="Qté" required />
            </div>
            <div class="col-span-3">
              <label class="block text-[10px] text-muted mb-0.5" v-if="idx === 0">PU HT (€)</label>
              <input v-model.number="line.unit_price" type="number" min="0" step="0.01" class="input" placeholder="Prix" required />
            </div>
            <div class="col-span-1 text-center pt-2">
              <button type="button" class="text-rose-400 hover:text-rose-300 font-bold p-1 text-sm" @click="removeQuoteLine(idx)" v-if="quoteForm.items.length > 1" title="Supprimer la ligne">
                ✕
              </button>
            </div>
          </div>

          <div class="flex justify-between items-center text-xs text-slate-300 pt-2 border-t border-slate-700/40">
            <span>Total HT : <strong class="text-amber-400">{{ formatCurrency(quoteTotalHt) }}</strong></span>
            <span>Total TTC (TVA 20%) : <strong class="text-emerald-400 font-bold text-sm">{{ formatCurrency(quoteTotalTtc) }}</strong></span>
          </div>
        </div>
      </form>
      <template #footer>
        <AppButton variant="ghost" @click="showQuoteModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleCreateQuote">Générer le Devis</AppButton>
      </template>
    </AppModal>

    <!-- Modal Nouvelle Facture Client -->
    <AppModal v-model="showInvoiceModal" title="Émettre une Facture Client" size="sm">
      <form @submit.prevent="handleCreateInvoice" class="space-y-4 text-xs">
        <div>
          <label class="block text-slate-300 font-semibold mb-1">Sélectionner la Commande *</label>
          <select v-model="invoiceForm.order_id" class="input" required>
            <option v-for="o in availableOrdersForInvoice" :key="o.id_order" :value="o.id_order">
              {{ o.order_ref }} — {{ o.customer_name }} ({{ formatCurrency(o.total_amount_ttc) }})
            </option>
          </select>
        </div>

        <div>
          <label class="block text-slate-300 font-semibold mb-1">Mode de Règlement *</label>
          <select v-model="invoiceForm.payment_mode" class="input" required>
            <option value="VIREMENT">Virement Bancaire</option>
            <option value="CHEQUE">Chèque</option>
            <option value="ESPECES">Espèces</option>
            <option value="CB">Carte Bancaire</option>
          </select>
        </div>
      </form>
      <template #footer>
        <AppButton variant="ghost" @click="showInvoiceModal = false">Annuler</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleCreateInvoice">Valider la Facture</AppButton>
      </template>
    </AppModal>

    <!-- Modal Détails du Document (Commande / Devis / Facture) -->
    <AppModal v-model="showDetailModal" :title="'Détails du Document — ' + (selectedDetailItem?.order_ref || selectedDetailItem?.invoice_ref || selectedDetailItem?.quote_ref || 'Détails')" size="lg">
      <div v-if="selectedDetailItem" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-4 bg-slate-800/60 p-3 rounded-lg border border-slate-700/60">
          <div>
            <span class="text-muted block text-[11px]">Client Destinataire :</span>
            <strong class="text-white text-sm block mt-0.5">{{ selectedDetailItem.customer_name || 'Client' }}</strong>
          </div>
          <div class="text-right">
            <span class="text-muted block text-[11px]">Date :</span>
            <span class="text-slate-300">{{ formatDate(selectedDetailItem.created_at || selectedDetailItem.order_date) }}</span>
            <div class="mt-1">
              <span :class="['badge', getStatusBadgeClass(selectedDetailItem.status)]">{{ selectedDetailItem.status }}</span>
            </div>
          </div>
        </div>

        <div>
          <h4 class="font-semibold text-slate-200 mb-2 flex items-center gap-2">
            <AppIcon name="box" size="14" />
            <span>Articles de la Commande ({{ parsedDetailItems.length }} ligne(s))</span>
          </h4>
          <div class="table-responsive">
            <table class="table text-xs">
              <thead>
                <tr>
                  <th>Produit / Désignation</th>
                  <th class="text-right">Quantité</th>
                  <th class="text-right">Prix Unitaire HT</th>
                  <th class="text-right">Montant Total HT</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(it, idx) in parsedDetailItems" :key="idx">
                  <td class="font-semibold text-white">
                    {{ it.label || it.reference || ('Produit ID #' + (it.product_id || (idx + 1))) }}
                  </td>
                  <td class="text-right font-semibold">{{ it.quantity || 1 }}</td>
                  <td class="text-right">{{ formatCurrency(it.unit_price || 0) }}</td>
                  <td class="text-right font-bold text-amber-400">
                    {{ formatCurrency((it.quantity || 1) * (it.unit_price || 0)) }}
                  </td>
                </tr>
                <tr v-if="parsedDetailItems.length === 0">
                  <td colspan="4" class="text-center py-4 text-muted">
                    1 ligne forfaitaire enregistrée — Total HT : {{ formatCurrency(selectedDetailItem.total_amount_ht || selectedDetailItem.total_ht) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="flex justify-end gap-6 bg-slate-900/80 p-3 rounded-lg border border-slate-700/50 text-xs">
          <div><span class="text-muted">Total HT :</span> <strong class="text-white ml-2">{{ formatCurrency(selectedDetailItem.total_amount_ht || selectedDetailItem.total_ht) }}</strong></div>
          <div><span class="text-muted">TVA (20%) :</span> <strong class="text-slate-300 ml-2">{{ formatCurrency((selectedDetailItem.total_amount_ht || selectedDetailItem.total_ht) * 0.20) }}</strong></div>
          <div><span class="text-muted">Total TTC :</span> <strong class="text-emerald-400 text-sm ml-2 font-bold">{{ formatCurrency(selectedDetailItem.total_amount_ttc || selectedDetailItem.total_ttc) }}</strong></div>
        </div>
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="showDetailModal = false">Fermer</AppButton>
      </template>
    </AppModal>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import salesService from '../../services/salesService'
import productService from '../../services/productService'
import { exportToExcel } from '../../utils/excelExport'
import AppLayout from '../../layouts/AppLayout.vue'
import PageHeader from '../../components/ui/PageHeader.vue'
import AppCard from '../../components/ui/AppCard.vue'
import AppButton from '../../components/ui/AppButton.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import AppInput from '../../components/ui/AppInput.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppAlert from '../../components/ui/AppAlert.vue'

const activeTab = ref('sales')
const overview = ref({})
const orders = ref([])
const quotes = ref([])
const invoices = ref([])
const customers = ref([])
const products = ref([])

const showCustomerModal = ref(false)
const showOrderModal = ref(false)
const showQuoteModal = ref(false)
const showInvoiceModal = ref(false)
const showDetailModal = ref(false)
const selectedDetailItem = ref(null)
const saving = ref(false)

const pageError = ref('')
const pageSuccess = ref('')

const customerForm = ref({
  name: '', email: '', phone: '', city: '', payment_terms: '30_DAYS'
})

const orderForm = ref({
  customer_id: 1,
  items: [{ product_id: 1, quantity: 1, unit_price: 100.0 }]
})

const quoteForm = ref({
  customer_id: 1,
  items: [{ product_id: 1, quantity: 1, unit_price: 100.0 }]
})

const invoiceForm = ref({
  order_id: 1, payment_mode: 'VIREMENT'
})

const availableOrdersForInvoice = computed(() => {
  return orders.value.filter(o => o.status !== 'FACTUREE')
})

const orderTotalHt = computed(() => {
  return (orderForm.value.items || []).reduce((sum, it) => sum + ((it.quantity || 0) * (it.unit_price || 0)), 0)
})

const orderTotalTtc = computed(() => {
  return Math.round((orderTotalHt.value * 1.2 + Number.EPSILON) * 100) / 100
})

const quoteTotalHt = computed(() => {
  return (quoteForm.value.items || []).reduce((sum, it) => sum + ((it.quantity || 0) * (it.unit_price || 0)), 0)
})

const quoteTotalTtc = computed(() => {
  return Math.round((quoteTotalHt.value * 1.2 + Number.EPSILON) * 100) / 100
})

const parsedDetailItems = computed(() => {
  if (!selectedDetailItem.value) return []
  const raw = selectedDetailItem.value.items || selectedDetailItem.value.items_json
  if (Array.isArray(raw)) return raw
  if (typeof raw === 'string') {
    try { return JSON.parse(raw) } catch (e) { return [] }
  }
  return []
})

function addOrderLine() {
  const p = products.value[0] || {}
  orderForm.value.items.push({
    product_id: p.id_product || 1,
    quantity: 1,
    unit_price: p.price || 100.0
  })
}

function removeOrderLine(idx) {
  if (orderForm.value.items.length > 1) {
    orderForm.value.items.splice(idx, 1)
  }
}

function onOrderLineProductSelect(line) {
  const p = products.value.find(prod => prod.id_product === line.product_id)
  if (p) {
    line.unit_price = p.price || 100.0
  }
}

function addQuoteLine() {
  const p = products.value[0] || {}
  quoteForm.value.items.push({
    product_id: p.id_product || 1,
    quantity: 1,
    unit_price: p.price || 100.0
  })
}

function removeQuoteLine(idx) {
  if (quoteForm.value.items.length > 1) {
    quoteForm.value.items.splice(idx, 1)
  }
}

function onQuoteLineProductSelect(line) {
  const p = products.value.find(prod => prod.id_product === line.product_id)
  if (p) {
    line.unit_price = p.price || 100.0
  }
}

function openDetailModal(item, type) {
  selectedDetailItem.value = item
  showDetailModal.value = true
}

async function fetchData() {
  pageError.value = ''
  try {
    const [ovRes, ordRes, qRes, invRes, custRes, prodRes] = await Promise.all([
      salesService.getOverview().catch(() => ({ data: {} })),
      salesService.getOrders().catch(() => ({ data: [] })),
      salesService.getQuotes().catch(() => ({ data: [] })),
      salesService.getInvoices().catch(() => ({ data: [] })),
      salesService.getCustomers().catch(() => ({ data: [] })),
      productService.getProducts().catch(() => ({ data: [] }))
    ])

    overview.value = ovRes.data || {}
    orders.value = ordRes.data || []
    quotes.value = qRes.data || []
    invoices.value = invRes.data || []
    customers.value = custRes.data || []
    products.value = prodRes.data || []

    if (customers.value.length > 0) {
      orderForm.value.customer_id = customers.value[0].id_customer
      quoteForm.value.customer_id = customers.value[0].id_customer
    }
    if (products.value.length > 0) {
      const p = products.value[0]
      orderForm.value.items = [{ product_id: p.id_product, quantity: 1, unit_price: p.price || 100.0 }]
      quoteForm.value.items = [{ product_id: p.id_product, quantity: 1, unit_price: p.price || 100.0 }]
    }
    if (orders.value.length > 0) {
      invoiceForm.value.order_id = orders.value[0].id_order
    }
  } catch (e) {
    pageError.value = 'Erreur lors du chargement des données de vente.'
  }
}

async function handleCreateCustomer() {
  if (!customerForm.value.name) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    await salesService.createCustomer(customerForm.value)
    pageSuccess.value = 'Client enregistré avec succès !'
    showCustomerModal.value = false
    customerForm.value = { name: '', email: '', phone: '', city: '', payment_terms: '30_DAYS' }
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la création du client.'
  } finally {
    saving.value = false
  }
}

async function handleCreateOrder() {
  if (!orderForm.value.customer_id) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    await salesService.createOrder({
      customer_id: orderForm.value.customer_id,
      items: orderForm.value.items
    })
    pageSuccess.value = 'Commande client multi-produits créée avec succès !'
    showOrderModal.value = false
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la création de la commande.'
  } finally {
    saving.value = false
  }
}

async function handleCreateQuote() {
  if (!quoteForm.value.customer_id) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    await salesService.createQuote({
      customer_id: quoteForm.value.customer_id,
      items: quoteForm.value.items,
      total_amount_ttc: quoteTotalTtc.value
    })
    pageSuccess.value = 'Devis commercial multi-produits généré avec succès !'
    showQuoteModal.value = false
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la création du devis.'
  } finally {
    saving.value = false
  }
}

async function convertQuoteToOrder(quote) {
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    const itemDetail = quote.items && quote.items.length > 0
      ? quote.items.map(it => ({ product_id: it.product_id || 1, quantity: it.quantity || 1, unit_price: it.unit_price || 100 }))
      : [{ product_id: 1, quantity: 1, unit_price: quote.total_amount_ttc / 1.2 }]

    await salesService.createOrder({
      customer_id: quote.customer_id,
      quote_id: quote.id_quote,
      items: itemDetail
    })
    quote.status = 'ACCEPTE'
    pageSuccess.value = `Le devis ${quote.quote_ref} a été converti avec succès en Commande Client !`
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la conversion du devis.'
  } finally {
    saving.value = false
  }
}

function openInvoiceModalForOrder(ord) {
  invoiceForm.value.order_id = ord.id_order
  showInvoiceModal.value = true
}

async function changeOrderStatus(orderId, newStatus) {
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    await salesService.updateOrderStatus(orderId, newStatus)
    pageSuccess.value = `Commande mise à jour avec succès (nouveau statut : ${newStatus}) !`
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la modification du statut.'
  } finally {
    saving.value = false
  }
}

async function handleCreateInvoice() {
  if (!invoiceForm.value.order_id) return
  saving.value = true
  pageError.value = ''
  pageSuccess.value = ''
  try {
    await salesService.createInvoice({
      order_id: invoiceForm.value.order_id,
      payment_mode: invoiceForm.value.payment_mode
    })
    pageSuccess.value = 'Facture client émise et enregistrée comme payée !'
    showInvoiceModal.value = false
    await fetchData()
  } catch (e) {
    pageError.value = e.response?.data?.detail || 'Erreur lors de la création de la facture.'
  } finally {
    saving.value = false
  }
}

function handleExportExcel() {
  if (activeTab.value === 'orders') {
    const cols = [
      { header: 'Référence', key: 'order_ref' },
      { header: 'Client', key: 'customer_name' },
      { header: 'Lignes', key: 'items_count' },
      { header: 'Montant HT (€)', key: 'total_amount_ht' },
      { header: 'Montant TTC (€)', key: 'total_amount_ttc' },
      { header: 'Statut', key: 'status' },
      { header: 'Date', key: 'created_at', formatter: (val) => formatDate(val) }
    ]
    exportToExcel('commandes_ventes', 'Commandes Clients', cols, orders.value)
  } else if (activeTab.value === 'quotes') {
    const cols = [
      { header: 'Réf. Devis', key: 'quote_ref' },
      { header: 'Client', key: 'customer_name' },
      { header: 'Montant TTC (€)', key: 'total_amount_ttc' },
      { header: 'Statut', key: 'status' },
      { header: 'Date Émission', key: 'created_at', formatter: (val) => formatDate(val) }
    ]
    exportToExcel('devis_ventes', 'Devis Pro-Forma', cols, quotes.value)
  } else if (activeTab.value === 'invoices') {
    const cols = [
      { header: 'Réf. Facture', key: 'invoice_ref' },
      { header: 'Réf. Commande', key: 'order_ref' },
      { header: 'Client', key: 'customer_name' },
      { header: 'Montant TTC (€)', key: 'total_amount_ttc' },
      { header: 'Montant Payé (€)', key: 'amount_paid' },
      { header: 'Règlement', key: 'payment_mode' },
      { header: 'Statut', key: 'status' },
      { header: 'Date Émission', key: 'created_at', formatter: (val) => formatDate(val) }
    ]
    exportToExcel('factures_ventes', 'Factures Clients', cols, invoices.value)
  } else {
    const cols = [
      { header: 'Code Client', key: 'code_client' },
      { header: 'Raison Sociale', key: 'name' },
      { header: 'Email', key: 'email' },
      { header: 'Téléphone', key: 'phone' },
      { header: 'Ville', key: 'city' },
      { header: 'Conditions Règlement', key: 'payment_terms' },
      { header: 'CA Généré (€)', key: 'total_revenue_generated' },
      { header: 'Statut', key: 'status' }
    ]
    exportToExcel('referentiel_clients', 'Clients Tiers', cols, customers.value)
  }
}

function formatCurrency(val) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val || 0)
}

function formatDate(str) {
  if (!str) return '-'
  return new Date(str).toLocaleDateString('fr-FR')
}

function getStatusBadgeClass(st) {
  if (st === 'VALIDEE' || st === 'FACTUREE') return 'badge-success'
  if (st === 'EN_LIVRAISON') return 'badge-warning'
  return 'badge-info'
}

onMounted(fetchData)
</script>

<style scoped>
.tabs-header {
  display: flex;
  gap: var(--space-4);
}
.tab-btn {
  padding: 0.6rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-weight: 600;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}
.tab-btn--active {
  border-bottom-color: var(--color-primary);
  color: var(--color-primary);
}
</style>
