import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { JobPositionFormComponent } from '../job-position-form/job-position-form.component';
import { RecruitmentService } from '../../services/recruitment.service';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { JobPosition } from '../../../../core/models/recruitment.model';

@Component({
  selector: 'app-job-position-edit',
  standalone: true,
  imports: [CommonModule, JobPositionFormComponent, CardComponent, LoadingComponent],
  template: `
    <div class="job-position-edit">
      <div class="page-header">
        <h1>Modifier le poste</h1>
      </div>
      <app-loading *ngIf="loading()" message="Chargement..."></app-loading>
      <app-card *ngIf="!loading() && jobPosition()" [title]="'Modifier: ' + jobPosition()?.title">
        <app-job-position-form 
          [jobPosition]="jobPosition()!" 
          (saved)="onSaved($event)" 
          (cancelled)="onCancelled()">
        </app-job-position-form>
      </app-card>
    </div>
  `,
  styles: [`
    .job-position-edit {
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
export class JobPositionEditComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private recruitmentService = inject(RecruitmentService);

  jobPosition = signal<JobPosition | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadJobPosition(+id);
    }
  }

  loadJobPosition(id: number): void {
    this.loading.set(true);
    this.recruitmentService.getJobPosition(id).subscribe({
      next: (jobPosition) => {
        this.jobPosition.set(jobPosition);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading job position:', error);
        this.loading.set(false);
        this.router.navigate(['/recruitment/positions']);
      }
    });
  }

  onSaved(jobPosition: JobPosition): void {
    this.router.navigate(['/recruitment/positions', jobPosition.id]);
  }

  onCancelled(): void {
    const id = this.jobPosition()?.id;
    if (id) {
      this.router.navigate(['/recruitment/positions', id]);
    } else {
      this.router.navigate(['/recruitment/positions']);
    }
  }
}

