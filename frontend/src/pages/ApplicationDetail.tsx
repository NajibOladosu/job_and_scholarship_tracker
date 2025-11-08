import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Calendar,
  MapPin,
  DollarSign,
  ExternalLink,
  Edit,
  Trash2,
  Plus,
  Loader2,
  AlertCircle,
  FileText,
  MessageSquare,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { applicationsService, type Application } from '@/services/applications';
import { questionsService, type Question } from '@/services/questions';
import { responsesService, type Response } from '@/services/responses';

export const ApplicationDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [application, setApplication] = useState<Application | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [responses, setResponses] = useState<Record<number, Response>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingQuestion, setDeletingQuestion] = useState<number | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const [appData, questionsData] = await Promise.all([
          applicationsService.getById(parseInt(id)),
          questionsService.getByApplication(parseInt(id)),
        ]);

        setApplication(appData);
        setQuestions(questionsData);

        // Fetch responses for all questions
        const responsesData: Record<number, Response> = {};
        for (const question of questionsData) {
          const questionResponses = await responsesService.getByQuestion(question.id);
          if (questionResponses.length > 0) {
            responsesData[question.id] = questionResponses[0]; // Get the first/latest response
          }
        }
        setResponses(responsesData);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load application');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleDeleteApplication = async () => {
    if (!application || !window.confirm('Are you sure you want to delete this application?')) {
      return;
    }

    try {
      await applicationsService.delete(application.id);
      navigate('/applications');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete application');
    }
  };

  const handleDeleteQuestion = async (questionId: number) => {
    if (!window.confirm('Are you sure you want to delete this question?')) {
      return;
    }

    try {
      setDeletingQuestion(questionId);
      await questionsService.delete(questionId);
      setQuestions(questions.filter((q) => q.id !== questionId));
      const newResponses = { ...responses };
      delete newResponses[questionId];
      setResponses(newResponses);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete question');
    } finally {
      setDeletingQuestion(null);
    }
  };

  const handleGenerateResponse = async (questionId: number) => {
    try {
      const response = await responsesService.generateAI(questionId);
      setResponses({ ...responses, [questionId]: response });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate response');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 text-accent animate-spin" />
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card variant="glass" className="p-8">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-500 text-center">{error || 'Application not found'}</p>
          <Link to="/applications" className="block mt-4 text-center text-accent hover:text-accent-hover">
            Back to Applications
          </Link>
        </Card>
      </div>
    );
  }

  const statusConfig: Record<string, { color: string; bg: string; border: string }> = {
    draft: { color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
    submitted: { color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/30' },
    in_review: { color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30' },
    interview: { color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30' },
    offer: { color: 'text-accent', bg: 'bg-accent/10', border: 'border-accent/30' },
    rejected: { color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30' },
    withdrawn: { color: 'text-gray-400', bg: 'bg-gray-500/10', border: 'border-gray-500/30' },
  };

  const status = statusConfig[application.status] || statusConfig.draft;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/applications">
            <Button variant="ghost">
              <ArrowLeft size={20} />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-text-primary">{application.position_title}</h1>
            <p className="text-text-secondary">{application.company_name}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Link to={`/applications/${application.id}/edit`}>
            <Button variant="secondary">
              <Edit size={18} />
              <span className="ml-2">Edit</span>
            </Button>
          </Link>
          <Button variant="danger" onClick={handleDeleteApplication}>
            <Trash2 size={18} />
          </Button>
        </div>
      </div>

      {/* Application Details */}
      <Card variant="glass">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className={`px-4 py-2 rounded-lg border font-medium ${status.bg} ${status.color} ${status.border}`}>
              {application.status.replace('_', ' ').toUpperCase()}
            </span>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                application.priority === 'high'
                  ? 'bg-red-500/10 text-red-400'
                  : application.priority === 'medium'
                  ? 'bg-yellow-500/10 text-yellow-400'
                  : 'bg-gray-500/10 text-gray-400'
              }`}
            >
              {application.priority.toUpperCase()} PRIORITY
            </span>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {application.deadline && (
              <div className="flex items-center space-x-2 text-text-secondary">
                <Calendar size={18} />
                <span>Deadline: {new Date(application.deadline).toLocaleDateString()}</span>
              </div>
            )}
            {application.location && (
              <div className="flex items-center space-x-2 text-text-secondary">
                <MapPin size={18} />
                <span>{application.location}</span>
              </div>
            )}
            {application.salary_range && (
              <div className="flex items-center space-x-2 text-text-secondary">
                <DollarSign size={18} />
                <span>{application.salary_range}</span>
              </div>
            )}
            {application.application_url && (
              <div className="flex items-center space-x-2">
                <ExternalLink size={18} className="text-accent" />
                <a
                  href={application.application_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent hover:text-accent-hover"
                >
                  View Original Posting
                </a>
              </div>
            )}
          </div>

          {application.job_description && (
            <div>
              <h3 className="text-lg font-semibold text-text-primary mb-2">Description</h3>
              <p className="text-text-secondary whitespace-pre-wrap">{application.job_description}</p>
            </div>
          )}
        </div>
      </Card>

      {/* Questions and Responses */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-text-primary flex items-center space-x-2">
            <FileText size={24} />
            <span>Questions ({questions.length})</span>
          </h2>
          <Link to={`/applications/${application.id}/questions/new`}>
            <Button variant="primary">
              <Plus size={18} />
              <span className="ml-2">Add Question</span>
            </Button>
          </Link>
        </div>

        {questions.length === 0 ? (
          <Card variant="glass">
            <div className="text-center py-12">
              <MessageSquare className="w-16 h-16 text-text-secondary mx-auto mb-4" />
              <p className="text-text-secondary text-lg mb-4">No questions yet</p>
              <Link to={`/applications/${application.id}/questions/new`}>
                <Button variant="primary">Add Your First Question</Button>
              </Link>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {questions.map((question, index) => (
              <Card key={question.id} variant="glass">
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-text-primary mb-2">
                        Question {index + 1}
                        {question.is_required && <span className="text-red-400 ml-1">*</span>}
                      </h3>
                      <p className="text-text-secondary">{question.question_text}</p>
                      {(question.word_limit || question.character_limit) && (
                        <p className="text-sm text-text-secondary mt-2">
                          Limit:{' '}
                          {question.word_limit
                            ? `${question.word_limit} words`
                            : `${question.character_limit} characters`}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => handleDeleteQuestion(question.id)}
                      disabled={deletingQuestion === question.id}
                      className="text-red-400 hover:text-red-300 transition-colors disabled:opacity-50"
                    >
                      {deletingQuestion === question.id ? (
                        <Loader2 size={18} className="animate-spin" />
                      ) : (
                        <Trash2 size={18} />
                      )}
                    </button>
                  </div>

                  {/* Response */}
                  {responses[question.id] ? (
                    <div className="bg-surface/50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-accent">
                          {responses[question.id].is_ai_generated ? 'AI Generated' : 'Your'} Response
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-text-secondary">
                            {responses[question.id].word_count} words
                          </span>
                          <Link to={`/responses/${responses[question.id].id}/edit`}>
                            <Button variant="ghost" size="sm">
                              <Edit size={14} />
                            </Button>
                          </Link>
                        </div>
                      </div>
                      <p className="text-text-secondary whitespace-pre-wrap">
                        {responses[question.id].response_text}
                      </p>
                    </div>
                  ) : (
                    <div className="flex space-x-2">
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleGenerateResponse(question.id)}
                      >
                        Generate AI Response
                      </Button>
                      <Link to={`/questions/${question.id}/respond`}>
                        <Button variant="secondary" size="sm">
                          Write Manually
                        </Button>
                      </Link>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
