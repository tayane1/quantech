import { Component, EventEmitter, Input, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ScheduleService } from '../../services/schedule.service';
import { EmployeeService } from '../../../employee/services/employee.service';
import { Meeting, CreateMeetingRequest, UpdateMeetingRequest } from '../../../../core/models/schedule.model';
import { Employee } from '../../../../core/models/employee.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { AuthService } from '../../../../core/services/auth.service';

/**
 * Composant de formulaire réutilisable pour la création/édition de réunions
 */
@Component({
  selector: 'app-meeting-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent],
  templateUrl: './meeting-form.component.html',
  styleUrls: ['./meeting-form.component.scss']
})
export class MeetingFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private scheduleService = inject(ScheduleService);
  private employeeService = inject(EmployeeService);
  private authService = inject(AuthService);

  @Input() meeting?: Meeting;
  @Output() saved = new EventEmitter<Meeting>();
  @Output() cancelled = new EventEmitter<void>();

  form!: FormGroup;
  loading = false;
  error: string | null = null;
  employees: Employee[] = [];
  selectedAttendees: number[] = [];

  ngOnInit(): void {
    this.initForm();
    this.loadEmployees();
    if (this.meeting) {
      this.populateForm();
    } else {
      // Par défaut, l'utilisateur connecté est l'organisateur
      const currentUser = this.authService.currentUser();
      if (currentUser) {
        // Cette logique devrait charger l'employé associé à l'utilisateur
      }
    }
  }

  private initForm(): void {
    const now = new Date();
    now.setMinutes(0);
    const defaultStart = now.toISOString().slice(0, 16);
    const defaultEnd = new Date(now.getTime() + 60 * 60 * 1000).toISOString().slice(0, 16);

    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.maxLength(200)]],
      description: ['', [Validators.required]],
      organizer: [null],
      attendees: [[]],
      start_time: [defaultStart, [Validators.required]],
      end_time: [defaultEnd, [Validators.required]],
      location: [''],
      video_conference_link: ['']
    });
  }

  private populateForm(): void {
    if (this.meeting) {
      const startTime = new Date(this.meeting.start_time);
      const endTime = new Date(this.meeting.end_time);
      const startString = startTime.toISOString().slice(0, 16);
      const endString = endTime.toISOString().slice(0, 16);

      this.form.patchValue({
        title: this.meeting.title,
        description: this.meeting.description,
        organizer: this.meeting.organizer || null,
        attendees: this.meeting.attendees || [],
        start_time: startString,
        end_time: endString,
        location: this.meeting.location || '',
        video_conference_link: this.meeting.video_conference_link || ''
      });
      this.selectedAttendees = this.meeting.attendees || [];
    }
  }

  private loadEmployees(): void {
    this.employeeService.getActiveEmployees().subscribe({
      next: (response) => {
        // Gérer différents formats de réponse : paginée ou tableau direct
        if (response && typeof response === 'object') {
          if (Array.isArray(response)) {
            // Si la réponse est directement un tableau
            this.employees = response;
          } else if (response.results && Array.isArray(response.results)) {
            // Si la réponse est paginée avec results
            this.employees = response.results;
          } else {
            // Format inattendu
            console.warn('Unexpected response format for employees in meeting form:', response);
            this.employees = [];
          }
        } else {
          this.employees = [];
        }
      },
      error: (error) => {
        console.error('Error loading employees:', error);
        this.employees = [];
      }
    });
  }

  onAttendeeToggle(employeeId: number): void {
    const index = this.selectedAttendees.indexOf(employeeId);
    if (index > -1) {
      this.selectedAttendees.splice(index, 1);
    } else {
      this.selectedAttendees.push(employeeId);
    }
    this.form.patchValue({ attendees: this.selectedAttendees });
  }

  isAttendeeSelected(employeeId: number): boolean {
    return this.selectedAttendees.includes(employeeId);
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.loading = true;
      this.error = null;

      const formValue = this.form.value;
      const startTime = new Date(formValue.start_time);
      const endTime = new Date(formValue.end_time);
      
      formValue.start_time = startTime.toISOString();
      formValue.end_time = endTime.toISOString();
      formValue.attendees = this.selectedAttendees;

      const request$ = this.meeting
        ? this.scheduleService.updateMeeting(this.meeting.id, formValue as UpdateMeetingRequest)
        : this.scheduleService.createMeeting(formValue as CreateMeetingRequest);

      request$.subscribe({
        next: (meeting) => {
          this.loading = false;
          this.saved.emit(meeting);
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 
                       Object.values(err.error || {}).flat().join(', ') ||
                       'Erreur lors de la sauvegarde de la réunion';
        }
      });
    } else {
      this.markFormGroupTouched(this.form);
    }
  }

  onCancel(): void {
    this.cancelled.emit();
  }

  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.form.get(fieldName);
    if (field?.hasError('required')) {
      return 'Ce champ est requis';
    }
    if (field?.hasError('maxlength')) {
      return `Maximum ${field.errors?.['maxlength'].requiredLength} caractères`;
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.form.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}

