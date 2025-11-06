/**
 * Documents API Service
 */
import api from '../lib/api';

export interface Document {
  id: number;
  document_type: 'resume' | 'transcript' | 'certificate' | 'other';
  original_filename: string;
  file_size: number;
  is_processed: boolean;
  uploaded_at: string;
  processed_at?: string;
  file_url?: string;
  extracted_info?: any;
}

export const documentsService = {
  /**
   * Get all documents
   */
  async getAll(): Promise<Document[]> {
    const response = await api.get<Document[]>('/documents/');
    return response.data;
  },

  /**
   * Get document by ID
   */
  async getById(id: number): Promise<Document> {
    const response = await api.get<Document>(`/documents/${id}/`);
    return response.data;
  },

  /**
   * Upload new document
   */
  async upload(file: File, documentType: string, originalFilename: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    formData.append('original_filename', originalFilename);

    const response = await api.post<Document>('/documents/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Delete document
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/documents/${id}/`);
  },

  /**
   * Get extracted information for a document
   */
  async getExtractedInfo(id: number): Promise<any> {
    const response = await api.get(`/documents/${id}/extracted_info/`);
    return response.data;
  },
};
