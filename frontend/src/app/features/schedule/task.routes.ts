import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/schedule',
    pathMatch: 'full'
  },
  {
    path: 'create',
    loadComponent: () => import('./components/task-create/task-create.component').then(m => m.TaskCreateComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'manager'])]
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/task-edit/task-edit.component').then(m => m.TaskEditComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'manager'])]
  }
];

