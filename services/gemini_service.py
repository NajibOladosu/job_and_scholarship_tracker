"""
Google Gemini AI service for question extraction and response generation.
"""
import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service class for interacting with Google Gemini API.
    """

    def __init__(self):
        """
        Initialize Gemini API with API key from settings.
        """
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_questions_from_content(self, content, application_type='job'):
        """
        Extract application questions from scraped content using Gemini.

        Args:
            content (str): The scraped web page content
            application_type (str): 'job' or 'scholarship'

        Returns:
            list: List of dictionaries containing question data
        """
        prompt = f"""
        Analyze this {application_type} application page and extract all questions that applicants need to answer.

        Page Content:
        {content[:8000]}  # Limit content to avoid token limits

        Return a JSON array of questions with this exact structure:
        [
            {{
                "question_text": "the full question text",
                "question_type": "short_answer|essay|experience|education|skills|custom",
                "is_required": true|false
            }}
        ]

        Guidelines:
        - Only include actual questions, not general descriptions
        - Classify question types accurately:
          * short_answer: Brief responses (1-2 sentences)
          * essay: Long-form responses (paragraphs)
          * experience: Work experience questions
          * education: Education background questions
          * skills: Technical or soft skills questions
          * custom: Other types of questions
        - Mark questions as required if explicitly stated or if they seem mandatory
        - If no questions are found, return an empty array []

        Return ONLY the JSON array, no additional text.
        """

        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            questions = json.loads(response_text)
            logger.info(f"Extracted {len(questions)} questions from {application_type} application")
            return questions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error extracting questions with Gemini: {e}")
            return []

    def generate_response(self, question_text, question_type, user_info):
        """
        Generate a tailored response to an application question.

        Args:
            question_text (str): The question to answer
            question_type (str): Type of question
            user_info (dict): Dictionary containing user's extracted information

        Returns:
            dict: Contains 'response' (str) and 'prompt' (str)
        """
        # Build user context from extracted information
        user_context = self._build_user_context(user_info)

        prompt = f"""
        You are helping a user answer an application question professionally and authentically.

        QUESTION: {question_text}
        QUESTION TYPE: {question_type}

        USER'S INFORMATION:
        {user_context}

        Generate a professional, tailored response that:
        1. Directly answers the question
        2. Uses specific examples and details from the user's background
        3. Is appropriate in length for the question type:
           - short_answer: 1-3 sentences, concise and direct
           - essay: 2-4 paragraphs, detailed with examples
           - experience: 1-2 paragraphs highlighting relevant work
           - education: 1-2 paragraphs about educational background
           - skills: Bulleted list or paragraph of relevant skills
           - custom: Adapt to the question's needs
        4. Maintains a professional yet authentic tone
        5. Highlights achievements and qualifications relevant to the question
        6. Does NOT include generic advice or platitudes
        7. Does NOT mention that this is AI-generated

        Return ONLY the response text, no preamble or explanation.
        """

        try:
            response = self.model.generate_content(prompt)
            generated_text = response.text.strip()

            logger.info(f"Generated response for {question_type} question (length: {len(generated_text)} chars)")

            return {
                'response': generated_text,
                'prompt': prompt  # Store for debugging
            }

        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
            return {
                'response': '',
                'prompt': prompt
            }

    def extract_document_information(self, text_content, document_type):
        """
        Extract structured information from document text.

        Args:
            text_content (str): Extracted text from document
            document_type (str): Type of document (resume, transcript, certificate)

        Returns:
            dict: Dictionary with extracted information by category
        """
        prompt = f"""
        Extract structured information from this {document_type}.

        Document Text:
        {text_content[:10000]}  # Limit to avoid token limits

        Return a JSON object with these categories:
        {{
            "name": "full name",
            "email": "email address",
            "phone": "phone number",
            "education": [
                {{
                    "institution": "school name",
                    "degree": "degree type",
                    "field": "field of study",
                    "graduation_year": "year",
                    "gpa": "GPA if mentioned"
                }}
            ],
            "experience": [
                {{
                    "company": "company name",
                    "title": "job title",
                    "duration": "time period",
                    "responsibilities": ["list", "of", "key", "responsibilities"]
                }}
            ],
            "skills": ["skill1", "skill2", "skill3"],
            "certifications": ["cert1", "cert2"]
        }}

        Guidelines:
        - Extract all available information
        - Use null or empty arrays for missing information
        - Be precise and accurate
        - Return ONLY the JSON object, no additional text
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            extracted_info = json.loads(response_text)
            logger.info(f"Extracted information from {document_type}")
            return extracted_info

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error extracting document information with Gemini: {e}")
            return {}

    def _build_user_context(self, user_info):
        """
        Build formatted user context string from extracted information.

        Args:
            user_info (dict): Dictionary containing user's extracted information

        Returns:
            str: Formatted context string
        """
        context_parts = []

        # Name and contact
        if user_info.get('name'):
            context_parts.append(f"Name: {user_info['name']}")
        if user_info.get('email'):
            context_parts.append(f"Email: {user_info['email']}")

        # Education
        education = user_info.get('education', [])
        if education:
            context_parts.append("\nEducation:")
            for edu in education:
                edu_text = f"  - {edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}"
                if edu.get('graduation_year'):
                    edu_text += f" ({edu['graduation_year']})"
                if edu.get('gpa'):
                    edu_text += f", GPA: {edu['gpa']}"
                context_parts.append(edu_text)

        # Work Experience
        experience = user_info.get('experience', [])
        if experience:
            context_parts.append("\nWork Experience:")
            for exp in experience:
                context_parts.append(f"  - {exp.get('title', '')} at {exp.get('company', '')}")
                context_parts.append(f"    Duration: {exp.get('duration', '')}")
                if exp.get('responsibilities'):
                    context_parts.append(f"    Responsibilities: {', '.join(exp['responsibilities'][:3])}")

        # Skills
        skills = user_info.get('skills', [])
        if skills:
            context_parts.append(f"\nSkills: {', '.join(skills)}")

        # Certifications
        certifications = user_info.get('certifications', [])
        if certifications:
            context_parts.append(f"\nCertifications: {', '.join(certifications)}")

        return '\n'.join(context_parts) if context_parts else "No user information available."


# Singleton instance
_gemini_service = None


def get_gemini_service():
    """
    Get or create singleton instance of GeminiService.

    Returns:
        GeminiService: The singleton service instance
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
