import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ScheduleService } from '../../services/schedule.service';
import { Schedule, Meeting } from '../../../../core/models/schedule.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';
import { normalizeApiResponse } from '../../../../core/utils/api.util';

/**
 * Composant de liste des tâches et réunions
 * Couche Presentation - Gère l'affichage du planning
 */
@Component({
  selector: 'app-schedule-list',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './schedule-list.component.html',
  styleUrls: ['./schedule-list.component.scss']
})
export class ScheduleListComponent implements OnInit {
  private scheduleService = inject(ScheduleService);
  private authService = inject(AuthService);

  schedules = signal<Schedule[]>([]);
  meetings = signal<Meeting[]>([]);
  loading = signal(true);
  canCreate = signal(false);

  // Filtres
  activeTab = signal<'tasks' | 'meetings'>('tasks');
  taskFilter = signal<'all' | 'pending' | 'completed'>('all');

  ngOnInit(): void {
    this.checkPermissions();
    this.loadData();
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canCreate.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager' || user.role === 'manager')
    );
  }

  loadData(): void {
    this.loading.set(true);

    // Charger les tâches
    const taskParams: any = {};
    if (this.taskFilter() === 'pending') {
      taskParams.completed = false;
    } else if (this.taskFilter() === 'completed') {
      taskParams.completed = true;
    }

    this.scheduleService.getSchedules(taskParams).subscribe({
      next: (response) => {
        const schedules = normalizeApiResponse<Schedule>(response);
        this.schedules.set(schedules);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading schedules:', error);
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.schedules.set([]);
        this.loading.set(false);
      }
    });

    // Charger les réunions à venir
    this.scheduleService.getUpcomingMeetings().subscribe({
      next: (response) => {
        const meetings = normalizeApiResponse<Meeting>(response);
        this.meetings.set(meetings);
      },
      error: (error) => {
        console.error('Error loading meetings:', error);
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.meetings.set([]);
      }
    });
  }

  onTabChange(tab: 'tasks' | 'meetings'): void {
    this.activeTab.set(tab);
  }

  onTaskFilterChange(filter: 'all' | 'pending' | 'completed'): void {
    this.taskFilter.set(filter);
    this.loadData();
  }

  toggleScheduleComplete(schedule: Schedule): void {
    this.scheduleService.updateSchedule(schedule.id, {
      completed: !schedule.completed
    }).subscribe({
      next: () => {
        this.loadData();
      },
      error: (error) => {
        console.error('Error updating schedule:', error);
      }
    });
  }

  deleteSchedule(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette tâche ?')) {
      this.scheduleService.deleteSchedule(id).subscribe({
        next: () => {
          this.loadData();
        },
        error: (error) => {
          console.error('Error deleting schedule:', error);
        }
      });
    }
  }

  deleteMeeting(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette réunion ?')) {
      this.scheduleService.deleteMeeting(id).subscribe({
        next: () => {
          this.loadData();
        },
        error: (error) => {
          console.error('Error deleting meeting:', error);
        }
      });
    }
  }

  getPriorityBadgeClass(priority: string): string {
    const classes: Record<string, string> = {
      'high': 'badge-danger',
      'medium': 'badge-warning',
      'low': 'badge-info'
    };
    return classes[priority] || 'badge-secondary';
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  isOverdue(scheduledDate: string, completed: boolean): boolean {
    if (completed) return false;
    return new Date(scheduledDate) < new Date();
  }
}
