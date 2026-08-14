/**
 * Configuration centralisée des modules et sous-menus de Smart ERP
 */

export const navigationItems = [
  {
    name: 'Tableau de bord',
    path: '/dashboard',
    icon: 'dashboard',
    badge: null
  },
  {
    name: 'Référentiel Produits',
    icon: 'package',
    badge: null,
    children: [
      {
        name: 'Gestion des Produits',
        path: '/products',
        icon: 'package'
      },
      {
        name: 'Catégories Produits',
        path: '/products/categories',
        icon: 'folder'
      }
    ]
  },
  {
    name: 'Gestion des Stocks',
    path: '/stocks',
    icon: 'box',
    badge: null
  },
  {
    name: 'Gestion des Achats',
    path: '/purchases',
    icon: 'shopping-cart',
    badge: 'Module 5 & 6'
  },
  {
    name: 'Ressources Humaines',
    path: '/hr',
    icon: 'users',
    badge: 'Module 8'
  },
  {
    name: 'Utilisateurs',
    path: '/users',
    icon: 'users',
    badge: 'Admin'
  },
  {
    name: 'Rôles & Permissions',
    path: '/roles',
    icon: 'shield',
    badge: null
  },
  {
    name: 'Intégration Dolibarr',
    path: '/dolibarr',
    icon: 'refresh',
    badge: 'Sync'
  },
  {
    name: 'Maintenance Système',
    path: '/system',
    icon: 'settings',
    badge: 'Purge'
  }
]
