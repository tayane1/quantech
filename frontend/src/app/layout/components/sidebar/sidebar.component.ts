import { Component, inject, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';
import { LayoutService } from '../../../core/services/layout.service';

interface MenuItem {
  label: string;
  icon: string;
  route: string;
  roles?: string[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  private router = inject(Router);
  private authService = inject(AuthService);
  private layoutService = inject(LayoutService);

  currentRoute = signal<string>('');
  
  // Exposer le signal du service directement
  isMobileMenuOpen = this.layoutService.isMobileMenuOpen;

  mainMenuItems: MenuItem[] = [
    { label: 'Dashboard', icon: 'grid', route: '/dashboard', roles: ['admin', 'hr_manager', 'recruiter', 'manager', 'employee'] },
    { label: 'Annonces', icon: 'megaphone', route: '/announcement', roles: ['admin', 'hr_manager', 'recruiter', 'manager', 'employee'] },
    { label: 'Recruitment', icon: 'person', route: '/recruitment', roles: ['admin', 'hr_manager', 'recruiter'] },
    { label: 'Schedule', icon: 'calendar', route: '/schedule', roles: ['admin', 'hr_manager', 'manager', 'employee'] },
    { label: 'Employee', icon: 'people', route: '/employee', roles: ['admin', 'hr_manager', 'manager'] },
    { label: 'Department', icon: 'building', route: '/department', roles: ['admin', 'hr_manager'] }
  ];

  otherMenuItems: MenuItem[] = [
    { label: 'Support', icon: 'headphones', route: '/support', roles: ['admin', 'hr_manager', 'recruiter', 'manager', 'employee'] },
    { label: 'Settings', icon: 'settings', route: '/settings', roles: ['admin', 'hr_manager'] }
  ];

  constructor() {
    // Suivre la route actuelle
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: any) => {
        this.currentRoute.set(event.url);
      });

    // Initialiser la route actuelle
    this.currentRoute.set(this.router.url);
  }

  isActive(route: string): boolean {
    return this.currentRoute().startsWith(route);
  }

  canAccess(item: MenuItem): boolean {
    const user = this.authService.currentUser();
    if (!user) return false;
    if (!item.roles) return true;
    return item.roles.includes(user.role) || user.is_staff;
  }

  toggleMobileMenu(): void {
    this.layoutService.toggleMobileMenu();
  }

  closeMobileMenu(): void {
    this.layoutService.closeMobileMenu();
  }

  getIconPath(icon: string): string {
    // Pour l'instant, on utilise des SVG inline
    // Vous pouvez remplacer par des icônes d'une bibliothèque comme Material Icons
    return '';
  }
}

