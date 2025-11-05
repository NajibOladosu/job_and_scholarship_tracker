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
        # Use Gemini 2.0 Flash - fast, stable, and available in all regions
        # Other options: models/gemini-2.5-flash, models/gemini-pro-latest
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')

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

        prompt = f"""You are the applicant answering this application question. Write as yourself in first person.

QUESTION: {question_text}

YOUR BACKGROUND:
{user_context}

CRITICAL INSTRUCTIONS:
- Write ONLY the final answer that would be submitted
- Do NOT write "Here's a framework" or "You need to fill in"
- Do NOT provide templates, placeholders, or instructions
- Do NOT use phrases like "[Your specific example here]"
- Write as if YOU are the candidate (use "I", "my", etc.)
- Use concrete details from YOUR BACKGROUND above
- Be professional and authentic
- Write a complete, ready-to-submit response

Length based on type:
- short_answer: 2-4 sentences
- essay: 2-4 well-developed paragraphs with specific examples
- experience/education: 1-2 focused paragraphs
- skills: Natural paragraph format
- custom: Match the question's needs

Write the complete answer now (nothing else):"""

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
        You are an expert at extracting information from {document_type} documents.
        Carefully analyze the document below and extract ALL available information.

        Document Text:
        {text_content[:10000]}

        Return a JSON object with these exact fields:
        {{
            "name": "full name or null",
            "email": "email address or null",
            "phone": "phone number or null",
            "education": [
                {{
                    "institution": "school/university name",
                    "degree": "degree type (BS, MS, PhD, etc.)",
                    "field": "major/field of study",
                    "graduation_year": "year",
                    "gpa": "GPA if mentioned",
                    "achievements": "honors, awards, relevant coursework"
                }}
            ],
            "experience": [
                {{
                    "company": "company/organization name",
                    "title": "job title/position",
                    "duration": "time period (e.g., Jan 2020 - Dec 2021)",
                    "responsibilities": ["responsibility 1", "responsibility 2", "..."],
                    "achievements": "key accomplishments or metrics"
                }}
            ],
            "skills": ["technical skill 1", "technical skill 2", "soft skill 1", "..."],
            "certifications": ["certification name 1", "certification name 2", "..."],
            "projects": [
                {{
                    "name": "project name",
                    "description": "brief description",
                    "technologies": "technologies used"
                }}
            ],
            "languages": ["language 1", "language 2", "..."],
            "summary": "brief professional summary or objective from the document"
        }}

        CRITICAL INSTRUCTIONS:
        - Extract EVERY piece of information you can find
        - If a field has no data, use null for strings or [] for arrays
        - For education: include ALL schools, degrees, and academic achievements
        - For experience: include ALL jobs, internships, volunteer work, and their responsibilities
        - For skills: include technical skills, programming languages, tools, frameworks, AND soft skills
        - For projects: include personal projects, academic projects, research
        - Be thorough and detailed - this information will be used to answer application questions
        - Return ONLY the JSON object, no markdown, no explanations
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

            # Log what was extracted
            extracted_fields = [k for k, v in extracted_info.items() if v and (not isinstance(v, list) or len(v) > 0)]
            logger.info(f"Successfully extracted from {document_type}: {', '.join(extracted_fields)}")

            # Log detailed counts
            if extracted_info.get('education'):
                logger.info(f"  - {len(extracted_info['education'])} education entries")
            if extracted_info.get('experience'):
                logger.info(f"  - {len(extracted_info['experience'])} experience entries")
            if extracted_info.get('skills'):
                logger.info(f"  - {len(extracted_info['skills'])} skills")

            return extracted_info

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response_text[:500]}")
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

        # Professional Summary
        if user_info.get('summary'):
            context_parts.append(f"Professional Summary:\n{user_info['summary']}\n")

        # Name and contact
        if user_info.get('name'):
            context_parts.append(f"Name: {user_info['name']}")
        if user_info.get('email'):
            context_parts.append(f"Email: {user_info['email']}")
        if user_info.get('phone'):
            context_parts.append(f"Phone: {user_info['phone']}")

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
                if edu.get('achievements'):
                    context_parts.append(f"    Achievements: {edu['achievements']}")

        # Work Experience
        experience = user_info.get('experience', [])
        if experience:
            context_parts.append("\nWork Experience:")
            for exp in experience:
                context_parts.append(f"  - {exp.get('title', '')} at {exp.get('company', '')}")
                if exp.get('duration'):
                    context_parts.append(f"    Duration: {exp['duration']}")
                if exp.get('responsibilities'):
                    context_parts.append(f"    Responsibilities:")
                    for resp in exp['responsibilities']:
                        context_parts.append(f"      • {resp}")
                if exp.get('achievements'):
                    context_parts.append(f"    Achievements: {exp['achievements']}")

        # Projects
        projects = user_info.get('projects', [])
        if projects:
            context_parts.append("\nProjects:")
            for proj in projects:
                proj_text = f"  - {proj.get('name', '')}"
                if proj.get('description'):
                    proj_text += f": {proj['description']}"
                context_parts.append(proj_text)
                if proj.get('technologies'):
                    context_parts.append(f"    Technologies: {proj['technologies']}")

        # Skills
        skills = user_info.get('skills', [])
        if skills:
            context_parts.append(f"\nSkills: {', '.join(skills)}")

        # Certifications
        certifications = user_info.get('certifications', [])
        if certifications:
            context_parts.append(f"\nCertifications: {', '.join(certifications)}")

        # Languages
        languages = user_info.get('languages', [])
        if languages:
            context_parts.append(f"\nLanguages: {', '.join(languages)}")

        return '\n'.join(context_parts) if context_parts else "No user information available. Please upload your resume or other documents to provide context for generating personalized responses."


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
