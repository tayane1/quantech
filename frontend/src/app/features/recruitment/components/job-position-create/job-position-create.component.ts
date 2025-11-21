import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { JobPositionFormComponent } from '../job-position-form/job-position-form.component';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { JobPosition } from '../../../../core/models/recruitment.model';

@Component({
  selector: 'app-job-position-create',
  standalone: true,
  imports: [CommonModule, JobPositionFormComponent, CardComponent],
  template: `
    <div class="job-position-create">
      <div class="page-header">
        <h1>Créer un poste</h1>
      </div>
      <app-card title="Nouveau poste d'emploi">
        <app-job-position-form (saved)="onSaved($event)" (cancelled)="onCancelled()"></app-job-position-form>
      </app-card>
    </div>
  `,
  styles: [`
    .job-position-create {
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
export class JobPositionCreateComponent {
  private router = inject(Router);

  onSaved(jobPosition: JobPosition): void {
    this.router.navigate(['/recruitment/positions', jobPosition.id]);
  }

  onCancelled(): void {
    this.router.navigate(['/recruitment/positions']);
  }
}

