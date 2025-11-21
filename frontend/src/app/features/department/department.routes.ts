import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/department-list/department-list.component').then(m => m.DepartmentListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./components/department-create/department-create.component').then(m => m.DepartmentCreateComponent),
    canActivate: [roleGuard(['admin', 'hr_manager'])]
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/department-edit/department-edit.component').then(m => m.DepartmentEditComponent),
    canActivate: [roleGuard(['admin', 'hr_manager'])]
  },
  {
    path: ':id',
    loadComponent: () => import('./components/department-detail/department-detail.component').then(m => m.DepartmentDetailComponent)
  }
];

