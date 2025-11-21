import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RecruitmentService } from '../../services/recruitment.service';
import { JobPosition } from '../../../../core/models/recruitment.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';
import { normalizeApiResponse } from '../../../../core/utils/api.util';

@Component({
  selector: 'app-job-position-list',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './job-position-list.component.html',
  styleUrls: ['./job-position-list.component.scss']
})
export class JobPositionListComponent implements OnInit {
  private recruitmentService = inject(RecruitmentService);
  private authService = inject(AuthService);

  positions = signal<JobPosition[]>([]);
  loading = signal(true);
  canCreate = signal(false);

  ngOnInit(): void {
    this.checkPermissions();
    this.loadPositions();
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canCreate.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager' || user.role === 'recruiter')
    );
  }

  loadPositions(): void {
    this.loading.set(true);
    this.recruitmentService.getJobPositions().subscribe({
      next: (response) => {
        const positions = normalizeApiResponse<JobPosition>(response);
        this.positions.set(positions);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading positions:', error);
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.positions.set([]);
        this.loading.set(false);
      }
    });
  }

  deletePosition(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce poste ?')) {
      this.recruitmentService.deleteJobPosition(id).subscribe({
        next: () => {
          this.loadPositions();
        },
        error: (error) => {
          console.error('Error deleting position:', error);
          alert('Erreur lors de la suppression du poste');
        }
      });
    }
  }

  getStatusBadgeClass(status: string): string {
    const classes: Record<string, string> = {
      'open': 'badge-success',
      'closed': 'badge-secondary',
      'on_hold': 'badge-warning'
    };
    return classes[status] || 'badge-secondary';
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR');
  }
}

