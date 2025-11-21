import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AnnouncementFormComponent } from '../announcement-form/announcement-form.component';
import { Announcement } from '../../../../core/models/dashboard.model';
import { CardComponent } from '../../../../shared/components/card/card.component';

@Component({
  selector: 'app-announcement-create',
  standalone: true,
  imports: [CommonModule, AnnouncementFormComponent, CardComponent],
  template: `
    <div class="announcement-create">
      <app-card title="Créer une annonce">
        <app-announcement-form
          (saved)="onSaved($event)"
          (cancelled)="onCancelled()"
        ></app-announcement-form>
      </app-card>
    </div>
  `,
  styles: [`
    .announcement-create {
      max-width: 1000px;
      margin: 0 auto;
    }
  `]
})
export class AnnouncementCreateComponent {
  private router = inject(Router);

  onSaved(announcement: Announcement): void {
    this.router.navigate(['/announcement']);
  }

  onCancelled(): void {
    this.router.navigate(['/announcement']);
  }
}

