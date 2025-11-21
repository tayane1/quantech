import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class LayoutService {
  isMobileMenuOpen = signal<boolean>(false);

  toggleMobileMenu(): void {
    this.isMobileMenuOpen.update(value => !value);
  }

  openMobileMenu(): void {
    this.isMobileMenuOpen.set(true);
  }

  closeMobileMenu(): void {
    this.isMobileMenuOpen.set(false);
  }
}

