import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // Routes statiques peuvent être pré-rendues
  {
    path: '',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'login',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'register',
    renderMode: RenderMode.Prerender
  },
  // Routes dynamiques et protégées doivent être rendues côté serveur
  {
    path: '**',
    renderMode: RenderMode.Server
  }
];
