import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { DashboardMetric, Announcement, Activity, Schedule, Notification } from '../models/dashboard.model';

export interface DashboardMetricsResponse {
  available_positions: number;
  urgent_positions: number;
  job_open: number;
  active_hiring: number;
  new_employees: number;
  departments_count: number;
  total_employees: number;
  men_count: number;
  women_count: number;
  employees_change: number;
  talent_requests: number;
  talent_men: number;
  talent_women: number;
  talent_change: number;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private api = inject(ApiService);

  getMetrics(): Observable<DashboardMetricsResponse> {
    return this.api.get<DashboardMetricsResponse>('dashboard/metrics/aggregated/');
  }

  getAnnouncements(params?: { published?: boolean; limit?: number }): Observable<{ results: Announcement[]; count: number }> {
    return this.api.get<{ results: Announcement[]; count: number }>('announcement/announcements/visible-to-me/', params);
  }

  getRecentActivities(limit: number = 10): Observable<Activity[]> {
    return this.api.get<Activity[]>('dashboard/activities/recent/', { limit });
  }

  getUpcomingSchedules(params?: { limit?: number; start_date?: string }): Observable<Schedule[]> {
    return this.api.get<Schedule[]>('schedule/tasks/upcoming/', params);
  }

  getNotifications(params?: { unread?: boolean; limit?: number }): Observable<{ results: Notification[]; count: number }> {
    return this.api.get<{ results: Notification[]; count: number }>('users/user-notifications/', params);
  }
}

