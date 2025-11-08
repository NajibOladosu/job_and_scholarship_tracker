/**
 * Responses API Service
 */
import api from '@/lib/api.ts';

export interface Response {
  id: number;
  question: number;
  response_text: string;
  is_ai_generated: boolean;
  word_count: number;
  character_count: number;
  status: 'draft' | 'final' | 'submitted';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ResponseCreateData {
  question: number;
  response_text: string;
  is_ai_generated?: boolean;
  status?: 'draft' | 'final' | 'submitted';
  notes?: string;
}

export const responsesService = {
  /**
   * Get all responses for a question
   */
  async getByQuestion(questionId: number): Promise<Response[]> {
    const response = await api.get<Response[]>('/responses/', {
      params: { question: questionId },
    });
    return response.data;
  },

  /**
   * Get all responses for an application
   */
  async getByApplication(applicationId: number): Promise<Response[]> {
    const response = await api.get<Response[]>('/responses/', {
      params: { application: applicationId },
    });
    return response.data;
  },

  /**
   * Get response by ID
   */
  async getById(id: number): Promise<Response> {
    const response = await api.get<Response>(`/responses/${id}/`);
    return response.data;
  },

  /**
   * Create new response
   */
  async create(data: ResponseCreateData): Promise<Response> {
    const response = await api.post<Response>('/responses/', data);
    return response.data;
  },

  /**
   * Update response
   */
  async update(id: number, data: Partial<ResponseCreateData>): Promise<Response> {
    const response = await api.patch<Response>(`/responses/${id}/`, data);
    return response.data;
  },

  /**
   * Delete response
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/responses/${id}/`);
  },

  /**
   * Generate AI response for a question
   */
  async generateAI(questionId: number): Promise<Response> {
    const response = await api.post<Response>(`/responses/generate/`, {
      question: questionId,
    });
    return response.data;
  },

  /**
   * Regenerate AI response
   */
  async regenerateAI(responseId: number): Promise<Response> {
    const response = await api.post<Response>(
      `/responses/${responseId}/regenerate/`
    );
    return response.data;
  },
};
