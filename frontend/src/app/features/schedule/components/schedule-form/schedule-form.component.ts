import { Component, EventEmitter, Input, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ScheduleService } from '../../services/schedule.service';
import { EmployeeService } from '../../../employee/services/employee.service';
import { Schedule, CreateScheduleRequest, UpdateScheduleRequest, SchedulePriority } from '../../../../core/models/schedule.model';
import { Employee } from '../../../../core/models/employee.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { AuthService } from '../../../../core/services/auth.service';

/**
 * Composant de formulaire réutilisable pour la création/édition de tâches
 */
@Component({
  selector: 'app-schedule-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent],
  templateUrl: './schedule-form.component.html',
  styleUrls: ['./schedule-form.component.scss']
})
export class ScheduleFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private scheduleService = inject(ScheduleService);
  private employeeService = inject(EmployeeService);
  private authService = inject(AuthService);

  @Input() schedule?: Schedule;
  @Output() saved = new EventEmitter<Schedule>();
  @Output() cancelled = new EventEmitter<void>();

  form!: FormGroup;
  loading = false;
  error: string | null = null;
  employees: Employee[] = [];

  readonly priorityOptions: { value: SchedulePriority; label: string }[] = [
    { value: 'low', label: 'Basse' },
    { value: 'medium', label: 'Moyenne' },
    { value: 'high', label: 'Élevée' }
  ];

  ngOnInit(): void {
    this.initForm();
    this.loadEmployees();
    if (this.schedule) {
      this.populateForm();
    } else {
      // Par défaut, assigner à soi-même si création
      const currentUser = this.authService.currentUser();
      if (currentUser) {
        // Tenter de charger l'employé associé à l'utilisateur
        this.loadCurrentEmployee(currentUser.id);
      }
    }
  }

  private initForm(): void {
    const now = new Date();
    now.setMinutes(0);
    const defaultDate = now.toISOString().slice(0, 16);

    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.maxLength(200)]],
      description: ['', [Validators.required]],
      assigned_to: [null, [Validators.required]],
      assigned_by: [null],
      priority: ['medium', [Validators.required]],
      scheduled_date: [defaultDate, [Validators.required]],
      completed: [false]
    });
  }

  private populateForm(): void {
    if (this.schedule) {
      const scheduledDate = new Date(this.schedule.scheduled_date);
      const dateTimeString = scheduledDate.toISOString().slice(0, 16);

      this.form.patchValue({
        title: this.schedule.title,
        description: this.schedule.description,
        assigned_to: this.schedule.assigned_to,
        assigned_by: this.schedule.assigned_by || null,
        priority: this.schedule.priority,
        scheduled_date: dateTimeString,
        completed: this.schedule.completed
      });
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
            console.warn('Unexpected response format for employees in schedule form:', response);
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

  private loadCurrentEmployee(userId: number): void {
    // Cette méthode devrait charger l'employé associé à l'utilisateur
    // Pour l'instant, on laisse null et l'utilisateur devra sélectionner
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.loading = true;
      this.error = null;

      const formValue = this.form.value;
      const scheduledDate = new Date(formValue.scheduled_date);
      formValue.scheduled_date = scheduledDate.toISOString();

      const request$ = this.schedule
        ? this.scheduleService.updateSchedule(this.schedule.id, formValue as UpdateScheduleRequest)
        : this.scheduleService.createSchedule(formValue as CreateScheduleRequest);

      request$.subscribe({
        next: (schedule) => {
          this.loading = false;
          this.saved.emit(schedule);
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 
                       Object.values(err.error || {}).flat().join(', ') ||
                       'Erreur lors de la sauvegarde de la tâche';
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

