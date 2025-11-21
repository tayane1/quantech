import { Routes } from '@angular/router';

export const SUPPORT_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/support-dashboard/support-dashboard.component').then(m => m.SupportDashboardComponent)
  },
  {
    path: 'tickets',
    loadComponent: () => import('./components/ticket-list/ticket-list.component').then(m => m.TicketListComponent)
  },
  {
    path: 'tickets/new',
    loadComponent: () => import('./components/ticket-create/ticket-create.component').then(m => m.TicketCreateComponent)
  },
  {
    path: 'tickets/:id',
    loadComponent: () => import('./components/ticket-detail/ticket-detail.component').then(m => m.TicketDetailComponent)
  }
];

export const routes = SUPPORT_ROUTES;

