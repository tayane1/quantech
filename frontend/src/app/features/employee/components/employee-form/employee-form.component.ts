import { Component, EventEmitter, Input, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { EmployeeService } from '../../services/employee.service';
import { DepartmentService } from '../../../department/services/department.service';
import { Employee, CreateEmployeeRequest, UpdateEmployeeRequest, Gender, EmployeeStatus } from '../../../../core/models/employee.model';
import { Department } from '../../../../core/models/department.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

/**
 * Composant de formulaire réutilisable pour la création/édition d'employés
 * Couche Presentation - Gère uniquement l'affichage du formulaire
 */
@Component({
  selector: 'app-employee-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent],
  templateUrl: './employee-form.component.html',
  styleUrls: ['./employee-form.component.scss']
})
export class EmployeeFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private employeeService = inject(EmployeeService);
  private departmentService = inject(DepartmentService);

  @Input() employee?: Employee;
  @Output() saved = new EventEmitter<Employee>();
  @Output() cancelled = new EventEmitter<void>();

  form!: FormGroup;
  loading = false;
  error: string | null = null;
  departments: Department[] = [];
  profilePictureFile: File | null = null;
  profilePicturePreview: string | null = null;

  readonly genderOptions: { value: Gender; label: string }[] = [
    { value: 'M', label: 'Homme' },
    { value: 'F', label: 'Femme' },
    { value: 'O', label: 'Autre' }
  ];

  readonly statusOptions: { value: EmployeeStatus; label: string }[] = [
    { value: 'active', label: 'Actif' },
    { value: 'on_leave', label: 'En congé' },
    { value: 'inactive', label: 'Inactif' }
  ];

  ngOnInit(): void {
    this.initForm();
    this.loadDepartments();
    if (this.employee) {
      this.populateForm();
    }
  }

  private initForm(): void {
    const today = new Date().toISOString().split('T')[0];
    
    this.form = this.fb.group({
      first_name: ['', [Validators.required, Validators.maxLength(100)]],
      last_name: ['', [Validators.required, Validators.maxLength(100)]],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', [Validators.required, Validators.maxLength(20)]],
      date_of_birth: ['', [Validators.required]],
      gender: ['M', [Validators.required]],
      hire_date: [today, [Validators.required]],
      department: [null],
      position: [null],
      manager: [null],
      salary: [0, [Validators.required, Validators.min(0)]],
      status: ['active', [Validators.required]],
      address: ['', [Validators.required]],
      city: ['', [Validators.required, Validators.maxLength(100)]],
      country: ['', [Validators.required, Validators.maxLength(100)]],
      profile_picture: [null]
    });
  }

  private populateForm(): void {
    if (this.employee) {
      this.form.patchValue({
        first_name: this.employee.first_name,
        last_name: this.employee.last_name,
        email: this.employee.email,
        phone: this.employee.phone,
        date_of_birth: this.employee.date_of_birth.split('T')[0],
        gender: this.employee.gender,
        hire_date: this.employee.hire_date.split('T')[0],
        department: this.employee.department || null,
        position: this.employee.position || null,
        manager: this.employee.manager || null,
        salary: this.employee.salary,
        status: this.employee.status,
        address: this.employee.address,
        city: this.employee.city,
        country: this.employee.country
      });
      
      if (this.employee.profile_picture) {
        this.profilePicturePreview = this.employee.profile_picture;
      }
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
            console.warn('Unexpected response format for departments in form:', response);
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

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      
      // Valider la taille de l'image (max 5MB)
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (file.size > maxSize) {
        this.error = 'L\'image est trop volumineuse. Taille maximum : 5MB';
        input.value = ''; // Réinitialiser l'input
        return;
      }
      
      // Valider le type de fichier
      if (!file.type.startsWith('image/')) {
        this.error = 'Veuillez sélectionner une image valide';
        input.value = '';
        return;
      }
      
      this.error = null;
      this.profilePictureFile = file;
      
      // Créer une preview optimisée
      const reader = new FileReader();
      reader.onload = (e: any) => {
        // Compresser l'image pour la preview si elle est grande
        this.compressImage(file).then((compressedFile) => {
          const previewReader = new FileReader();
          previewReader.onload = (previewEvent: any) => {
            this.profilePicturePreview = previewEvent.target.result;
          };
          previewReader.readAsDataURL(compressedFile);
        }).catch(() => {
          // Si la compression échoue, utiliser l'image originale
          this.profilePicturePreview = e.target.result;
        });
      };
      reader.readAsDataURL(file);
    }
  }

  /**
   * Compresse une image pour réduire sa taille
   */
  private compressImage(file: File): Promise<File> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e: any) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const maxWidth = 800;
          const maxHeight = 800;
          let width = img.width;
          let height = img.height;

          // Calculer les nouvelles dimensions
          if (width > height) {
            if (width > maxWidth) {
              height = (height * maxWidth) / width;
              width = maxWidth;
            }
          } else {
            if (height > maxHeight) {
              width = (width * maxHeight) / height;
              height = maxHeight;
            }
          }

          canvas.width = width;
          canvas.height = height;

          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.drawImage(img, 0, 0, width, height);
            canvas.toBlob((blob) => {
              if (blob) {
                const compressedFile = new File([blob], file.name, {
                  type: file.type,
                  lastModified: Date.now()
                });
                // Utiliser le fichier compressé pour l'upload
                this.profilePictureFile = compressedFile;
                resolve(compressedFile);
              } else {
                reject(new Error('Compression failed'));
              }
            }, file.type, 0.8); // Qualité 80%
          } else {
            reject(new Error('Canvas context not available'));
          }
        };
        img.onerror = () => reject(new Error('Image load failed'));
        img.src = e.target.result;
      };
      reader.onerror = () => reject(new Error('File read failed'));
      reader.readAsDataURL(file);
    });
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.loading = true;
      this.error = null;

      const formValue = { ...this.form.value };
      if (this.profilePictureFile) {
        formValue.profile_picture = this.profilePictureFile;
      }

      const request$ = this.employee
        ? this.employeeService.updateEmployee(this.employee.id, formValue as UpdateEmployeeRequest)
        : this.employeeService.createEmployee(formValue as CreateEmployeeRequest);

      request$.subscribe({
        next: (employee) => {
          this.loading = false;
          // Mettre à jour la preview avec l'URL complète de l'image si disponible
          if (employee.profile_picture) {
            this.profilePicturePreview = employee.profile_picture;
          }
          this.saved.emit(employee);
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 
                       Object.values(err.error || {}).flat().join(', ') ||
                       'Erreur lors de la sauvegarde de l\'employé';
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
    if (field?.hasError('min')) {
      return 'La valeur doit être positive';
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.form.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}

