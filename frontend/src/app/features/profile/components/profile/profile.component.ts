import { Component, OnInit, inject, signal, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { User } from '../../../../core/models/user.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { getImageUrl } from '../../../../core/utils/image.util';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    CardComponent,
    ButtonComponent,
    LoadingComponent
  ],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  user = signal<User | null>(null);
  loading = signal(false);
  saving = signal(false);
  profileForm!: FormGroup;
  selectedFile: File | null = null;
  imagePreview: string | null = null;
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  ngOnInit(): void {
    this.initForm();
    this.loadUser();
  }

  initForm(): void {
    this.profileForm = this.fb.group({
      first_name: ['', [Validators.required]],
      last_name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      phone: [''],
      bio: ['']
    });
  }

  loadUser(): void {
    this.loading.set(true);
    this.authService.getUser().subscribe({
      next: (user) => {
        this.user.set(user);
        this.profileForm.patchValue({
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          email: user.email || '',
          phone: user.phone || '',
          bio: user.bio || ''
        });
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading user:', error);
        this.loading.set(false);
      }
    });
  }

  onSubmit(): void {
    if (this.profileForm.valid) {
      this.saving.set(true);
      const formData: any = {
        ...this.profileForm.value
      };
      
      // Ajouter la photo seulement si un nouveau fichier a été sélectionné
      if (this.selectedFile) {
        formData.profile_picture = this.selectedFile;
      }
      
      this.authService.updateUser(formData).subscribe({
        next: (updatedUser) => {
          this.user.set(updatedUser);
          this.selectedFile = null;
          this.imagePreview = null;
          if (this.fileInput) {
            this.fileInput.nativeElement.value = '';
          }
          this.saving.set(false);
        },
        error: (error) => {
          console.error('Error updating profile:', error);
          alert('Erreur lors de la mise à jour du profil');
          this.saving.set(false);
        }
      });
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      // Vérifier le type de fichier
      if (!file.type.startsWith('image/')) {
        alert('Veuillez sélectionner une image');
        return;
      }
      // Vérifier la taille (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('L\'image est trop volumineuse. Taille maximale : 5MB');
        return;
      }
      this.selectedFile = file;
      
      // Créer un aperçu
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imagePreview = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  deleteProfilePicture(): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer votre photo de profil ?')) {
      this.saving.set(true);
      this.authService.updateUser({ profile_picture: null }).subscribe({
        next: (updatedUser) => {
          this.user.set(updatedUser);
          this.selectedFile = null;
          this.imagePreview = null;
          if (this.fileInput) {
            this.fileInput.nativeElement.value = '';
          }
          this.saving.set(false);
        },
        error: (error) => {
          console.error('Error deleting profile picture:', error);
          alert('Erreur lors de la suppression de la photo');
          this.saving.set(false);
        }
      });
    }
  }

  getProfileImageUrl(): string | null {
    if (this.imagePreview) {
      return this.imagePreview;
    }
    return getImageUrl(this.user()?.profile_picture);
  }

  triggerFileInput(): void {
    if (this.fileInput?.nativeElement) {
      this.fileInput.nativeElement.click();
    }
  }

  getUserInitials(): string {
    const user = this.user();
    if (!user) return '';
    return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase();
  }

  getUserName(): string {
    const user = this.user();
    if (!user) return '';
    return user.full_name || `${user.first_name} ${user.last_name}`;
  }

  getFieldError(fieldName: string): string {
    const field = this.profileForm.get(fieldName);
    if (field?.hasError('required')) {
      return 'Ce champ est requis';
    }
    if (field?.hasError('email')) {
      return 'Email invalide';
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.profileForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}

