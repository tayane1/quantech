import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/profile/profile.component').then(m => m.ProfileComponent)
  },
  {
    path: 'change-password',
    loadComponent: () => import('./components/change-password/change-password.component').then(m => m.ChangePasswordComponent)
  }
];

