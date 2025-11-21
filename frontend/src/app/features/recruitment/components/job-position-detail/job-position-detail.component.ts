import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { RecruitmentService } from '../../services/recruitment.service';
import { JobPosition, Candidate } from '../../../../core/models/recruitment.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-job-position-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './job-position-detail.component.html',
  styleUrls: ['./job-position-detail.component.scss']
})
export class JobPositionDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private recruitmentService = inject(RecruitmentService);
  private authService = inject(AuthService);

  jobPosition = signal<JobPosition | null>(null);
  candidates = signal<Candidate[]>([]);
  loading = signal(true);
  canEdit = signal(false);

  ngOnInit(): void {
    this.checkPermissions();
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadJobPosition(+id);
      this.loadCandidates(+id);
    }
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canEdit.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager' || user.role === 'recruiter')
    );
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

  loadCandidates(positionId: number): void {
    this.recruitmentService.getCandidatesByPosition(positionId).subscribe({
      next: (response) => {
        this.candidates.set(response.results || []);
      },
      error: (error) => {
        console.error('Error loading candidates:', error);
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
      'open': 'badge-success',
      'closed': 'badge-secondary',
      'on_hold': 'badge-warning'
    };
    return classes[status] || 'badge-secondary';
  }

  getStatusDisplay(status: string): string {
    const displays: Record<string, string> = {
      'open': 'Ouvert',
      'closed': 'Fermé',
      'on_hold': 'En attente'
    };
    return displays[status] || status;
  }

  getCandidateStatusBadgeClass(status: string): string {
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
}
