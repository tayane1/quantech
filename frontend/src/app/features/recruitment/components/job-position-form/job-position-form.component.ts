import { Component, EventEmitter, Input, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RecruitmentService } from '../../services/recruitment.service';
import { DepartmentService } from '../../../department/services/department.service';
import { JobPosition, CreateJobPositionRequest, UpdateJobPositionRequest, JobPositionStatus } from '../../../../core/models/recruitment.model';
import { Department } from '../../../../core/models/department.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

/**
 * Composant de formulaire réutilisable pour la création/édition de postes d'emploi
 */
@Component({
  selector: 'app-job-position-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent],
  templateUrl: './job-position-form.component.html',
  styleUrls: ['./job-position-form.component.scss']
})
export class JobPositionFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private recruitmentService = inject(RecruitmentService);
  private departmentService = inject(DepartmentService);

  @Input() jobPosition?: JobPosition;
  @Output() saved = new EventEmitter<JobPosition>();
  @Output() cancelled = new EventEmitter<void>();

  form!: FormGroup;
  loading = false;
  error: string | null = null;
  departments: Department[] = [];

  readonly statusOptions: { value: JobPositionStatus; label: string }[] = [
    { value: 'open', label: 'Ouvert' },
    { value: 'closed', label: 'Fermé' },
    { value: 'on_hold', label: 'En attente' }
  ];

  ngOnInit(): void {
    this.initForm();
    this.loadDepartments();
    if (this.jobPosition) {
      this.populateForm();
    }
  }

  private initForm(): void {
    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.maxLength(200)]],
      description: ['', [Validators.required]],
      department: [null],
      status: ['open', [Validators.required]],
      urgency: [false]
    });
  }

  private populateForm(): void {
    if (this.jobPosition) {
      this.form.patchValue({
        title: this.jobPosition.title,
        description: this.jobPosition.description,
        department: this.jobPosition.department || null,
        status: this.jobPosition.status,
        urgency: this.jobPosition.urgency
      });
    }
  }

  private loadDepartments(): void {
    this.departmentService.getDepartments().subscribe({
      next: (response) => {
        // Gérer différents formats de réponse : paginée ou tableau direct
        if (response && typeof response === 'object') {
          if (Array.isArray(response)) {
            // Si la réponse est directement un tableau
            this.departments = response;
          } else if (response.results && Array.isArray(response.results)) {
            // Si la réponse est paginée avec results
            this.departments = response.results;
          } else {
            // Format inattendu
            console.warn('Unexpected response format for departments in job position form:', response);
            this.departments = [];
          }
        } else {
          this.departments = [];
        }
      },
      error: (error) => {
        console.error('Error loading departments:', error);
        this.departments = [];
      }
    });
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.loading = true;
      this.error = null;

      const formValue = this.form.value;
      const request$ = this.jobPosition
        ? this.recruitmentService.updateJobPosition(this.jobPosition.id, formValue as UpdateJobPositionRequest)
        : this.recruitmentService.createJobPosition(formValue as CreateJobPositionRequest);

      request$.subscribe({
        next: (jobPosition) => {
          this.loading = false;
          this.saved.emit(jobPosition);
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 
                       Object.values(err.error || {}).flat().join(', ') ||
                       'Erreur lors de la sauvegarde du poste';
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

