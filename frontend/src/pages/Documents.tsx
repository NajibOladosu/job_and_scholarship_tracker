import { motion } from 'framer-motion';
import { Upload, FileText, File, Trash2, Download, Eye, Loader2, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { documentsService } from '@/services/documents';
import type { Document } from '@/services/documents';

export const Documents = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const data = await documentsService.getAll();
      setDocuments(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    await uploadFiles(files);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      await uploadFiles(files);
    }
  };

  const uploadFiles = async (files: File[]) => {
    setUploading(true);

    for (const file of files) {
      try {
        // Determine document type based on file extension
        const extension = file.name.split('.').pop()?.toLowerCase();
        let documentType = 'other';
        if (extension === 'pdf' && file.name.toLowerCase().includes('resume')) {
          documentType = 'resume';
        } else if (extension === 'pdf' && file.name.toLowerCase().includes('transcript')) {
          documentType = 'transcript';
        } else if (['pdf', 'jpg', 'jpeg', 'png'].includes(extension || '')) {
          documentType = 'certificate';
        }

        await documentsService.upload(file, documentType, file.name);
      } catch (err: any) {
        console.error(`Failed to upload ${file.name}:`, err);
      }
    }

    setUploading(false);
    await fetchDocuments(); // Refresh the documents list
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await documentsService.delete(id);
        await fetchDocuments(); // Refresh the documents list
      } catch (err: any) {
        console.error('Failed to delete document:', err);
        alert('Failed to delete document');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 text-accent animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card variant="glass" className="p-8">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-500 text-center">{error}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-text-primary mb-2">Documents</h1>
        <p className="text-text-secondary">Upload and manage your application documents</p>
      </div>

      {/* Upload Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={`relative transition-all duration-300 ${
          isDragging ? 'scale-[1.02]' : ''
        }`}
      >
        <Card
          variant="glass"
          className={`p-12 text-center cursor-pointer transition-all duration-300 ${
            isDragging
              ? 'border-accent shadow-glow-lg bg-accent/5'
              : 'border-dashed border-2 hover:border-accent'
          }`}
        >
          <motion.div
            animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
            transition={{ duration: 0.2 }}
          >
            <Upload
              className={`mx-auto mb-4 transition-colors duration-300 ${
                isDragging ? 'text-accent' : 'text-text-secondary'
              }`}
              size={48}
            />
            <h3 className="text-xl font-bold text-text-primary mb-2">
              {uploading ? 'Uploading...' : isDragging ? 'Drop files here' : 'Upload Documents'}
            </h3>
            <p className="text-text-secondary mb-4">
              {uploading ? 'Please wait while we process your files' : 'Drag and drop files here or click to browse'}
            </p>
            <Button variant="primary" disabled={uploading}>
              <label htmlFor="file-upload" className="cursor-pointer">
                {uploading ? 'Uploading...' : 'Choose Files'}
              </label>
            </Button>
            <input
              id="file-upload"
              type="file"
              multiple
              className="hidden"
              onChange={handleFileSelect}
              disabled={uploading}
            />
            <p className="text-text-secondary text-sm mt-4">
              Supported formats: PDF, DOCX, DOC, JPG, PNG (Max 10MB)
            </p>
          </motion.div>
        </Card>
      </motion.div>

      {/* Documents List */}
      <div>
        <h2 className="text-xl font-bold text-text-primary mb-4">Your Documents</h2>
        {documents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {documents.map((doc, index) => (
              <DocumentCard key={doc.id} document={doc} delay={index * 0.1} onDelete={handleDelete} />
            ))}
          </div>
        ) : (
          <Card variant="glass" className="p-12 text-center">
            <FileText className="mx-auto mb-4 text-text-secondary" size={48} />
            <p className="text-text-secondary text-lg">No documents yet</p>
            <p className="text-text-secondary text-sm mt-2">Upload your first document to get started</p>
          </Card>
        )}
      </div>
    </div>
  );
};

const DocumentCard = ({
  document,
  delay,
  onDelete,
}: {
  document: Document;
  delay: number;
  onDelete: (id: number) => void;
}) => {
  const getFileExtension = (filename: string) => {
    return filename.split('.').pop()?.toUpperCase() || '';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (filename: string) => {
    const extension = getFileExtension(filename).toLowerCase();
    switch (extension) {
      case 'PDF':
        return <File className="text-red-400" size={32} />;
      case 'DOCX':
      case 'DOC':
        return <FileText className="text-blue-400" size={32} />;
      case 'JPG':
      case 'JPEG':
      case 'PNG':
        return <File className="text-purple-400" size={32} />;
      default:
        return <File className="text-text-secondary" size={32} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
    >
      <Card variant="hover">
        <div className="space-y-4">
          {/* File Icon and Info */}
          <div className="flex items-start space-x-4">
            <div className="p-3 rounded-lg glass">
              {getFileIcon(document.original_filename)}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-text-primary font-medium truncate mb-1">
                {document.original_filename}
              </h3>
              <p className="text-text-secondary text-sm">{formatFileSize(document.file_size)}</p>
            </div>
          </div>

          {/* Status Badge */}
          <div className="flex items-center justify-between">
            <span
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                document.is_processed
                  ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                  : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30'
              }`}
            >
              {document.is_processed ? 'Processed' : 'Processing...'}
            </span>
            <span className="text-text-secondary text-xs">
              {new Date(document.uploaded_at).toLocaleDateString()}
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2 pt-2 border-t border-border">
            {document.file_url && (
              <a href={document.file_url} target="_blank" rel="noopener noreferrer">
                <ActionButton icon={<Eye size={16} />} label="View" />
              </a>
            )}
            {document.file_url && (
              <a href={document.file_url} download>
                <ActionButton icon={<Download size={16} />} label="Download" />
              </a>
            )}
            <button onClick={() => onDelete(document.id)}>
              <ActionButton
                icon={<Trash2 size={16} />}
                label="Delete"
                danger
              />
            </button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};

const ActionButton = ({
  icon,
  label,
  danger = false,
}: {
  icon: React.ReactNode;
  label: string;
  danger?: boolean;
}) => (
  <motion.button
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
      danger
        ? 'text-red-400 hover:bg-red-500/10'
        : 'text-text-secondary hover:bg-surface hover:text-accent'
    }`}
  >
    {icon}
    <span>{label}</span>
  </motion.button>
);
