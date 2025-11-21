import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ScheduleFormComponent } from '../schedule-form/schedule-form.component';
import { ScheduleService } from '../../services/schedule.service';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { Schedule } from '../../../../core/models/schedule.model';

@Component({
  selector: 'app-task-edit',
  standalone: true,
  imports: [CommonModule, ScheduleFormComponent, CardComponent, LoadingComponent],
  template: `
    <div class="task-edit">
      <div class="page-header">
        <h1>Modifier la tâche</h1>
      </div>
      <app-loading *ngIf="loading()" message="Chargement..."></app-loading>
      <app-card *ngIf="!loading() && schedule()" [title]="'Modifier: ' + schedule()?.title">
        <app-schedule-form 
          [schedule]="schedule()!" 
          (saved)="onSaved($event)" 
          (cancelled)="onCancelled()">
        </app-schedule-form>
      </app-card>
    </div>
  `,
  styles: [`
    .task-edit {
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
    }
    .page-header {
      margin-bottom: 30px;
      h1 {
        margin: 0;
        font-size: 2rem;
        color: #333;
      }
    }
  `]
})
export class TaskEditComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private scheduleService = inject(ScheduleService);

  schedule = signal<Schedule | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadSchedule(+id);
    }
  }

  loadSchedule(id: number): void {
    this.loading.set(true);
    this.scheduleService.getSchedule(id).subscribe({
      next: (schedule) => {
        this.schedule.set(schedule);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading schedule:', error);
        this.loading.set(false);
        this.router.navigate(['/schedule']);
      }
    });
  }

  onSaved(schedule: Schedule): void {
    this.router.navigate(['/schedule']);
  }

  onCancelled(): void {
    this.router.navigate(['/schedule']);
  }
}

