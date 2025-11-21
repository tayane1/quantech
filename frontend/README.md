# WeHR - Frontend Documentation

## 📋 Vue d'ensemble

Frontend Angular 21 pour l'application WeHR (Gestion des Ressources Humaines). Application responsive avec support Desktop, Tablette et Mobile, connectée au backend Django REST Framework.

## 🏗️ Architecture Clean en Couches

### Structure du projet

```
frontend/src/app/
├── core/                          # Couche Core (services de base, interceptors, guards)
│   ├── guards/                    # Guards de navigation
│   │   ├── auth.guard.ts
│   │   └── role.guard.ts
│   ├── interceptors/              # Interceptors HTTP
│   │   ├── jwt.interceptor.ts     # Gestion JWT automatique
│   │   └── error.interceptor.ts   # Gestion des erreurs
│   ├── models/                    # Interfaces TypeScript
│   │   ├── user.model.ts
│   │   └── dashboard.model.ts
│   ├── services/                  # Services de base
│   │   ├── api.service.ts         # Service HTTP générique
│   │   ├── auth.service.ts        # Service d'authentification
│   │   └── dashboard.service.ts  # Service dashboard
│   └── utils/                     # Utilitaires
│       └── date.util.ts
│
├── features/                      # Couche Features (modules fonctionnels)
│   ├── auth/                      # Module authentification
│   │   └── components/
│   │       └── login/
│   ├── dashboard/                 # Module dashboard
│   │   ├── components/
│   │   │   └── dashboard/
│   │   └── services/
│   ├── announcement/              # Module annonces
│   │   ├── components/
│   │   │   ├── announcement-form/    # Formulaire complet avec validation
│   │   │   ├── announcement-list/
│   │   │   ├── announcement-create/
│   │   │   └── announcement-edit/
│   │   ├── services/
│   │   │   └── announcement.service.ts
│   │   └── announcement.routes.ts
│   ├── employee/                  # Module employés
│   ├── department/                # Module départements
│   ├── recruitment/               # Module recrutement
│   ├── schedule/                  # Module planning
│   ├── support/                   # Module support
│   └── settings/                  # Module paramètres
│
├── shared/                        # Couche Shared (composants réutilisables)
│   └── components/
│       ├── button/
│       ├── card/
│       └── loading/
│
└── layout/                        # Couche Layout (structure de l'application)
    └── components/
        ├── header/                # Header responsive (Desktop/Tablette/Mobile)
        ├── sidebar/               # Sidebar responsive
        └── main-layout/           # Layout principal
```

## 🎨 Design Responsive

### Breakpoints

- **Mobile** : `max-width: 768px`
- **Tablette** : `769px - 1024px`
- **Desktop** : `min-width: 1025px` (prioritaire)

### Implémentation

Chaque composant de layout (Header, Sidebar) adapte son affichage selon la taille d'écran :

- **Mobile** : Menu hamburger, header compact, sidebar en overlay
- **Tablette** : Header avec logo et recherche, sidebar fixe
- **Desktop** : Layout complet avec sidebar fixe et header étendu

## 🔌 Connexion Backend

### Configuration

**Environment** (`src/environments/environment.ts`) :

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
};
```

### Services API

**ApiService** (`core/services/api.service.ts`) :

- Service HTTP générique avec gestion automatique des tokens JWT
- Méthodes : `get()`, `post()`, `put()`, `patch()`, `delete()`
- Headers automatiques avec token d'authentification

**AuthService** (`core/services/auth.service.ts`) :

- Gestion de l'authentification JWT
- Stockage des tokens (access + refresh)
- Gestion de l'utilisateur connecté (signals)
- Méthodes : `login()`, `logout()`, `refreshToken()`, `getUser()`

### Interceptors HTTP

**JWT Interceptor** :

- Ajoute automatiquement le token JWT à toutes les requêtes
- Rafraîchit automatiquement le token en cas d'erreur 401
- Déconnecte l'utilisateur si le refresh échoue

**Error Interceptor** :

- Gère les erreurs HTTP de manière centralisée
- Messages d'erreur utilisateur-friendly
- Logging des erreurs

### Guards

**AuthGuard** :

- Protège les routes nécessitant une authentification
- Redirige vers `/login` si non authentifié

**RoleGuard** :

- Protège les routes selon les rôles utilisateurs
- Vérifie les permissions avant d'accéder à une route

## 📝 Formulaire Complet - Announcement

### Composant `AnnouncementFormComponent`

**Fichier** : `features/announcement/components/announcement-form/`

**Fonctionnalités** :

- ✅ Validation complète des champs
- ✅ Validation conditionnelle (départements requis si `visible_to_all = false`)
- ✅ Gestion des erreurs avec messages clairs
- ✅ États de chargement
- ✅ Support création et édition
- ✅ Intégration avec le backend (POST/PATCH)

**Champs du formulaire** :

- Titre (requis, max 255 caractères)
- Contenu (requis)
- Visible par tous (checkbox)
- Départements (multi-select, requis si visible_to_all = false)
- Publier immédiatement (checkbox)

**Validation** :

```typescript
// Validation conditionnelle
this.form.get('visible_to_all')?.valueChanges.subscribe((visibleToAll) => {
  if (!visibleToAll) {
    departmentsControl?.setValidators([Validators.required, this.minLengthArray(1)]);
  } else {
    departmentsControl?.clearValidators();
  }
});
```

## 🎯 Composants Dashboard

### Métriques

**Cartes de métriques** :

- Available Position (orange)
- Job Open (bleu)
- New Employees (violet)
- Total Employees (avec graphique de tendance)
- Talent Request (avec graphique de tendance)

### Sections

**Announcements** :

- Liste des 3 dernières annonces visibles
- Affichage du temps relatif ("5 Minutes ago", "Yesterday")
- Actions (pin, menu)

**Recently Activity** :

- Carte bleue foncée avec activité récente
- Bouton "See All Activity"

**Upcoming Schedule** :

- Liste des rendez-vous à venir
- Catégories (Priority, Other)
- Date et heure

## 🛣️ Routing

### Routes principales

```typescript
/login                    # Page de connexion
/dashboard                # Dashboard principal
/announcement             # Liste des annonces
/announcement/create      # Créer une annonce (formulaire complet)
/announcement/:id/edit    # Modifier une annonce
/employee                 # Employés
/department               # Départements
/recruitment              # Recrutement
/schedule                 # Planning
/support                  # Support
/settings                 # Paramètres
```

### Lazy Loading

Toutes les routes utilisent le lazy loading pour optimiser les performances :

```typescript
loadComponent: () => import('./path/to/component').then((m) => m.ComponentName);
```

## 🔐 Sécurité

### Authentification JWT

- Tokens stockés dans `localStorage`
- Refresh automatique des tokens
- Déconnexion automatique si token invalide

### Protection des routes

- Routes protégées par `authGuard`
- Routes protégées par rôle avec `roleGuard`
- Vérification des permissions au niveau composant

## 📱 Responsive Design

### Header

**Mobile** :

- Label "Dashboard - Mobile"
- Menu hamburger
- Icônes compactes (search, notifications, chat, profil)

**Tablette** :

- Label "Dashboard - Tablet"
- Logo "WeHR"
- Barre de recherche
- Icônes + profil avec nom

**Desktop** :

- Label "Dashboard Desktop"
- Barre de recherche large
- Icônes + profil avec nom complet

### Sidebar

**Mobile** :

- Overlay avec menu slide-in
- Logo + bouton fermer
- Menu complet avec icônes

**Tablette/Desktop** :

- Sidebar fixe à gauche
- Logo en haut
- Menu avec icônes et labels
- État actif (highlight rouge)

## 🎨 Composants Partagés

### CardComponent

- Carte réutilisable avec header, body, footer
- Support pour couleurs personnalisées
- Slots pour actions et footer

### ButtonComponent

- Variantes : primary, secondary, outline
- États : loading, disabled
- Événements : clicked

### LoadingComponent

- Spinner avec message optionnel
- Réutilisable partout

## 📊 Gestion d'État

### Signals Angular

Utilisation des **Signals** (Angular 21) pour la réactivité :

```typescript
loading = signal(false);
announcements = signal<Announcement[]>([]);
currentUser = signal<User | null>(null);
```

### Services

- Services injectables avec `inject()`
- Observable-based pour les appels API
- Gestion d'état centralisée dans les services

## 🚀 Démarrage

### Installation

```bash
cd frontend
npm install
```

### Développement

```bash
npm start
# ou
ng serve
```

L'application sera accessible sur `http://localhost:4200`

### Build

```bash
npm run build
```

### Configuration Backend

Assurez-vous que le backend Django est démarré sur `http://localhost:8000`

Modifier l'URL dans `src/environments/environment.ts` si nécessaire.

## 🔧 Technologies et justifications

### Stack principale

| Technologie     | Version | Justification                                                                  |
| --------------- | ------- | ------------------------------------------------------------------------------ |
| **Angular**     | 21.0.0  | Framework moderne, SSR natif, Signals réactifs, standalone components          |
| **RxJS**        | 7.8.0   | Programmation réactive, gestion asynchrone (Observables), opérateurs puissants |
| **TypeScript**  | 5.9.2   | Typage statique, sécurité du code, autocomplétion, refactoring sûr             |
| **Express**     | 5.1.0   | Serveur SSR (Server-Side Rendering) pour SEO et performance                    |
| **Angular SSR** | 21.0.0  | Rendu côté serveur intégré, hydration automatique                              |

### Architecture Angular 21

**Standalone Components** : Tous les composants sont standalone (pas de NgModules)

- ✅ Moins de boilerplate
- ✅ Tree-shaking optimisé
- ✅ Lazy loading simplifié

**Signals** : Gestion d'état réactive moderne

```typescript
loading = signal(false);
announcements = signal<Announcement[]>([]);
```

**Inject Function** : Injection de dépendances moderne

```typescript
private api = inject(ApiService);
```

**SSR (Server-Side Rendering)** : Rendu côté serveur pour SEO et performance initiale

## ✅ Fonctionnalités Implémentées

### Modules (10+ features)

- ✅ **Auth** : Login, Register, 2FA
- ✅ **Dashboard** : Métriques, KPIs, activités
- ✅ **Announcement** : CRUD complet avec validation
- ✅ **Employee** : Gestion employés (list, detail, create, edit)
- ✅ **Department** : Gestion départements avec statistiques
- ✅ **Recruitment** : Offres, candidats, processus de recrutement
- ✅ **Schedule** : Planning, réunions, tâches
- ✅ **Support** : Tickets de support
- ✅ **Settings** : Paramètres système, templates emails
- ✅ **Profile** : Profil utilisateur, changement mot de passe

### ✅ Architecture Clean en Couches

- Séparation Core / Features / Shared / Layout
- Services injectables avec `inject()`
- Composants standalone (Angular 21)
- Models TypeScript pour type safety

### ✅ Design Responsive

- Header adaptatif (Mobile/Tablette/Desktop)
- Sidebar responsive avec overlay mobile
- Layout flexible avec breakpoints CSS
- Composants adaptatifs selon viewport

### ✅ Connexion Backend

- Service API générique (`ApiService`)
- Interceptors JWT (ajout token auto, refresh)
- Interceptor erreurs (gestion centralisée)
- Authentification complète (login, logout, refresh)

### ✅ Formulaire Complet

- `AnnouncementFormComponent` avec validation
- Validation conditionnelle (départements requis)
- Intégration backend (CRUD complet)
- Gestion des erreurs avec messages clairs

### ✅ Dashboard

- Cartes de métriques (Available Position, Job Open, etc.)
- Section annonces (3 dernières)
- Section activité récente
- Section planning à venir

### ✅ Routing & Navigation

- Routes configurées avec lazy loading
- Guards de protection (auth, role)
- Navigation par rôle
- Routes protégées par permissions

## 📊 Statistiques

- **10+ modules** fonctionnels
- **50+ composants** standalone
- **15+ services** injectables
- **10+ guards/interceptors** pour sécurité
- **Architecture modulaire** et scalable

## 🎯 Points Forts

1. **Architecture Clean** : Séparation claire Core/Features/Shared/Layout
2. **Responsive Design** : Adaptation parfaite Mobile/Tablette/Desktop
3. **Type Safety** : TypeScript strict avec interfaces complètes
4. **Réactivité** : Signals Angular 21 pour gestion d'état moderne
5. **Sécurité** : JWT auto, guards, validation, permissions
6. **Performance** : Lazy loading, SSR, tree-shaking optimisé
7. **Maintenabilité** : Code modulaire, standalone, documenté
8. **SSR** : Server-Side Rendering pour SEO et performance

## 📚 Structure des Features

Chaque feature suit la même structure :

```
feature/
├── components/          # Composants de la feature
├── services/           # Services spécifiques à la feature
└── feature.routes.ts  # Routes de la feature
```

## 🔄 Workflow de Développement

1. **Créer un service** dans `features/{feature}/services/`
2. **Créer les interfaces** dans `core/models/` si partagées
3. **Créer les composants** dans `features/{feature}/components/`
4. **Configurer les routes** dans `features/{feature}/{feature}.routes.ts`
5. **Ajouter au routing principal** dans `app.routes.ts`

## 📝 Exemples d'Utilisation

### Appel API

```typescript
constructor(private api: ApiService) {}

loadData(): void {
  this.api.get<MyData>('endpoint/').subscribe({
    next: (data) => console.log(data),
    error: (error) => console.error(error)
  });
}
```

### Utilisation d'un Guard

```typescript
{
  path: 'admin',
  canActivate: [roleGuard(['admin'])],
  loadComponent: () => import('./admin.component')
}
```

### Formulaire avec Validation

```typescript
this.form = this.fb.group({
  name: ['', [Validators.required, Validators.maxLength(100)]],
  email: ['', [Validators.required, Validators.email]],
});
```

---

**Développé avec Angular 21 et les meilleures pratiques de développement frontend**
