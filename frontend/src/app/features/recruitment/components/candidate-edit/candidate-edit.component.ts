import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { CandidateFormComponent } from '../candidate-form/candidate-form.component';
import { RecruitmentService } from '../../services/recruitment.service';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { Candidate } from '../../../../core/models/recruitment.model';

@Component({
  selector: 'app-candidate-edit',
  standalone: true,
  imports: [CommonModule, CandidateFormComponent, CardComponent, LoadingComponent],
  template: `
    <div class="candidate-edit">
      <div class="page-header">
        <h1>Modifier le candidat</h1>
      </div>
      <app-loading *ngIf="loading()" message="Chargement..."></app-loading>
      <app-card *ngIf="!loading() && candidate()" [title]="'Modifier: ' + (candidate()?.full_name || candidate()?.first_name + ' ' + candidate()?.last_name)">
        <app-candidate-form 
          [candidate]="candidate()!" 
          (saved)="onSaved($event)" 
          (cancelled)="onCancelled()">
        </app-candidate-form>
      </app-card>
    </div>
  `,
  styles: [`
    .candidate-edit {
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
export class CandidateEditComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private recruitmentService = inject(RecruitmentService);

  candidate = signal<Candidate | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadCandidate(+id);
    }
  }

  loadCandidate(id: number): void {
    this.loading.set(true);
    this.recruitmentService.getCandidate(id).subscribe({
      next: (candidate) => {
        this.candidate.set(candidate);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading candidate:', error);
        this.loading.set(false);
        this.router.navigate(['/recruitment/candidates']);
      }
    });
  }

  onSaved(candidate: Candidate): void {
    this.router.navigate(['/recruitment/candidates', candidate.id]);
  }

  onCancelled(): void {
    const id = this.candidate()?.id;
    if (id) {
      this.router.navigate(['/recruitment/candidates', id]);
    } else {
      this.router.navigate(['/recruitment/candidates']);
    }
  }
}

