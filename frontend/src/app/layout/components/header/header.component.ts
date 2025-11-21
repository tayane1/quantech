import { Component, inject, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { LayoutService } from '../../../core/services/layout.service';
import { User } from '../../../core/models/user.model';
import { NotificationDropdownComponent } from '../../../shared/components/notification-dropdown/notification-dropdown.component';
import { MessageDropdownComponent } from '../../../shared/components/message-dropdown/message-dropdown.component';
import { getImageUrl } from '../../../core/utils/image.util';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, NotificationDropdownComponent, MessageDropdownComponent],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  private layoutService = inject(LayoutService);

  user = signal<User | null>(null);
  showUserMenu = signal(false);
  searchQuery = signal('');

  constructor() {
    effect(() => {
      this.user.set(this.authService.currentUser());
    });
  }

  toggleUserMenu(): void {
    this.showUserMenu.update(value => !value);
  }

  toggleMobileMenu(): void {
    this.layoutService.toggleMobileMenu();
  }

  onSearch(): void {
    // TODO: Implémenter la recherche
    console.log('Search:', this.searchQuery());
  }

  logout(): void {
    this.authService.logout();
  }

  getUserInitials(): string {
    const user = this.user();
    if (!user) return '';
    return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase();
  }

  getUserName(): string {
    const user = this.user();
    if (!user) return '';
    return user.full_name || `${user.first_name} ${user.last_name}`;
  }

  getUserImageUrl(): string | null {
    return getImageUrl(this.user()?.profile_picture);
  }
}

