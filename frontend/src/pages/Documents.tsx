import { motion } from 'framer-motion';
import { Upload, FileText, File, Trash2, Download, Eye } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

const mockDocuments = [
  {
    id: 1,
    name: 'Resume_2024.pdf',
    type: 'PDF',
    size: '245 KB',
    uploadedAt: '2025-11-01',
    status: 'processed',
  },
  {
    id: 2,
    name: 'Cover_Letter.docx',
    type: 'DOCX',
    size: '128 KB',
    uploadedAt: '2025-11-03',
    status: 'processed',
  },
  {
    id: 3,
    name: 'Transcript.pdf',
    type: 'PDF',
    size: '1.2 MB',
    uploadedAt: '2025-11-05',
    status: 'processing',
  },
  {
    id: 4,
    name: 'Portfolio.pdf',
    type: 'PDF',
    size: '3.5 MB',
    uploadedAt: '2025-11-06',
    status: 'processed',
  },
];

export const Documents = () => {
  const [isDragging, setIsDragging] = useState(false);

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

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    // Handle file upload logic here
    console.log('Files dropped:', e.dataTransfer.files);
  };

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
              {isDragging ? 'Drop files here' : 'Upload Documents'}
            </h3>
            <p className="text-text-secondary mb-4">
              Drag and drop files here or click to browse
            </p>
            <Button variant="primary">
              <label htmlFor="file-upload" className="cursor-pointer">
                Choose Files
              </label>
            </Button>
            <input
              id="file-upload"
              type="file"
              multiple
              className="hidden"
              onChange={(e) => console.log('Files selected:', e.target.files)}
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockDocuments.map((doc, index) => (
            <DocumentCard key={doc.id} document={doc} delay={index * 0.1} />
          ))}
        </div>
      </div>
    </div>
  );
};

const DocumentCard = ({
  document,
  delay,
}: {
  document: typeof mockDocuments[0];
  delay: number;
}) => {
  const getFileIcon = (type: string) => {
    switch (type) {
      case 'PDF':
        return <File className="text-red-400" size={32} />;
      case 'DOCX':
      case 'DOC':
        return <FileText className="text-blue-400" size={32} />;
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
              {getFileIcon(document.type)}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-text-primary font-medium truncate mb-1">
                {document.name}
              </h3>
              <p className="text-text-secondary text-sm">{document.size}</p>
            </div>
          </div>

          {/* Status Badge */}
          <div className="flex items-center justify-between">
            <span
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                document.status === 'processed'
                  ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                  : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30'
              }`}
            >
              {document.status === 'processed' ? 'Processed' : 'Processing...'}
            </span>
            <span className="text-text-secondary text-xs">
              {new Date(document.uploadedAt).toLocaleDateString()}
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2 pt-2 border-t border-border">
            <ActionButton icon={<Eye size={16} />} label="View" />
            <ActionButton icon={<Download size={16} />} label="Download" />
            <ActionButton
              icon={<Trash2 size={16} />}
              label="Delete"
              danger
            />
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
