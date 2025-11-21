import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { 
  JobPosition,
  CreateJobPositionRequest,
  UpdateJobPositionRequest,
  Candidate,
  CreateCandidateRequest,
  UpdateCandidateRequest,
  HiringProcess,
  CreateHiringProcessRequest,
  UpdateHiringProcessRequest,
  RecruitmentStatistics
} from '../../../core/models/recruitment.model';
import { PaginatedResponse } from '../../../core/interfaces/api.interface';

/**
 * Service pour la gestion du recrutement
 * Couche Application - Gère toutes les opérations CRUD et métier
 */
@Injectable({
  providedIn: 'root'
})
export class RecruitmentService {
  private api = inject(ApiService);

  // ============ Job Positions ============

  getJobPositions(params?: any): Observable<PaginatedResponse<JobPosition>> {
    return this.api.get<PaginatedResponse<JobPosition>>('recruitment/job-positions/', params);
  }

  getJobPosition(id: number): Observable<JobPosition> {
    return this.api.get<JobPosition>(`recruitment/job-positions/${id}/`);
  }

  createJobPosition(data: CreateJobPositionRequest): Observable<JobPosition> {
    return this.api.post<JobPosition>('recruitment/job-positions/', data);
  }

  updateJobPosition(id: number, data: UpdateJobPositionRequest): Observable<JobPosition> {
    return this.api.patch<JobPosition>(`recruitment/job-positions/${id}/`, data);
  }

  deleteJobPosition(id: number): Observable<void> {
    return this.api.delete<void>(`recruitment/job-positions/${id}/`);
  }

  getOpenJobPositions(params?: any): Observable<PaginatedResponse<JobPosition>> {
    return this.api.get<PaginatedResponse<JobPosition>>('recruitment/job-positions/', { ...params, status: 'open' });
  }

  // ============ Candidates ============

  getCandidates(params?: any): Observable<PaginatedResponse<Candidate>> {
    return this.api.get<PaginatedResponse<Candidate>>('recruitment/candidates/', params);
  }

  getCandidate(id: number): Observable<Candidate> {
    return this.api.get<Candidate>(`recruitment/candidates/${id}/`);
  }

  createCandidate(data: CreateCandidateRequest): Observable<Candidate> {
    if (data.resume instanceof File) {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        if (key === 'resume' && data.resume instanceof File) {
          formData.append(key, data.resume);
        } else if (data[key as keyof CreateCandidateRequest] !== undefined) {
          formData.append(key, String(data[key as keyof CreateCandidateRequest]));
        }
      });
      return this.api.postFormData<Candidate>('recruitment/candidates/', formData);
    }
    return this.api.post<Candidate>('recruitment/candidates/', data);
  }

  updateCandidate(id: number, data: UpdateCandidateRequest): Observable<Candidate> {
    if (data.resume instanceof File) {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        if (key === 'resume' && data.resume instanceof File) {
          formData.append(key, data.resume);
        } else if (data[key as keyof UpdateCandidateRequest] !== undefined) {
          const value = data[key as keyof UpdateCandidateRequest];
          if (value !== null && value !== undefined) {
            if (typeof value === 'object' && !(value instanceof File)) {
              formData.append(key, JSON.stringify(value));
            } else {
              formData.append(key, String(value));
            }
          }
        }
      });
      return this.api.patchFormData<Candidate>(`recruitment/candidates/${id}/`, formData);
    }
    return this.api.patch<Candidate>(`recruitment/candidates/${id}/`, data);
  }

  deleteCandidate(id: number): Observable<void> {
    return this.api.delete<void>(`recruitment/candidates/${id}/`);
  }

  getCandidatesByPosition(positionId: number, params?: any): Observable<PaginatedResponse<Candidate>> {
    return this.api.get<PaginatedResponse<Candidate>>('recruitment/candidates/', { ...params, position: positionId });
  }

  // ============ Hiring Process ============

  getHiringProcesses(params?: any): Observable<PaginatedResponse<HiringProcess>> {
    return this.api.get<PaginatedResponse<HiringProcess>>('recruitment/hiring-process/', params);
  }

  getHiringProcess(id: number): Observable<HiringProcess> {
    return this.api.get<HiringProcess>(`recruitment/hiring-process/${id}/`);
  }

  createHiringProcess(data: CreateHiringProcessRequest): Observable<HiringProcess> {
    return this.api.post<HiringProcess>('recruitment/hiring-process/', data);
  }

  updateHiringProcess(id: number, data: UpdateHiringProcessRequest): Observable<HiringProcess> {
    return this.api.patch<HiringProcess>(`recruitment/hiring-process/${id}/`, data);
  }

  deleteHiringProcess(id: number): Observable<void> {
    return this.api.delete<void>(`recruitment/hiring-process/${id}/`);
  }

  // ============ Statistics ============

  getStatistics(): Observable<RecruitmentStatistics> {
    return this.api.get<RecruitmentStatistics>('recruitment/statistics/');
  }
}

