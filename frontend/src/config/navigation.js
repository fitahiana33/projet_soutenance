/**
 * Navigation centralisée — Smart ERP
 * Les noms de menu correspondent exactement aux titres des pages (guide UX).
 * Chaque entrée inclut ses permissions RBAC pour le filtrage dynamique dans AppSidebar.
 */

export const navigationSections = [
  {
    header: "PILOTAGE & DÉCISION",
    items: [
      {
        name: "Tableau de bord",
        description: "Vue d'ensemble stratégique et KPIs",
        path: "/dashboard",
        icon: "dashboard",
        badge: null,
        permissions: ["DASHBOARD_READ"]
      }
    ]
  },
  {
    header: "ACHATS & LOGISTIQUE",
    items: [
      {
        name: "Achats & Approvisionnements",
        description: "Demandes, commandes, réceptions, factures fournisseurs",
        path: "/purchases",
        icon: "shopping-cart",
        badge: null,
        permissions: ["PURCHASE_READ", "PURCHASE_CREATE", "PURCHASE_UPDATE", "PURCHASE_VALIDATE"]
      },
      {
        name: "Suivi des Stocks",
        description: "Inventaire, mouvements, valorisation CUMP/FIFO",
        path: "/stocks",
        icon: "box",
        badge: null,
        permissions: ["STOCK_READ", "STOCK_UPDATE", "STOCK_MANAGE"]
      },
      {
        name: "Référentiel Produits",
        description: "Catalogue produits et catégories",
        icon: "package",
        badge: null,
        permissions: ["PRODUCT_READ", "CATEGORY_READ", "PRODUCT_CREATE"],
        children: [
          {
            name: "Catalogue Produits",
            path: "/products",
            icon: "package",
            permissions: ["PRODUCT_READ", "PRODUCT_CREATE"]
          },
          {
            name: "Catégories & Familles",
            path: "/products/categories",
            icon: "folder",
            permissions: ["CATEGORY_READ", "CATEGORY_CREATE"]
          }
        ]
      }
    ]
  },
  {
    header: "VENTES & CLIENTS",
    items: [
      {
        name: "Ventes & Commandes",
        description: "Devis, commandes clients, livraisons, facturation",
        path: "/sales",
        icon: "dollar-sign",
        badge: null,
        permissions: ["SALES_READ", "SALES_CREATE", "SALES_VALIDATE"]
      }
    ]
  },
  {
    header: "RESSOURCES HUMAINES",
    items: [
      {
        name: "Gestion RH & Paie",
        description: "Employés, congés, paie, évaluations",
        path: "/hr",
        icon: "users",
        badge: null,
        permissions: ["HR_READ", "EMPLOYEE_READ", "PAYROLL_READ", "HOLIDAY_READ"]
      },
      {
        name: "Recrutement & Talents",
        description: "Offres d'emploi, candidatures, scoring",
        path: "/recruitment",
        icon: "shield",
        badge: null,
        permissions: ["HR_READ", "HR_MANAGE"]
      }
    ]
  },
  {
    header: "GOUVERNANCE & SÉCURITÉ",
    items: [
      {
        name: "Annuaire Utilisateurs",
        description: "Comptes, statuts, attributions de rôles",
        path: "/users",
        icon: "users",
        badge: null,
        permissions: ["USER_READ", "USER_CREATE", "USER_UPDATE"]
      },
      {
        name: "Rôles & Habilitations",
        description: "Créer et administrer les rôles utilisateurs",
        path: "/roles",
        icon: "shield",
        badge: null,
        permissions: ["ROLE_READ", "ROLE_CREATE", "ROLE_UPDATE"]
      },
      {
        name: "Permissions Système",
        description: "Catalogue des droits d’accès par fonctionnalité",
        path: "/permissions",
        icon: "key",
        badge: null,
        permissions: ["ROLE_READ", "PERMISSION_MANAGE"]
      },
      {
        name: "Journal d'Audit",
        description: "Traçabilité des actions et événements",
        path: "/audit",
        icon: "clock",
        badge: null,
        permissions: ["AUDIT_READ"]
      }
    ]
  },
  {
    header: "SYSTÈME & CONFIGURATION",
    items: [
      {
        name: "Paramètres Système",
        description: "Règles métier, fiscalité, intégrations",
        path: "/system",
        icon: "settings",
        badge: null,
        permissions: ["SYSTEM_READ", "SYSTEM_MANAGE"]
      }
    ]
  }
]
