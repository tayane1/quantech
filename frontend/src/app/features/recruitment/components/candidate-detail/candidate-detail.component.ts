import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { RecruitmentService } from '../../services/recruitment.service';
import { Candidate, JobPosition } from '../../../../core/models/recruitment.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-candidate-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './candidate-detail.component.html',
  styleUrls: ['./candidate-detail.component.scss']
})
export class CandidateDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private recruitmentService = inject(RecruitmentService);
  private authService = inject(AuthService);

  candidate = signal<Candidate | null>(null);
  jobPosition = signal<JobPosition | null>(null);
  loading = signal(true);
  canEdit = signal(false);

  ngOnInit(): void {
    this.checkPermissions();
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadCandidate(+id);
    }
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canEdit.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager' || user.role === 'recruiter')
    );
  }

  loadCandidate(id: number): void {
    this.loading.set(true);
    this.recruitmentService.getCandidate(id).subscribe({
      next: (candidate) => {
        this.candidate.set(candidate);
        if (candidate.position) {
          this.loadJobPosition(candidate.position);
        }
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading candidate:', error);
        this.loading.set(false);
        this.router.navigate(['/recruitment/candidates']);
      }
    });
  }

  loadJobPosition(id: number): void {
    this.recruitmentService.getJobPosition(id).subscribe({
      next: (position) => {
        this.jobPosition.set(position);
      },
      error: (error) => {
        console.error('Error loading job position:', error);
      }
    });
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  getStatusBadgeClass(status: string): string {
    const classes: Record<string, string> = {
      'applied': 'badge-info',
      'screening': 'badge-warning',
      'interview': 'badge-primary',
      'offer': 'badge-success',
      'hired': 'badge-success',
      'rejected': 'badge-danger'
    };
    return classes[status] || 'badge-secondary';
  }

  getStatusDisplay(status: string): string {
    const displays: Record<string, string> = {
      'applied': 'Candidature',
      'screening': 'Sélection',
      'interview': 'Entretien',
      'offer': 'Offre',
      'hired': 'Embauché',
      'rejected': 'Rejeté'
    };
    return displays[status] || status;
  }

  downloadResume(): void {
    const resume = this.candidate()?.resume;
    if (resume) {
      window.open(resume, '_blank');
    }
  }
}
