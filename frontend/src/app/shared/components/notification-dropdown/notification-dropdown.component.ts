import { Component, OnInit, inject, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { NotificationService } from '../../../core/services/notification.service';
import { Notification } from '../../../core/models/dashboard.model';
import { DateUtil } from '../../../core/utils/date.util';
import { LoadingComponent } from '../loading/loading.component';
import { ClickOutsideDirective } from '../../directives/click-outside.directive';

@Component({
  selector: 'app-notification-dropdown',
  standalone: true,
  imports: [CommonModule, RouterModule, LoadingComponent, ClickOutsideDirective],
  templateUrl: './notification-dropdown.component.html',
  styleUrls: ['./notification-dropdown.component.scss']
})
export class NotificationDropdownComponent implements OnInit {
  private notificationService = inject(NotificationService);
  private router = inject(Router);

  notifications = signal<Notification[]>([]);
  unreadCount = signal<number>(0);
  loading = signal(false);
  showDropdown = signal(false);

  ngOnInit(): void {
    this.loadNotifications();
    this.loadUnreadCount();
  }

  toggleDropdown(): void {
    this.showDropdown.update(value => !value);
    if (this.showDropdown()) {
      this.loadNotifications();
    }
  }

  closeDropdown(): void {
    this.showDropdown.set(false);
  }

  loadNotifications(): void {
    this.loading.set(true);
    this.notificationService.getNotifications({ limit: 10, unread: false }).subscribe({
      next: (response) => {
        this.notifications.set(response.results || []);
        this.loading.set(false);
        this.loadUnreadCount();
      },
      error: (error) => {
        console.error('Error loading notifications:', error);
        this.loading.set(false);
      }
    });
  }

  loadUnreadCount(): void {
    this.notificationService.getUnreadCount().subscribe({
      next: (count) => {
        this.unreadCount.set(count);
      },
      error: (error) => {
        // Si l'endpoint n'existe pas encore, calculer depuis les notifications
        this.notificationService.getNotifications({ unread: true, limit: 1 }).subscribe({
          next: (response) => {
            this.unreadCount.set(response.count || 0);
          },
          error: () => {
            // Si les deux échouent, mettre à 0
            this.unreadCount.set(0);
          }
        });
      }
    });
  }

  markAsRead(notification: Notification, event: Event): void {
    event.stopPropagation();
    if (!notification.is_read) {
      this.notificationService.markAsRead(notification.id).subscribe({
        next: () => {
          notification.is_read = true;
          notification.read_at = new Date().toISOString();
          this.unreadCount.update(count => Math.max(0, count - 1));
        },
        error: (error) => {
          console.error('Error marking notification as read:', error);
        }
      });
    }
  }

  markAllAsRead(): void {
    this.notificationService.markAllAsRead().subscribe({
      next: () => {
        this.notifications.update(notifications =>
          notifications.map(n => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
        );
        this.unreadCount.set(0);
      },
      error: (error) => {
        console.error('Error marking all as read:', error);
      }
    });
  }

  deleteNotification(id: number, event: Event): void {
    event.stopPropagation();
    if (confirm('Supprimer cette notification ?')) {
      this.notificationService.deleteNotification(id).subscribe({
        next: () => {
          const notification = this.notifications().find(n => n.id === id);
          if (notification && !notification.is_read) {
            this.unreadCount.update(count => Math.max(0, count - 1));
          }
          this.notifications.update(notifications => notifications.filter(n => n.id !== id));
        },
        error: (error) => {
          console.error('Error deleting notification:', error);
        }
      });
    }
  }

  handleNotificationClick(notification: Notification): void {
    if (!notification.is_read) {
      this.markAsRead(notification, new Event('click'));
    }
    if (notification.related_link) {
      this.router.navigateByUrl(notification.related_link);
      this.closeDropdown();
    }
  }

  getRelativeTime(date: string): string {
    return DateUtil.getRelativeTime(date);
  }

  getNotificationIcon(type: string): string {
    switch (type) {
      case 'success':
        return 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z';
      case 'warning':
        return 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z';
      case 'error':
        return 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z';
      default:
        return 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z';
    }
  }

  getNotificationColor(type: string): string {
    switch (type) {
      case 'success':
        return '#28a745';
      case 'warning':
        return '#ffc107';
      case 'error':
        return '#dc3545';
      default:
        return '#17a2b8';
    }
  }
}

