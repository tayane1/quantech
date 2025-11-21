import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/announcement-list/announcement-list.component').then(m => m.AnnouncementListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./components/announcement-create/announcement-create.component').then(m => m.AnnouncementCreateComponent),
    canActivate: [roleGuard(['admin', 'hr_manager'])]
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/announcement-edit/announcement-edit.component').then(m => m.AnnouncementEditComponent),
    canActivate: [roleGuard(['admin', 'hr_manager'])]
  },
  {
    path: ':id',
    loadComponent: () => import('./components/announcement-detail/announcement-detail.component').then(m => m.AnnouncementDetailComponent)
  }
];

