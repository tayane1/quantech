import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonComponent, RouterModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  loginForm: FormGroup;
  loading = signal(false);
  error = signal<string | null>(null);

  constructor() {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.loading.set(true);
      this.error.set(null);

      this.authService.login(this.loginForm.value).subscribe({
        next: () => {
          this.loading.set(false);
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          this.loading.set(false);
          
          // Si l'erreur est liée à un token invalide, nettoyer les tokens stockés
          if (err.status === 401 && err.error?.code === 'token_not_valid') {
            this.authService.logout();
          }
          
          let errorMessage = 'Erreur de connexion. Vérifiez vos identifiants.';
          
          if (err.error) {
            if (err.error.detail) {
              errorMessage = err.error.detail;
            } else if (err.error.message) {
              errorMessage = err.error.message;
            } else if (typeof err.error === 'string') {
              errorMessage = err.error;
            } else if (Array.isArray(err.error) && err.error.length > 0) {
              errorMessage = err.error.join(', ');
            } else if (typeof err.error === 'object') {
              const errorKeys = Object.keys(err.error);
              if (errorKeys.length > 0) {
                errorMessage = Object.values(err.error).flat().join(', ');
              }
            }
          } else if (err.message) {
            errorMessage = err.message;
          }
          
          console.error('Login error details:', {
            status: err.status,
            statusText: err.statusText,
            error: err.error,
            message: err.message,
            url: err.url
          });
          
          this.error.set(errorMessage);
        }
      });
    } else {
      this.markFormGroupTouched(this.loginForm);
    }
  }

  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.loginForm.get(fieldName);
    if (field?.hasError('required')) {
      return 'Ce champ est requis';
    }
    if (field?.hasError('minlength')) {
      return `Minimum ${field.errors?.['minlength'].requiredLength} caractères`;
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.loginForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}

