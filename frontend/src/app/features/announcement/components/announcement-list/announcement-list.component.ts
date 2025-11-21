import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AnnouncementService } from '../../services/announcement.service';
import { Announcement } from '../../../../core/models/dashboard.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { DateUtil } from '../../../../core/utils/date.util';
import { AuthService } from '../../../../core/services/auth.service';
import { normalizeApiResponse } from '../../../../core/utils/api.util';

@Component({
  selector: 'app-announcement-list',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './announcement-list.component.html',
  styleUrls: ['./announcement-list.component.scss']
})
export class AnnouncementListComponent implements OnInit {
  private announcementService = inject(AnnouncementService);
  private authService = inject(AuthService);

  announcements = signal<Announcement[]>([]);
  loading = signal(true);
  canCreate = signal(false);

  ngOnInit(): void {
    this.checkPermissions();
    this.loadAnnouncements();
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canCreate.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager')
    );
  }

  loadAnnouncements(): void {
    this.loading.set(true);
    this.announcementService.getVisibleAnnouncements().subscribe({
      next: (response) => {
        const announcements = normalizeApiResponse<Announcement>(response);
        this.announcements.set(announcements);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading announcements:', error);
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.announcements.set([]);
        this.loading.set(false);
      }
    });
  }

  deleteAnnouncement(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette annonce ?')) {
      this.announcementService.deleteAnnouncement(id).subscribe({
        next: () => {
          this.loadAnnouncements();
        },
        error: (error) => {
          console.error('Error deleting announcement:', error);
        }
      });
    }
  }

  getRelativeTime(date: string): string {
    return DateUtil.getRelativeTime(date);
  }

  truncateContent(content?: string): string {
    if (!content) return '';
    const maxLength = 150;
    return content.length > maxLength ? content.slice(0, maxLength) + '...' : content;
  }
}

