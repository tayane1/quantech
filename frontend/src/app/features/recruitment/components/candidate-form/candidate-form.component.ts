import { Component, EventEmitter, Input, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RecruitmentService } from '../../services/recruitment.service';
import { Candidate, CreateCandidateRequest, UpdateCandidateRequest, CandidateStatus } from '../../../../core/models/recruitment.model';
import { JobPosition } from '../../../../core/models/recruitment.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

/**
 * Composant de formulaire réutilisable pour la création/édition de candidats
 */
@Component({
  selector: 'app-candidate-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent],
  templateUrl: './candidate-form.component.html',
  styleUrls: ['./candidate-form.component.scss']
})
export class CandidateFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private recruitmentService = inject(RecruitmentService);

  @Input() candidate?: Candidate;
  @Output() saved = new EventEmitter<Candidate>();
  @Output() cancelled = new EventEmitter<void>();

  form!: FormGroup;
  loading = false;
  error: string | null = null;
  jobPositions: JobPosition[] = [];
  resumeFile: File | null = null;
  resumePreview: string | null = null;

  readonly statusOptions: { value: CandidateStatus; label: string }[] = [
    { value: 'applied', label: 'Candidature' },
    { value: 'screening', label: 'Sélection' },
    { value: 'interview', label: 'Entretien' },
    { value: 'offer', label: 'Offre' },
    { value: 'hired', label: 'Embauché' },
    { value: 'rejected', label: 'Rejeté' }
  ];

  ngOnInit(): void {
    this.initForm();
    this.loadJobPositions();
    if (this.candidate) {
      this.populateForm();
    }
  }

  private initForm(): void {
    this.form = this.fb.group({
      first_name: ['', [Validators.required, Validators.maxLength(100)]],
      last_name: ['', [Validators.required, Validators.maxLength(100)]],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', [Validators.required, Validators.maxLength(20)]],
      position: [null, [Validators.required]],
      status: [this.candidate?.status || 'applied', [Validators.required]],
      cover_letter: [''],
      notes: ['']
    });
  }

  private populateForm(): void {
    if (this.candidate) {
      this.form.patchValue({
        first_name: this.candidate.first_name,
        last_name: this.candidate.last_name,
        email: this.candidate.email,
        phone: this.candidate.phone,
        position: this.candidate.position,
        status: this.candidate.status,
        cover_letter: this.candidate.cover_letter || '',
        notes: this.candidate.notes || ''
      });
      
      if (this.candidate.resume) {
        this.resumePreview = this.candidate.resume;
      }
    }
  }

  private loadJobPositions(): void {
    this.recruitmentService.getOpenJobPositions().subscribe({
      next: (response) => {
        this.jobPositions = response.results || [];
      },
      error: (error) => {
        console.error('Error loading job positions:', error);
      }
    });
  }

  onResumeSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.resumeFile = input.files[0];
      if (this.resumeFile.type === 'application/pdf') {
        const reader = new FileReader();
        reader.onload = (e: any) => {
          this.resumePreview = e.target.result;
        };
        reader.readAsDataURL(this.resumeFile);
      } else {
        this.resumePreview = this.resumeFile.name;
      }
    }
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.loading = true;
      this.error = null;

      const formValue = { ...this.form.value };
      if (this.resumeFile) {
        formValue.resume = this.resumeFile;
      }

      const request$ = this.candidate
        ? this.recruitmentService.updateCandidate(this.candidate.id, formValue as UpdateCandidateRequest)
        : this.recruitmentService.createCandidate(formValue as CreateCandidateRequest);

      request$.subscribe({
        next: (candidate) => {
          this.loading = false;
          this.saved.emit(candidate);
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 
                       Object.values(err.error || {}).flat().join(', ') ||
                       'Erreur lors de la sauvegarde du candidat';
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
    if (field?.hasError('email')) {
      return 'Format d\'email invalide';
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

