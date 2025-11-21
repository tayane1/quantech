import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/schedule-list/schedule-list.component').then(m => m.ScheduleListComponent)
  },
  {
    path: 'tasks',
    loadChildren: () => import('./task.routes').then(m => m.routes)
  },
  {
    path: 'meetings',
    loadChildren: () => import('./meeting.routes').then(m => m.routes)
  }
];

