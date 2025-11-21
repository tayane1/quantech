import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { 
  Department, 
  CreateDepartmentRequest, 
  UpdateDepartmentRequest,
  DepartmentStatistics,
  GlobalDepartmentStatistics
} from '../../../core/models/department.model';
import { PaginatedResponse } from '../../../core/interfaces/api.interface';

@Injectable({
  providedIn: 'root'
})
export class DepartmentService {
  private api = inject(ApiService);

  getDepartments(params?: any): Observable<PaginatedResponse<Department>> {
    return this.api.get<PaginatedResponse<Department>>('department/departments/', params);
  }

  getDepartment(id: number): Observable<Department> {
    return this.api.get<Department>(`department/departments/${id}/`);
  }

  createDepartment(data: CreateDepartmentRequest): Observable<Department> {
    return this.api.post<Department>('department/departments/', data);
  }

  updateDepartment(id: number, data: UpdateDepartmentRequest): Observable<Department> {
    return this.api.patch<Department>(`department/departments/${id}/`, data);
  }

  deleteDepartment(id: number): Observable<void> {
    return this.api.delete<void>(`department/departments/${id}/`);
  }

  getDepartmentEmployees(id: number): Observable<any[]> {
    return this.api.get<any[]>(`department/departments/${id}/employees/`);
  }

  getDepartmentJobPositions(id: number): Observable<any[]> {
    return this.api.get<any[]>(`department/departments/${id}/job-positions/`);
  }

  getDepartmentStatistics(id: number): Observable<DepartmentStatistics> {
    return this.api.get<DepartmentStatistics>(`department/departments/${id}/statistics/`);
  }

  getGlobalStatistics(): Observable<GlobalDepartmentStatistics> {
    return this.api.get<GlobalDepartmentStatistics>('department/departments/statistics/');
  }
}

