import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent, RouterModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  registerForm: FormGroup;
  loading = signal(false);
  error = signal<string | null>(null);

  constructor() {
    this.registerForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      first_name: ['', [Validators.required]],
      last_name: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      password_confirm: ['', [Validators.required]],
      role: ['employee']
    }, {
      validators: this.passwordMatchValidator
    });
  }

  passwordMatchValidator(form: FormGroup): { [key: string]: boolean } | null {
    const password = form.get('password');
    const passwordConfirm = form.get('password_confirm');
    
    if (password && passwordConfirm && password.value !== passwordConfirm.value) {
      return { passwordMismatch: true };
    }
    
    return null;
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.loading.set(true);
      this.error.set(null);

      const formValue = { ...this.registerForm.value };
      // Supprimer password_confirm car le backend n'en a pas besoin
      delete formValue.password_confirm;

      this.authService.register(formValue).subscribe({
        next: () => {
          this.loading.set(false);
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          this.loading.set(false);
          const errorMessage = err.error?.detail || 
                             err.error?.message || 
                             Object.values(err.error || {}).flat().join(', ') ||
                             'Erreur lors de l\'inscription. Veuillez réessayer.';
          this.error.set(errorMessage);
        }
      });
    } else {
      this.markFormGroupTouched(this.registerForm);
    }
  }

  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.registerForm.get(fieldName);
    if (field?.hasError('required')) {
      return 'Ce champ est requis';
    }
    if (field?.hasError('email')) {
      return 'Format d\'email invalide';
    }
    if (field?.hasError('minlength')) {
      return `Minimum ${field.errors?.['minlength'].requiredLength} caractères`;
    }
    return '';
  }

  getFormError(): string {
    if (this.registerForm.hasError('passwordMismatch')) {
      return 'Les mots de passe ne correspondent pas';
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.registerForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}

