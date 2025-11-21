import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/hiring-process-list/hiring-process-list.component').then(m => m.HiringProcessListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./components/hiring-process-create/hiring-process-create.component').then(m => m.HiringProcessCreateComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'recruiter'])]
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/hiring-process-edit/hiring-process-edit.component').then(m => m.HiringProcessEditComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'recruiter'])]
  },
  {
    path: ':id',
    loadComponent: () => import('./components/hiring-process-detail/hiring-process-detail.component').then(m => m.HiringProcessDetailComponent)
  }
];

