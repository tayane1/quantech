import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { 
  Employee, 
  CreateEmployeeRequest, 
  UpdateEmployeeRequest,
  EmployeeStatistics
} from '../../../core/models/employee.model';
import { PaginatedResponse } from '../../../core/interfaces/api.interface';

/**
 * Service pour la gestion des employés
 * Couche Application - Gère toutes les opérations CRUD et métier
 */
@Injectable({
  providedIn: 'root'
})
export class EmployeeService {
  private api = inject(ApiService);

  /**
   * Récupère la liste paginée des employés
   */
  getEmployees(params?: any): Observable<PaginatedResponse<Employee>> {
    return this.api.get<PaginatedResponse<Employee>>('employee/employees/', params);
  }

  /**
   * Récupère un employé par son ID
   */
  getEmployee(id: number): Observable<Employee> {
    return this.api.get<Employee>(`employee/employees/${id}/`);
  }

  /**
   * Crée un nouvel employé
   */
  createEmployee(data: CreateEmployeeRequest): Observable<Employee> {
    // Si une image est fournie, utiliser FormData
    if (data.profile_picture instanceof File) {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        if (key === 'profile_picture' && data.profile_picture instanceof File) {
          formData.append(key, data.profile_picture);
        } else if (data[key as keyof CreateEmployeeRequest] !== undefined) {
          const value = data[key as keyof CreateEmployeeRequest];
          if (value !== null && value !== undefined) {
            if (typeof value === 'object' && !(value instanceof File)) {
              formData.append(key, JSON.stringify(value));
            } else {
              formData.append(key, String(value));
            }
          }
        }
      });
      return this.api.postFormData<Employee>('employee/employees/', formData);
    }
    return this.api.post<Employee>('employee/employees/', data);
  }

  /**
   * Met à jour un employé existant
   */
  updateEmployee(id: number, data: UpdateEmployeeRequest): Observable<Employee> {
    if (data.profile_picture instanceof File) {
      // Utiliser FormData pour l'upload de fichier
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        if (key === 'profile_picture' && data.profile_picture instanceof File) {
          formData.append(key, data.profile_picture);
        } else if (data[key as keyof UpdateEmployeeRequest] !== undefined) {
          const value = data[key as keyof UpdateEmployeeRequest];
          if (value !== null && value !== undefined) {
            if (typeof value === 'object' && !(value instanceof File)) {
              formData.append(key, JSON.stringify(value));
            } else {
              formData.append(key, String(value));
            }
          }
        }
      });
      return this.api.patchFormData<Employee>(`employee/employees/${id}/`, formData);
    }
    return this.api.patch<Employee>(`employee/employees/${id}/`, data);
  }

  /**
   * Supprime un employé
   */
  deleteEmployee(id: number): Observable<void> {
    return this.api.delete<void>(`employee/employees/${id}/`);
  }

  /**
   * Récupère les employés actifs
   */
  getActiveEmployees(params?: any): Observable<PaginatedResponse<Employee>> {
    return this.api.get<PaginatedResponse<Employee>>('employee/employees/active/', params);
  }

  /**
   * Récupère les employés par département
   */
  getEmployeesByDepartment(departmentId: number, params?: any): Observable<PaginatedResponse<Employee>> {
    return this.api.get<PaginatedResponse<Employee>>(`employee/employees/by-department/${departmentId}/`, params);
  }

  /**
   * Récupère l'équipe du manager connecté
   */
  getMyTeam(params?: any): Observable<PaginatedResponse<Employee>> {
    return this.api.get<PaginatedResponse<Employee>>('employee/employees/my-team/', params);
  }

  /**
   * Récupère les subordonnés d'un employé
   */
  getSubordinates(employeeId: number): Observable<Employee[]> {
    return this.api.get<Employee[]>(`employee/employees/${employeeId}/subordinates/`);
  }

  /**
   * Récupère les statistiques globales des employés
   */
  getStatistics(): Observable<EmployeeStatistics> {
    return this.api.get<EmployeeStatistics>('employee/employees/statistics/');
  }

  /**
   * Récupère l'historique d'un employé
   */
  getEmployeeHistory(employeeId: number): Observable<any[]> {
    return this.api.get<any[]>(`employee/history/?employee=${employeeId}`);
  }

  /**
   * Supprime la photo de profil d'un employé
   */
  deleteEmployeeProfilePicture(id: number): Observable<Employee> {
    return this.api.patch<Employee>(`employee/employees/${id}/`, { profile_picture: null });
  }
}

