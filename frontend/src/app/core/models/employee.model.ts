export type Gender = 'M' | 'F' | 'O';
export type EmployeeStatus = 'active' | 'on_leave' | 'inactive';

export interface Employee {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string;
  email: string;
  phone: string;
  date_of_birth: string;
  age?: number;
  gender: Gender;
  gender_display?: string;
  profile_picture?: string;
  employee_id: string;
  hire_date: string;
  years_of_service?: number;
  position?: number;
  position_name?: string;
  department?: number;
  department_name?: string;
  manager?: number;
  manager_name?: string;
  subordinates_count?: number;
  salary: number;
  status: EmployeeStatus;
  status_display?: string;
  address: string;
  city: string;
  country: string;
  created_at: string;
  updated_at: string;
}

export interface CreateEmployeeRequest {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  gender: Gender;
  employee_id?: string;
  hire_date: string;
  position?: number;
  department?: number;
  manager?: number;
  salary: number;
  status?: EmployeeStatus;
  address: string;
  city: string;
  country: string;
  profile_picture?: File;
}

export interface UpdateEmployeeRequest extends Omit<Partial<CreateEmployeeRequest>, 'profile_picture'> {
  profile_picture?: File | string;
}

export interface EmployeeStatistics {
  total: number;
  by_status: Record<EmployeeStatus, number>;
  by_gender: Record<Gender, number>;
  by_department: Array<{
    department_id: number;
    department_name: string;
    count: number;
  }>;
  average_salary: number;
  total_salary: number;
  average_age: number;
  average_years_of_service: number;
}

