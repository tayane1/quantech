import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RecruitmentService } from '../../services/recruitment.service';
import { Candidate, CandidateStatus } from '../../../../core/models/recruitment.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';
import { normalizeApiResponse } from '../../../../core/utils/api.util';

@Component({
  selector: 'app-candidate-list',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './candidate-list.component.html',
  styleUrls: ['./candidate-list.component.scss']
})
export class CandidateListComponent implements OnInit {
  private recruitmentService = inject(RecruitmentService);
  private authService = inject(AuthService);

  candidates = signal<Candidate[]>([]);
  loading = signal(true);
  canCreate = signal(false);
  statusFilter = signal<CandidateStatus | 'all'>('all');

  ngOnInit(): void {
    this.checkPermissions();
    this.loadCandidates();
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canCreate.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager' || user.role === 'recruiter')
    );
  }

  loadCandidates(): void {
    this.loading.set(true);
    const params: any = {};
    if (this.statusFilter() !== 'all') {
      params.status = this.statusFilter();
    }

    this.recruitmentService.getCandidates(params).subscribe({
      next: (response) => {
        const candidates = normalizeApiResponse<Candidate>(response);
        this.candidates.set(candidates);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading candidates:', error);
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.candidates.set([]);
        this.loading.set(false);
      }
    });
  }

  onStatusFilterChange(status: CandidateStatus | 'all'): void {
    this.statusFilter.set(status);
    this.loadCandidates();
  }

  deleteCandidate(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce candidat ?')) {
      this.recruitmentService.deleteCandidate(id).subscribe({
        next: () => {
          this.loadCandidates();
        },
        error: (error) => {
          console.error('Error deleting candidate:', error);
          alert('Erreur lors de la suppression du candidat');
        }
      });
    }
  }

  getStatusBadgeClass(status: CandidateStatus): string {
    const classes: Record<CandidateStatus, string> = {
      'applied': 'badge-info',
      'screening': 'badge-warning',
      'interview': 'badge-primary',
      'offer': 'badge-success',
      'hired': 'badge-success',
      'rejected': 'badge-danger'
    };
    return classes[status] || 'badge-secondary';
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR');
  }
}

