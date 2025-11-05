"""
Celery tasks for document processing.

This module contains background tasks for processing uploaded documents,
extracting information, and performing document analysis.
"""
import logging
from typing import Dict, List

from celery import shared_task
from django.utils import timezone

from core.tasks import BaseTask, exponential_backoff_retry, TaskStatusTracker
from documents.models import Document, ExtractedInformation

logger = logging.getLogger(__name__)


@shared_task(base=BaseTask, bind=True, max_retries=3)
@exponential_backoff_retry(max_retries=3, base_delay=60)
def process_document_task(self, document_id: int, file_content: str = None, file_extension: str = None) -> Dict[str, any]:
    """
    Process an uploaded document and extract information.

    This task handles the complete document processing pipeline:
    1. Validate document exists and is readable
    2. Parse document based on file type (PDF, DOCX, etc.)
    3. Extract structured information using AI
    4. Update document status

    Args:
        document_id: ID of the Document to process
        file_content: Optional base64-encoded file content (for Railway compatibility)
        file_extension: Optional file extension (e.g., '.pdf', '.docx')

    Returns:
        Dict containing processing results and status

    Raises:
        Document.DoesNotExist: If document with given ID doesn't exist
        Exception: For file reading or processing errors

    Example:
        # Process document asynchronously
        result = process_document_task.delay(document_id=123)

        # Process with countdown (delay)
        process_document_task.apply_async(
            args=[123],
            countdown=60  # Process after 60 seconds
        )
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, document_id=document_id)
    temp_file_path = None

    try:
        # Get document from database
        document = Document.objects.get(id=document_id)
        logger.info(f"Processing document: {document.original_filename}")

        # Validate file exists and is readable
        if not document.file and not file_content:
            raise ValueError(f"Document {document_id} has no file attached")

        # Parse document using document parser service
        from services.document_parser import get_document_parser
        parser = get_document_parser()

        # Handle file content for Railway (separate containers for web/worker)
        if file_content:
            import base64
            import tempfile
            logger.info(f"Using file content passed from upload (Railway mode)")

            # Decode base64 content
            file_bytes = base64.b64decode(file_content)

            # Write to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension or '.pdf') as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name
                logger.info(f"Written file content to temporary file: {temp_file_path}")

            parse_result = parser.parse_document(temp_file_path, document.document_type)
        else:
            # Use file path for local development
            logger.info(f"Parsing document: {document.file.path}")
            parse_result = parser.parse_document(document.file.path, document.document_type)

        if not parse_result['success']:
            raise ValueError(f"Failed to parse document: {parse_result['error']}")

        text_content = parse_result['text']
        logger.info(f"Extracted {len(text_content)} characters from document")

        # Extract structured information using AI
        # Call extract_information_task as a subtask
        extraction_result = extract_information_task.apply_async(
            args=[document_id, text_content],
            countdown=2  # Small delay to ensure document is saved
        )
        logger.info(f"Started information extraction task: {extraction_result.id}")

        # Update document status
        document.is_processed = True
        document.processed_at = timezone.now()
        document.save(update_fields=['is_processed', 'processed_at'])

        result = {
            'status': 'success',
            'document_id': document_id,
            'document_filename': document.original_filename,
            'processed_at': document.processed_at.isoformat(),
            'extraction_task_id': extraction_result.id
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Document.DoesNotExist:
        logger.error(f"Document with id {document_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}", exc_info=True)
        # Mark document as not processed on failure
        try:
            document = Document.objects.get(id=document_id)
            document.is_processed = False
            document.save(update_fields=['is_processed'])
        except:
            pass
        raise
    finally:
        # Clean up temporary file if created
        if temp_file_path:
            import os
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")


@shared_task(base=BaseTask, bind=True, max_retries=3)
@exponential_backoff_retry(max_retries=3, base_delay=60)
def extract_information_task(self, document_id: int, text_content: str = None) -> Dict[str, any]:
    """
    Extract structured information from a processed document using AI.

    This task uses AI (Gemini API) to extract structured information such as:
    - Name, email, contact information
    - Education history
    - Work experience
    - Skills and certifications
    - Other relevant information based on document type

    Args:
        document_id: ID of the Document to extract information from
        text_content: Optional pre-extracted text content (if None, will re-parse)

    Returns:
        Dict containing extracted information and metadata

    Example:
        # Extract information from document
        result = extract_information_task.delay(document_id=123)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, document_id=document_id)

    try:
        document = Document.objects.get(id=document_id)
        logger.info(f"Extracting information from: {document.original_filename}")

        # If text content not provided, parse the document
        if not text_content:
            from services.document_parser import get_document_parser
            parser = get_document_parser()
            parse_result = parser.parse_document(document.file.path, document.document_type)
            if not parse_result['success']:
                raise ValueError(f"Failed to parse document: {parse_result['error']}")
            text_content = parse_result['text']

        # Use Gemini API to extract structured information
        from services.gemini_service import get_gemini_service
        gemini = get_gemini_service()

        logger.info(f"Extracting structured information using Gemini AI")
        extracted_data = gemini.extract_document_information(text_content, document.document_type)

        # Save extracted information to database
        # Store each type of extracted information as separate records
        extraction_types = [
            ('name', extracted_data.get('name')),
            ('email', extracted_data.get('email')),
            ('phone', extracted_data.get('phone')),
            ('education', extracted_data.get('education')),
            ('experience', extracted_data.get('experience')),
            ('skills', extracted_data.get('skills')),
            ('certifications', extracted_data.get('certifications')),
            ('projects', extracted_data.get('projects')),
            ('languages', extracted_data.get('languages')),
            ('summary', extracted_data.get('summary')),
        ]

        created_count = 0
        for data_type, content in extraction_types:
            # Save if content exists and is not empty
            # For strings: check if not None and not empty
            # For lists: check if not None and has items
            if content is not None:
                if isinstance(content, str) and content.strip():
                    ExtractedInformation.objects.create(
                        document=document,
                        data_type=data_type,
                        content=content,
                        confidence_score=0.85  # Default confidence for AI extraction
                    )
                    created_count += 1
                    logger.info(f"Saved {data_type}: {str(content)[:100]}")
                elif isinstance(content, list) and len(content) > 0:
                    ExtractedInformation.objects.create(
                        document=document,
                        data_type=data_type,
                        content=content,
                        confidence_score=0.85  # Default confidence for AI extraction
                    )
                    created_count += 1
                    logger.info(f"Saved {data_type}: {len(content)} items")

        result = {
            'status': 'success',
            'document_id': document_id,
            'extracted_records': created_count,
            'extraction_types': [t for t, c in extraction_types if c]
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Document.DoesNotExist:
        logger.error(f"Document with id {document_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error extracting information from document {document_id}: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def bulk_process_documents_task(self, document_ids: List[int]) -> Dict[str, any]:
    """
    Process multiple documents in bulk.

    This task processes a batch of documents by spawning individual
    process_document_task for each document.

    Args:
        document_ids: List of Document IDs to process

    Returns:
        Dict containing batch processing results

    Example:
        # Process multiple documents
        result = bulk_process_documents_task.delay(document_ids=[1, 2, 3, 4, 5])
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, document_count=len(document_ids))

    results = []
    for i, doc_id in enumerate(document_ids, 1):
        try:
            task_result = process_document_task.delay(doc_id)
            results.append({
                'document_id': doc_id,
                'task_id': task_result.id,
                'status': 'queued'
            })
            tracker.log_progress(
                self.name,
                self.request.id,
                progress=i,
                total=len(document_ids)
            )
        except Exception as e:
            logger.error(f"Error queueing document {doc_id}: {e}")
            results.append({
                'document_id': doc_id,
                'status': 'error',
                'error': str(e)
            })

    result = {
        'status': 'success',
        'total_documents': len(document_ids),
        'queued': sum(1 for r in results if r['status'] == 'queued'),
        'failed': sum(1 for r in results if r['status'] == 'error'),
        'results': results
    }

    tracker.log_completion(self.name, self.request.id, **result)
    return result


@shared_task(base=BaseTask, bind=True)
def cleanup_old_documents_task(self, days: int = 365) -> Dict[str, any]:
    """
    Clean up old, unprocessed documents.

    This task can be scheduled to run periodically to remove old documents
    that were never processed or are no longer needed.

    Args:
        days: Number of days after which to consider documents old

    Returns:
        Dict containing cleanup statistics

    Example:
        # Clean up documents older than 1 year
        result = cleanup_old_documents_task.delay(days=365)
    """
    from django.utils import timezone
    from datetime import timedelta

    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, days=days)

    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        # TODO: Define cleanup criteria
        # For now, we don't actually delete documents - just log what would be deleted
        old_documents = Document.objects.filter(
            uploaded_at__lt=cutoff_date,
            is_processed=False
        )

        count = old_documents.count()
        logger.info(f"Found {count} old documents that could be cleaned up")

        # TODO: Uncomment to actually delete documents
        # deleted_count, _ = old_documents.delete()

        result = {
            'status': 'success',
            'cutoff_date': cutoff_date.isoformat(),
            'documents_found': count,
            'documents_deleted': 0  # Change when implementing actual deletion
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error during document cleanup: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True, max_retries=3)
def reprocess_document_task(self, document_id: int, force: bool = False) -> Dict[str, any]:
    """
    Reprocess a document that was previously processed.

    This is useful for updating extracted information when the AI model
    or extraction logic has been improved.

    Args:
        document_id: ID of the Document to reprocess
        force: If True, reprocess even if document is already processed

    Returns:
        Dict containing reprocessing results

    Example:
        # Force reprocess a document
        result = reprocess_document_task.delay(document_id=123, force=True)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, document_id=document_id, force=force)

    try:
        document = Document.objects.get(id=document_id)

        if document.is_processed and not force:
            logger.info(f"Document {document_id} already processed, skipping")
            return {
                'status': 'skipped',
                'document_id': document_id,
                'message': 'Document already processed, use force=True to reprocess'
            }

        # Clear existing extracted information
        if force:
            logger.info(f"Clearing existing extracted information for document {document_id}")
            document.extracted_info.all().delete()

        # Reset processing status
        document.is_processed = False
        document.processed_at = None
        document.save(update_fields=['is_processed', 'processed_at'])

        # Trigger processing
        task_result = process_document_task.delay(document_id)

        result = {
            'status': 'success',
            'document_id': document_id,
            'processing_task_id': task_result.id
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Document.DoesNotExist:
        logger.error(f"Document with id {document_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error reprocessing document {document_id}: {e}", exc_info=True)
        raise
