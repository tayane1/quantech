import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { Notification } from '../models/dashboard.model';

export interface NotificationListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Notification[];
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private api = inject(ApiService);

  getNotifications(params?: {
    unread?: boolean;
    limit?: number;
    page?: number;
  }): Observable<NotificationListResponse> {
    return this.api.get<NotificationListResponse>('users/user-notifications/', params);
  }

  getUnreadCount(): Observable<number> {
    return this.api.get<{ count: number }>('users/user-notifications/unread-count/').pipe(
      map(response => response.count || 0)
    );
  }

  markAsRead(id: number): Observable<Notification> {
    return this.api.post<Notification>(`users/user-notifications/${id}/mark-read/`, {});
  }

  markAllAsRead(): Observable<void> {
    return this.api.post<void>('users/user-notifications/mark-all-read/', {});
  }

  deleteNotification(id: number): Observable<void> {
    return this.api.delete<void>(`users/user-notifications/${id}/`);
  }
}

