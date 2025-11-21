import { Component, EventEmitter, Input, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { DepartmentService } from '../../services/department.service';
import { Department, CreateDepartmentRequest, UpdateDepartmentRequest } from '../../../../core/models/department.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-department-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent],
  templateUrl: './department-form.component.html',
  styleUrls: ['./department-form.component.scss']
})
export class DepartmentFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private departmentService = inject(DepartmentService);

  @Input() department?: Department;
  @Output() saved = new EventEmitter<Department>();
  @Output() cancelled = new EventEmitter<void>();

  form!: FormGroup;
  loading = false;
  error: string | null = null;

  ngOnInit(): void {
    this.initForm();
    if (this.department) {
      this.populateForm();
    }
  }

  private initForm(): void {
    this.form = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(200)]],
      code: ['', [Validators.required, Validators.maxLength(50), Validators.pattern(/^[A-Z0-9_-]+$/)]],
      description: [''],
      manager: [null],
      location: ['', [Validators.maxLength(200)]],
      budget: [0, [Validators.min(0)]]
    });
  }

  private populateForm(): void {
    if (this.department) {
      this.form.patchValue({
        name: this.department.name,
        code: this.department.code,
        description: this.department.description || '',
        manager: this.department.manager || null,
        location: this.department.location || '',
        budget: this.department.budget || 0
      });
    }
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.loading = true;
      this.error = null;

      const formValue = this.form.value;
      const request$ = this.department
        ? this.departmentService.updateDepartment(this.department.id, formValue as UpdateDepartmentRequest)
        : this.departmentService.createDepartment(formValue as CreateDepartmentRequest);

      request$.subscribe({
        next: (department) => {
          this.loading = false;
          this.saved.emit(department);
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 
                       Object.values(err.error || {}).flat().join(', ') ||
                       'Erreur lors de la sauvegarde du département';
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
    if (field?.hasError('min')) {
      return 'La valeur doit être positive';
    }
    if (field?.hasError('pattern')) {
      return 'Le code doit contenir uniquement des majuscules, chiffres, tirets et underscores';
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.form.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}

