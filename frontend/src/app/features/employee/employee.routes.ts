import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/employee-list/employee-list.component').then(m => m.EmployeeListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./components/employee-create/employee-create.component').then(m => m.EmployeeCreateComponent),
    canActivate: [roleGuard(['admin', 'hr_manager'])]
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/employee-edit/employee-edit.component').then(m => m.EmployeeEditComponent),
    canActivate: [roleGuard(['admin', 'hr_manager'])]
  },
  {
    path: ':id',
    loadComponent: () => import('./components/employee-detail/employee-detail.component').then(m => m.EmployeeDetailComponent)
  }
];

