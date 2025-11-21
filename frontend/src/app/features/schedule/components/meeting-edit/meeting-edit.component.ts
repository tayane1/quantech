import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MeetingFormComponent } from '../meeting-form/meeting-form.component';
import { ScheduleService } from '../../services/schedule.service';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { Meeting } from '../../../../core/models/schedule.model';

@Component({
  selector: 'app-meeting-edit',
  standalone: true,
  imports: [CommonModule, MeetingFormComponent, CardComponent, LoadingComponent],
  template: `
    <div class="meeting-edit">
      <div class="page-header">
        <h1>Modifier la réunion</h1>
      </div>
      <app-loading *ngIf="loading()" message="Chargement..."></app-loading>
      <app-card *ngIf="!loading() && meeting()" [title]="'Modifier: ' + meeting()?.title">
        <app-meeting-form 
          [meeting]="meeting()!" 
          (saved)="onSaved($event)" 
          (cancelled)="onCancelled()">
        </app-meeting-form>
      </app-card>
    </div>
  `,
  styles: [`
    .meeting-edit {
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
export class MeetingEditComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private scheduleService = inject(ScheduleService);

  meeting = signal<Meeting | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadMeeting(+id);
    }
  }

  loadMeeting(id: number): void {
    this.loading.set(true);
    this.scheduleService.getMeeting(id).subscribe({
      next: (meeting) => {
        this.meeting.set(meeting);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading meeting:', error);
        this.loading.set(false);
        this.router.navigate(['/schedule']);
      }
    });
  }

  onSaved(meeting: Meeting): void {
    this.router.navigate(['/schedule']);
  }

  onCancelled(): void {
    this.router.navigate(['/schedule']);
  }
}

