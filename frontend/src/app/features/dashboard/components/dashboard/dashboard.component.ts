import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { DashboardService, DashboardMetricsResponse } from '../../services/dashboard.service';
import { Announcement, Activity, Schedule } from '../../../../core/models/dashboard.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { DateUtil } from '../../../../core/utils/date.util';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  private dashboardService = inject(DashboardService);

  loading = signal(true);
  metrics = signal<DashboardMetricsResponse | null>(null);
  announcements = signal<Announcement[]>([]);
  recentActivities = signal<Activity[]>([]);
  upcomingSchedules = signal<Schedule[]>([]);
  selectedDate = signal<string>(new Date().toISOString().split('T')[0]);

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.loading.set(true);
    
    // Charger les métriques
    this.dashboardService.getMetrics().subscribe({
      next: (data) => {
        this.metrics.set(data);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading metrics:', error);
        this.loading.set(false);
      }
    });

    // Charger les annonces (limiter à 3 pour l'affichage sur le dashboard)
    this.dashboardService.getAnnouncements({ limit: 3 }).subscribe({
      next: (response) => {
        console.log('Announcements response:', response);
        const announcementsList = response.results || [];
        // S'assurer de limiter à 3 annonces maximum pour l'affichage
        this.announcements.set(announcementsList.slice(0, 3));
      },
      error: (error) => {
        console.error('Error loading announcements:', error);
        console.error('Error details:', JSON.stringify(error, null, 2));
        this.announcements.set([]);
      }
    });

    // Charger les activités récentes
    this.dashboardService.getRecentActivities(10).subscribe({
      next: (activities) => {
        this.recentActivities.set(activities || []);
      },
      error: (error) => {
        console.error('Error loading recent activities:', error);
      }
    });

    // Charger les horaires à venir
    this.dashboardService.getUpcomingSchedules({ limit: 10 }).subscribe({
      next: (schedules) => {
        this.upcomingSchedules.set(schedules || []);
      },
      error: (error) => {
        console.error('Error loading upcoming schedules:', error);
      }
    });
  }

  getRelativeTime(date: string): string {
    return DateUtil.getRelativeTime(date);
  }

  formatDate(date: string): string {
    return DateUtil.formatDateShort(date);
  }

  formatDateTime(date: string): string {
    return DateUtil.formatDateTime(date);
  }

  formatActivityDateTime(date: string): string {
    return DateUtil.formatActivityDateTime(date);
  }

  formatScheduleTime(date: string): string {
    return DateUtil.formatScheduleTime(date);
  }

  getTodayActivitiesCount(): number {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return this.recentActivities().filter(activity => {
      const activityDate = new Date(activity.created_at);
      activityDate.setHours(0, 0, 0, 0);
      return activityDate.getTime() === today.getTime();
    }).length;
  }

  getPrioritySchedules(): Schedule[] {
    return this.upcomingSchedules().filter(schedule => schedule.priority === 'high');
  }

  getOtherSchedules(): Schedule[] {
    return this.upcomingSchedules().filter(schedule => schedule.priority !== 'high');
  }

  getActivityTitle(activity: Activity): string {
    const typeMap: { [key: string]: string } = {
      'job_posted': 'Vous avez posté un nouveau job',
      'candidate_applied': 'Un candidat a postulé',
      'employee_added': 'Un nouvel employé a été ajouté',
      'announcement_posted': 'Une annonce a été publiée',
      'schedule_created': 'Une tâche a été créée',
      'meeting_scheduled': 'Une réunion a été planifiée'
    };
    return typeMap[activity.activity_type] || activity.activity_type_display || 'Activité récente';
  }
}

