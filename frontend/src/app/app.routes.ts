import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/auth/components/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/components/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./layout/components/main-layout/main-layout.component').then(m => m.MainLayoutComponent),
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/components/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      {
        path: 'announcement',
        loadChildren: () => import('./features/announcement/announcement.routes').then(m => m.routes)
      },
      {
        path: 'employee',
        loadChildren: () => import('./features/employee/employee.routes').then(m => m.routes),
        canActivate: [roleGuard(['admin', 'hr_manager', 'manager'])]
      },
      {
        path: 'department',
        loadChildren: () => import('./features/department/department.routes').then(m => m.routes),
        canActivate: [roleGuard(['admin', 'hr_manager'])]
      },
      {
        path: 'recruitment',
        loadChildren: () => import('./features/recruitment/recruitment.routes').then(m => m.routes),
        canActivate: [roleGuard(['admin', 'hr_manager', 'recruiter'])]
      },
      {
        path: 'schedule',
        loadChildren: () => import('./features/schedule/schedule.routes').then(m => m.routes)
      },
      {
        path: 'support',
        loadChildren: () => import('./features/support/support.routes').then(m => m.routes)
      },
      {
        path: 'settings',
        loadChildren: () => import('./features/settings/settings.routes').then(m => m.routes),
        canActivate: [roleGuard(['admin', 'hr_manager'])]
      },
      {
        path: 'profile',
        loadChildren: () => import('./features/profile/profile.routes').then(m => m.routes)
      }
    ]
  },
  {
    path: '**',
    redirectTo: ''
  }
];
