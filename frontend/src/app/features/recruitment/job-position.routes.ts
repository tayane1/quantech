import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/job-position-list/job-position-list.component').then(m => m.JobPositionListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./components/job-position-create/job-position-create.component').then(m => m.JobPositionCreateComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'recruiter'])]
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/job-position-edit/job-position-edit.component').then(m => m.JobPositionEditComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'recruiter'])]
  },
  {
    path: ':id',
    loadComponent: () => import('./components/job-position-detail/job-position-detail.component').then(m => m.JobPositionDetailComponent)
  }
];

