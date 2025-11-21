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
    loadComponent: () => import('./components/meeting-create/meeting-create.component').then(m => m.MeetingCreateComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'manager'])]
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/meeting-edit/meeting-edit.component').then(m => m.MeetingEditComponent),
    canActivate: [roleGuard(['admin', 'hr_manager', 'manager'])]
  }
];

