/**
 * Applications API Service
 */
import api from '@/lib/api.ts';

export interface Application {
  id: number;
  application_type: 'job' | 'scholarship';
  company_name: string;
  position_title: string;
  status: 'draft' | 'submitted' | 'in_review' | 'interview' | 'offer' | 'rejected' | 'withdrawn';
  priority: 'high' | 'medium' | 'low';
  deadline: string;
  tags?: any[];
  question_count?: number;
  response_count?: number;
  created_at: string;
  updated_at: string;
  application_url?: string;
  job_description?: string;
  requirements?: string;
  submission_date?: string;
  follow_up_date?: string;
  salary_range?: string;
  location?: string;
  is_remote?: boolean;
  company_website?: string;
  contact_person_name?: string;
  contact_person_email?: string;
  cover_letter?: string;
  resume_version?: string;
  additional_documents?: string;
  questions?: any[];
  notes?: any[];
  interviews?: any[];
}

export interface ApplicationCreateData {
  application_type: 'job' | 'scholarship';
  company_name: string;
  position_title: string;
  application_url?: string;
  job_description?: string;
  requirements?: string;
  status?: string;
  priority?: string;
  deadline?: string;
  submission_date?: string;
  salary_range?: string;
  location?: string;
  is_remote?: boolean;
  company_website?: string;
}

export interface ApplicationStats {
  total: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_type: Record<string, number>;
}

export const applicationsService = {
  /**
   * Get all applications
   */
  async getAll(params?: {
    search?: string;
    status?: string;
    priority?: string;
    application_type?: string;
  }): Promise<Application[]> {
    const response = await api.get<Application[]>('/applications/', { params });
    return response.data;
  },

  /**
   * Get application by ID
   */
  async getById(id: number): Promise<Application> {
    const response = await api.get<Application>(`/applications/${id}/`);
    return response.data;
  },

  /**
   * Create new application
   */
  async create(data: ApplicationCreateData): Promise<Application> {
    const response = await api.post<Application>('/applications/', data);
    return response.data;
  },

  /**
   * Update application
   */
  async update(id: number, data: Partial<ApplicationCreateData>): Promise<Application> {
    const response = await api.patch<Application>(`/applications/${id}/`, data);
    return response.data;
  },

  /**
   * Delete application
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/applications/${id}/`);
  },

  /**
   * Get application statistics
   */
  async getStats(): Promise<ApplicationStats> {
    const response = await api.get<ApplicationStats>('/applications/stats/');
    return response.data;
  },

  /**
   * Change application status
   */
  async changeStatus(
    id: number,
    status: string,
    notes?: string
  ): Promise<Application> {
    const response = await api.post<Application>(
      `/applications/${id}/change_status/`,
      { status, notes }
    );
    return response.data;
  },
};
