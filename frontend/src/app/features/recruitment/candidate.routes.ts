import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/candidate-list/candidate-list.component').then(m => m.CandidateListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./components/candidate-create/candidate-create.component').then(m => m.CandidateCreateComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'recruiter'])]
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/candidate-edit/candidate-edit.component').then(m => m.CandidateEditComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'recruiter'])]
  },
  {
    path: ':id',
    loadComponent: () => import('./components/candidate-detail/candidate-detail.component').then(m => m.CandidateDetailComponent)
  }
];

