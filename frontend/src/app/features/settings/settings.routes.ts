import { Routes } from '@angular/router';

export const SETTINGS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/settings-dashboard/settings-dashboard.component').then(m => m.SettingsDashboardComponent)
  },
  {
    path: 'email-templates',
    loadComponent: () => import('./components/email-templates-list/email-templates-list.component').then(m => m.EmailTemplatesListComponent)
  },
  {
    path: 'email-templates/new',
    loadComponent: () => import('./components/email-template-form/email-template-form.component').then(m => m.EmailTemplateFormComponent)
  },
  {
    path: 'email-templates/:id',
    loadComponent: () => import('./components/email-template-form/email-template-form.component').then(m => m.EmailTemplateFormComponent)
  }
];

export const routes = SETTINGS_ROUTES;

