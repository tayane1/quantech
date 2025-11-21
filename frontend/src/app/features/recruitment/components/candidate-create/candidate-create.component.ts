import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { CandidateFormComponent } from '../candidate-form/candidate-form.component';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { Candidate } from '../../../../core/models/recruitment.model';

@Component({
  selector: 'app-candidate-create',
  standalone: true,
  imports: [CommonModule, CandidateFormComponent, CardComponent],
  template: `
    <div class="candidate-create">
      <div class="page-header">
        <h1>Ajouter un candidat</h1>
      </div>
      <app-card title="Nouveau candidat">
        <app-candidate-form (saved)="onSaved($event)" (cancelled)="onCancelled()"></app-candidate-form>
      </app-card>
    </div>
  `,
  styles: [`
    .candidate-create {
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
export class CandidateCreateComponent {
  private router = inject(Router);

  onSaved(candidate: Candidate): void {
    this.router.navigate(['/recruitment/candidates', candidate.id]);
  }

  onCancelled(): void {
    this.router.navigate(['/recruitment/candidates']);
  }
}

