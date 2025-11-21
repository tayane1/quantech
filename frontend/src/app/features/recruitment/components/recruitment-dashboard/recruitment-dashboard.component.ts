import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RecruitmentService } from '../../services/recruitment.service';
import { 
  JobPosition, 
  Candidate, 
  HiringProcess,
  RecruitmentStatistics 
} from '../../../../core/models/recruitment.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';
import { normalizeApiResponse } from '../../../../core/utils/api.util';

/**
 * Dashboard du module Recrutement
 * Couche Presentation - Affiche les statistiques et vues d'ensemble
 */
@Component({
  selector: 'app-recruitment-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './recruitment-dashboard.component.html',
  styleUrls: ['./recruitment-dashboard.component.scss']
})
export class RecruitmentDashboardComponent implements OnInit {
  private recruitmentService = inject(RecruitmentService);
  private authService = inject(AuthService);

  statistics = signal<RecruitmentStatistics | null>(null);
  openPositions = signal<JobPosition[]>([]);
  recentCandidates = signal<Candidate[]>([]);
  activeProcesses = signal<HiringProcess[]>([]);
  loading = signal(true);
  canCreate = signal(false);

  ngOnInit(): void {
    this.checkPermissions();
    this.loadData();
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canCreate.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager' || user.role === 'recruiter')
    );
  }

  loadData(): void {
    this.loading.set(true);
    
    // Charger les statistiques
    this.recruitmentService.getStatistics().subscribe({
      next: (stats) => {
        this.statistics.set(stats);
      },
      error: (error) => {
        console.error('Error loading statistics:', error);
      }
    });

    // Charger les postes ouverts
    this.recruitmentService.getOpenJobPositions().subscribe({
      next: (response) => {
        const positions = normalizeApiResponse<JobPosition>(response);
        this.openPositions.set(positions.slice(0, 5));
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading open positions:', error);
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.openPositions.set([]);
        this.loading.set(false);
      }
    });

    // Charger les candidats récents
    this.recruitmentService.getCandidates({ ordering: '-applied_date' }).subscribe({
      next: (response) => {
        const candidates = normalizeApiResponse<Candidate>(response);
        this.recentCandidates.set(candidates.slice(0, 5));
      },
      error: (error) => {
        console.error('Error loading recent candidates:', error);
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.recentCandidates.set([]);
      }
    });

    // Charger les processus actifs
    this.recruitmentService.getHiringProcesses({ stage__ne: 'rejected,closed' }).subscribe({
      next: (response) => {
        const processes = normalizeApiResponse<HiringProcess>(response);
        this.activeProcesses.set(processes.slice(0, 5));
      },
      error: (error) => {
        console.error('Error loading active processes:', error);
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.activeProcesses.set([]);
      }
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

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
}
