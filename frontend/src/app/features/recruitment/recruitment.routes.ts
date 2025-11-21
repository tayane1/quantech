import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/recruitment-dashboard/recruitment-dashboard.component').then(m => m.RecruitmentDashboardComponent)
  },
  {
    path: 'positions',
    loadChildren: () => import('./job-position.routes').then(m => m.routes)
  },
  {
    path: 'candidates',
    loadChildren: () => import('./candidate.routes').then(m => m.routes)
  },
  {
    path: 'processes',
    loadChildren: () => import('./hiring-process.routes').then(m => m.routes)
  }
];

