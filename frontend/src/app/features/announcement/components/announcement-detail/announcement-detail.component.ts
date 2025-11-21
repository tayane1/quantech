import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AnnouncementService } from '../../services/announcement.service';
import { Announcement } from '../../../../core/models/dashboard.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { DateUtil } from '../../../../core/utils/date.util';
import { AuthService } from '../../../../core/services/auth.service';

/**
 * Composant de détail d'une annonce
 */
@Component({
  selector: 'app-announcement-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './announcement-detail.component.html',
  styleUrls: ['./announcement-detail.component.scss']
})
export class AnnouncementDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  public router = inject(Router); // Public pour accès dans le template
  private announcementService = inject(AnnouncementService);
  private authService = inject(AuthService);

  announcement = signal<Announcement | null>(null);
  loading = signal(true);
  canEdit = signal(false);

  ngOnInit(): void {
    this.checkPermissions();
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadAnnouncement(+id);
    }
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canEdit.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager')
    );
  }

  loadAnnouncement(id: number): void {
    this.loading.set(true);
    this.announcementService.getAnnouncement(id).subscribe({
      next: (announcement) => {
        this.announcement.set(announcement);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading announcement:', error);
        this.loading.set(false);
        this.router.navigate(['/announcement']);
      }
    });
  }

  deleteAnnouncement(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette annonce ?')) {
      this.announcementService.deleteAnnouncement(id).subscribe({
        next: () => {
          this.router.navigate(['/announcement']);
        },
        error: (error) => {
          console.error('Error deleting announcement:', error);
          alert('Erreur lors de la suppression de l\'annonce');
        }
      });
    }
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getRelativeTime(date: string): string {
    return DateUtil.getRelativeTime(date);
  }

  hasDepartments(): boolean {
    const depts = this.announcement()?.departments_names;
    return !!(depts && depts.length > 0);
  }
}

