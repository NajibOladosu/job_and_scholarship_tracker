/**
 * Questions API Service
 */
import api from '@/lib/api.ts';

export interface Question {
  id: number;
  application: number;
  question_text: string;
  question_type: 'short_answer' | 'essay' | 'multiple_choice' | 'file_upload' | 'other';
  is_required: boolean;
  word_limit?: number;
  character_limit?: number;
  order: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface QuestionCreateData {
  application: number;
  question_text: string;
  question_type?: 'short_answer' | 'essay' | 'multiple_choice' | 'file_upload' | 'other';
  is_required?: boolean;
  word_limit?: number;
  character_limit?: number;
  order?: number;
  notes?: string;
}

export const questionsService = {
  /**
   * Get all questions for an application
   */
  async getByApplication(applicationId: number): Promise<Question[]> {
    const response = await api.get<Question[]>('/questions/', {
      params: { application: applicationId },
    });
    return response.data;
  },

  /**
   * Get question by ID
   */
  async getById(id: number): Promise<Question> {
    const response = await api.get<Question>(`/questions/${id}/`);
    return response.data;
  },

  /**
   * Create new question
   */
  async create(data: QuestionCreateData): Promise<Question> {
    const response = await api.post<Question>('/questions/', data);
    return response.data;
  },

  /**
   * Update question
   */
  async update(id: number, data: Partial<QuestionCreateData>): Promise<Question> {
    const response = await api.patch<Question>(`/questions/${id}/`, data);
    return response.data;
  },

  /**
   * Delete question
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/questions/${id}/`);
  },

  /**
   * Bulk create questions from text
   */
  async bulkCreate(
    applicationId: number,
    questions: string[]
  ): Promise<Question[]> {
    const createdQuestions: Question[] = [];
    for (let i = 0; i < questions.length; i++) {
      const question = await this.create({
        application: applicationId,
        question_text: questions[i],
        order: i + 1,
      });
      createdQuestions.push(question);
    }
    return createdQuestions;
  },
};
