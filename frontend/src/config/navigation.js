/**
 * Navigation centralisée de l'application Smart ERP pour Grande Entreprise
 */

export const navigationSections = [
  {
    header: "PILOTAGE & DECISION",
    items: [
      {
        name: "Tableau de bord Direction",
        path: "/dashboard",
        icon: "dashboard",
        badge: "KPI"
      }
    ]
  },
  {
    header: "ACHATS & LOGISTIQUE",
    items: [
      {
        name: "Achats & Approvisionnements",
        path: "/purchases",
        icon: "shopping-cart",
        badge: "Flux"
      },
      {
        name: "Stocks & Inventaires",
        path: "/stocks",
        icon: "box",
        badge: "CUMP/FIFO"
      },
      {
        name: "Référentiel Produits",
        icon: "package",
        badge: null,
        children: [
          {
            name: "Catalogue Produits",
            path: "/products",
            icon: "package"
          },
          {
            name: "Catégories & Familles",
            path: "/products/categories",
            icon: "folder"
          }
        ]
      }
    ]
  },
  {
    header: "VENTES & CLIENTS",
    items: [
      {
        name: "Ventes & Commandes Clients",
        path: "/sales",
        icon: "dollar-sign",
        badge: "CA"
      }
    ]
  },
  {
    header: "RESSOURCES HUMAINES",
    items: [
      {
        name: "Gestion RH & Paie",
        path: "/hr",
        icon: "users",
        badge: "Social"
      },
      {
        name: "Recrutement & Talents",
        path: "/recruitment",
        icon: "shield",
        badge: "Matching"
      }
    ]
  },
  {
    header: "GOUVERNANCE & AUDIT",
    items: [
      {
        name: "Annuaire Utilisateurs",
        path: "/users",
        icon: "users",
        badge: "RBAC"
      },
      {
        name: "Habilitations & Rôles",
        path: "/roles",
        icon: "shield",
        badge: null
      },
      {
        name: "Journal d'Audit",
        path: "/audit",
        icon: "clock",
        badge: "Sécurité"
      }
    ]
  },
  {
    header: "SYSTEME & PARAMETRAGE",
    items: [
      {
        name: "Réglages & Paramètres System",
        path: "/system",
        icon: "settings",
        badge: "Config"
      }
    ]
  }
]
