import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ScheduleFormComponent } from '../schedule-form/schedule-form.component';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { Schedule } from '../../../../core/models/schedule.model';

@Component({
  selector: 'app-task-create',
  standalone: true,
  imports: [CommonModule, ScheduleFormComponent, CardComponent],
  template: `
    <div class="task-create">
      <div class="page-header">
        <h1>Créer une tâche</h1>
      </div>
      <app-card title="Nouvelle tâche">
        <app-schedule-form (saved)="onSaved($event)" (cancelled)="onCancelled()"></app-schedule-form>
      </app-card>
    </div>
  `,
  styles: [`
    .task-create {
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
export class TaskCreateComponent {
  private router = inject(Router);

  onSaved(schedule: Schedule): void {
    this.router.navigate(['/schedule']);
  }

  onCancelled(): void {
    this.router.navigate(['/schedule']);
  }
}

