import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MeetingFormComponent } from '../meeting-form/meeting-form.component';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { Meeting } from '../../../../core/models/schedule.model';

@Component({
  selector: 'app-meeting-create',
  standalone: true,
  imports: [CommonModule, MeetingFormComponent, CardComponent],
  template: `
    <div class="meeting-create">
      <div class="page-header">
        <h1>Créer une réunion</h1>
      </div>
      <app-card title="Nouvelle réunion">
        <app-meeting-form (saved)="onSaved($event)" (cancelled)="onCancelled()"></app-meeting-form>
      </app-card>
    </div>
  `,
  styles: [`
    .meeting-create {
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
export class MeetingCreateComponent {
  private router = inject(Router);

  onSaved(meeting: Meeting): void {
    this.router.navigate(['/schedule']);
  }

  onCancelled(): void {
    this.router.navigate(['/schedule']);
  }
}

