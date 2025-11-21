import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { AnnouncementFormComponent } from '../announcement-form/announcement-form.component';
import { AnnouncementService } from '../../services/announcement.service';
import { Announcement } from '../../../../core/models/dashboard.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';

@Component({
  selector: 'app-announcement-edit',
  standalone: true,
  imports: [CommonModule, AnnouncementFormComponent, CardComponent, LoadingComponent],
  template: `
    <div class="announcement-edit">
      <app-loading *ngIf="loading()" message="Chargement..."></app-loading>
      <app-card *ngIf="!loading() && announcement()" title="Modifier l'annonce">
        <app-announcement-form
          [announcement]="announcement()!"
          (saved)="onSaved($event)"
          (cancelled)="onCancelled()"
        ></app-announcement-form>
      </app-card>
    </div>
  `,
  styles: [`
    .announcement-edit {
      max-width: 1000px;
      margin: 0 auto;
    }
  `]
})
export class AnnouncementEditComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private announcementService = inject(AnnouncementService);

  announcement = signal<Announcement | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadAnnouncement(+id);
    }
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

  onSaved(announcement: Announcement): void {
    this.router.navigate(['/announcement']);
  }

  onCancelled(): void {
    this.router.navigate(['/announcement']);
  }
}

