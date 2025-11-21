import { Component, EventEmitter, Input, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AnnouncementService, CreateAnnouncementRequest } from '../../services/announcement.service';
import { Announcement } from '../../../../core/models/dashboard.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { DepartmentService } from '../../../department/services/department.service';

@Component({
  selector: 'app-announcement-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent],
  templateUrl: './announcement-form.component.html',
  styleUrls: ['./announcement-form.component.scss']
})
export class AnnouncementFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private announcementService = inject(AnnouncementService);

  @Input() announcement?: Announcement;
  @Output() saved = new EventEmitter<Announcement>();
  @Output() cancelled = new EventEmitter<void>();

  form!: FormGroup;
  loading = false;
  departments: any[] = [];
  
  private departmentService = inject(DepartmentService);

  ngOnInit(): void {
    this.initForm();
    this.loadDepartments();
    if (this.announcement) {
      this.populateForm();
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
            console.warn('Unexpected response format for departments in announcement form:', response);
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

  private initForm(): void {
    this.form = this.fb.group({
      title: ['', [Validators.required, Validators.maxLength(255)]],
      content: ['', [Validators.required]],
      visible_to_all: [true],
      departments_ids: [[]],
      published: [true]
    });

    // Validation conditionnelle : si visible_to_all est false, au moins un département requis
    this.form.get('visible_to_all')?.valueChanges.subscribe(visibleToAll => {
      const departmentsControl = this.form.get('departments_ids');
      if (!visibleToAll) {
        departmentsControl?.setValidators([Validators.required, this.minLengthArray(1)]);
      } else {
        departmentsControl?.clearValidators();
      }
      departmentsControl?.updateValueAndValidity();
    });
  }

  private populateForm(): void {
    if (this.announcement) {
      this.form.patchValue({
        title: this.announcement.title,
        content: this.announcement.content,
        visible_to_all: this.announcement.visible_to_all,
        departments_ids: this.announcement.departments_ids || [],
        published: this.announcement.published
      });
    }
  }

  private minLengthArray(min: number) {
    return (control: any) => {
      if (!control.value || control.value.length < min) {
        return { minLengthArray: { requiredLength: min, actualLength: control.value?.length || 0 } };
      }
      return null;
    };
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.loading = true;
      const formValue: CreateAnnouncementRequest = this.form.value;

      const request$ = this.announcement
        ? this.announcementService.updateAnnouncement(this.announcement.id, formValue)
        : this.announcementService.createAnnouncement(formValue);

      request$.subscribe({
        next: (announcement) => {
          this.loading = false;
          this.saved.emit(announcement);
        },
        error: (error) => {
          this.loading = false;
          console.error('Error saving announcement:', error);
          // TODO: Afficher un message d'erreur
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

      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
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
    if (field?.hasError('minLengthArray')) {
      return 'Au moins un département doit être sélectionné';
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.form.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}

