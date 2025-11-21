import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CardComponent, ButtonComponent],
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss']
})
export class ChangePasswordComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  router = inject(Router);

  passwordForm: FormGroup;
  saving = signal(false);
  error = signal<string | null>(null);
  success = signal(false);

  constructor() {
    this.passwordForm = this.fb.group({
      old_password: ['', [Validators.required]],
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      confirm_password: ['', [Validators.required]]
    }, {
      validators: this.passwordMatchValidator
    });
  }

  passwordMatchValidator(form: FormGroup): { [key: string]: boolean } | null {
    const newPassword = form.get('new_password');
    const confirmPassword = form.get('confirm_password');
    
    if (newPassword && confirmPassword && newPassword.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    
    return null;
  }

  onSubmit(): void {
    if (this.passwordForm.valid) {
      this.saving.set(true);
      this.error.set(null);
      this.success.set(false);

      // TODO: Implémenter le changement de mot de passe via l'API
      const { old_password, new_password } = this.passwordForm.value;
      
      setTimeout(() => {
        this.saving.set(false);
        this.success.set(true);
        setTimeout(() => {
          this.router.navigate(['/profile']);
        }, 2000);
      }, 1000);
    }
  }

  getFieldError(fieldName: string): string {
    const field = this.passwordForm.get(fieldName);
    if (field?.hasError('required')) {
      return 'Ce champ est requis';
    }
    if (field?.hasError('minlength')) {
      return `Minimum ${field.errors?.['minlength'].requiredLength} caractères`;
    }
    return '';
  }

  getFormError(): string {
    if (this.passwordForm.hasError('passwordMismatch')) {
      return 'Les mots de passe ne correspondent pas';
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.passwordForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}

