export type JobPositionStatus = 'open' | 'closed' | 'on_hold';
export type CandidateStatus = 'applied' | 'screening' | 'interview' | 'offer' | 'hired' | 'rejected';
export type HiringProcessStage = 'application' | 'screening' | 'interview' | 'offer' | 'onboarding' | 'hired' | 'rejected';

export interface JobPosition {
  id: number;
  title: string;
  description: string;
  department?: number;
  department_name?: string;
  status: JobPositionStatus;
  status_display?: string;
  urgency: boolean;
  candidates_count?: number;
  active_candidates_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateJobPositionRequest {
  title: string;
  description: string;
  department?: number;
  status?: JobPositionStatus;
  urgency?: boolean;
}

export interface UpdateJobPositionRequest extends Partial<CreateJobPositionRequest> {}

export interface Candidate {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string;
  email: string;
  phone: string;
  resume?: string;
  cover_letter?: string;
  position: number;
  position_title?: string;
  status: CandidateStatus;
  status_display?: string;
  applied_date: string;
  interview_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateCandidateRequest {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  position: number;
  resume?: File;
  cover_letter?: string;
  notes?: string;
}

export interface UpdateCandidateRequest extends Partial<CreateCandidateRequest> {
  status?: CandidateStatus;
  interview_date?: string;
  notes?: string;
}

export interface HiringProcess {
  id: number;
  candidate: number;
  candidate_name?: string;
  position: number;
  position_title?: string;
  stage: HiringProcessStage;
  stage_display?: string;
  current_interviewer?: number;
  interview_date?: string;
  offer_date?: string;
  start_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateHiringProcessRequest {
  candidate: number;
  position: number;
  stage?: HiringProcessStage;
  interview_date?: string;
  notes?: string;
}

export interface UpdateHiringProcessRequest extends Partial<CreateHiringProcessRequest> {
  stage?: HiringProcessStage;
  offer_date?: string;
  start_date?: string;
}

export interface RecruitmentStatistics {
  total_positions: number;
  open_positions: number;
  closed_positions: number;
  urgent_positions: number;
  total_candidates: number;
  candidates_by_status: Record<CandidateStatus, number>;
  active_processes: number;
  average_time_to_hire: number;
}

