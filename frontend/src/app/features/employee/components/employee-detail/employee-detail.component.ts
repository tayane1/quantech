import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { EmployeeService } from '../../services/employee.service';
import { Employee } from '../../../../core/models/employee.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';
import { CurrencyService } from '../../../../core/services/currency.service';
import { getImageUrl } from '../../../../core/utils/image.util';

@Component({
  selector: 'app-employee-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './employee-detail.component.html',
  styleUrls: ['./employee-detail.component.scss']
})
export class EmployeeDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private employeeService = inject(EmployeeService);
  private authService = inject(AuthService);
  private currencyService = inject(CurrencyService);

  employee = signal<Employee | null>(null);
  loading = signal(true);
  canEdit = signal(false);
  currency = signal<string>('XOF');

  ngOnInit(): void {
    this.checkPermissions();
    this.loadCurrency();
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadEmployee(+id);
    }
  }

  loadCurrency(): void {
    this.currencyService.getCurrency().subscribe({
      next: (currency) => {
        this.currency.set(currency);
      },
      error: () => {
        this.currency.set('XOF');
      }
    });
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canEdit.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager')
    );
  }

  loadEmployee(id: number): void {
    this.loading.set(true);
    this.employeeService.getEmployee(id).subscribe({
      next: (employee) => {
        this.employee.set(employee);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading employee:', error);
        this.loading.set(false);
        this.router.navigate(['/employee']);
      }
    });
  }

  formatSalary(salary: number): string {
    // Format avec FCFA au lieu du formatage automatique de devise
    return new Intl.NumberFormat('fr-FR', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(salary) + ' FCFA';
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  calculateAge(dateOfBirth: string): number {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  }

  getStatusBadgeClass(status: string): string {
    const classes: Record<string, string> = {
      'active': 'badge-success',
      'on_leave': 'badge-warning',
      'inactive': 'badge-secondary'
    };
    return classes[status] || 'badge-secondary';
  }

  getStatusDisplay(status: string): string {
    const displays: Record<string, string> = {
      'active': 'Actif',
      'on_leave': 'En congé',
      'inactive': 'Inactif'
    };
    return displays[status] || status;
  }

  hasSubordinates(): boolean {
    const count = this.employee()?.subordinates_count;
    return count !== undefined && count !== null && count > 0;
  }

  getEmployeeImageUrl(): string | null {
    return getImageUrl(this.employee()?.profile_picture);
  }

  deleteProfilePicture(): void {
    const employee = this.employee();
    if (!employee) return;

    if (confirm('Êtes-vous sûr de vouloir supprimer la photo de profil ?')) {
      this.employeeService.deleteEmployeeProfilePicture(employee.id).subscribe({
        next: (updatedEmployee) => {
          this.employee.set(updatedEmployee);
        },
        error: (error) => {
          console.error('Error deleting profile picture:', error);
          alert('Erreur lors de la suppression de la photo');
        }
      });
    }
  }
}

