export interface Department {
  id: number;
  name: string;
  code: string;
  description?: string;
  manager?: number;
  manager_name?: string;
  manager_email?: string;
  location?: string;
  budget?: number;
  employee_count?: number;
  total_employees?: number;
  active_employees?: number;
  job_positions_count?: number;
  open_positions_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateDepartmentRequest {
  name: string;
  code: string;
  description?: string;
  manager?: number;
  location?: string;
  budget?: number;
}

export interface UpdateDepartmentRequest extends Partial<CreateDepartmentRequest> {}

export interface DepartmentStatistics {
  department: {
    id: number;
    name: string;
    code: string;
    budget: number;
  };
  employees: {
    total: number;
    by_status: Record<string, number>;
    by_gender: Record<string, number>;
    average_salary: number;
    total_salary: number;
  };
  job_positions: {
    total: number;
    by_status: Record<string, number>;
    urgent: number;
    total_candidates: number;
  };
}

export interface GlobalDepartmentStatistics {
  total_departments: number;
  total_budget: number;
  total_employees: number;
  total_job_positions: number;
  by_department: Array<{
    id: number;
    name: string;
    code: string;
    employee_count: number;
    budget: number;
  }>;
}

