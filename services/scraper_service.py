"""
Web scraping service for extracting content from application URLs.
"""
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)


class ScraperService:
    """
    Service class for scraping application URLs.
    """

    def __init__(self):
        """
        Initialize scraper with user agent rotation.
        """
        self.ua = UserAgent()
        self.session = requests.Session()

    def get_headers(self):
        """
        Get headers with random user agent.

        Returns:
            dict: Headers dictionary
        """
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def scrape_url(self, url, timeout=15):
        """
        Scrape content from a URL.

        Args:
            url (str): The URL to scrape
            timeout (int): Request timeout in seconds

        Returns:
            dict: Dictionary containing:
                - success (bool): Whether scraping succeeded
                - content (str): Extracted text content
                - title (str): Page title
                - error (str): Error message if failed
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return {
                    'success': False,
                    'content': '',
                    'title': '',
                    'error': 'Invalid URL format'
                }

            logger.info(f"Scraping URL: {url}")

            # Try static scraping first
            result = self._scrape_static(url, timeout)

            if result['success']:
                return result

            # If static scraping fails, we could try Playwright here
            # For now, return the static result
            return result

        except Exception as e:
            logger.error(f"Unexpected error scraping URL {url}: {e}")
            return {
                'success': False,
                'content': '',
                'title': '',
                'error': str(e)
            }

    def _scrape_static(self, url, timeout=15):
        """
        Scrape static content using requests and BeautifulSoup.

        Args:
            url (str): The URL to scrape
            timeout (int): Request timeout

        Returns:
            dict: Scraping result
        """
        try:
            # Make request
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = ''
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()

            # Also try to find job/scholarship title in common locations
            if not title:
                h1_tag = soup.find('h1')
                if h1_tag:
                    title = h1_tag.get_text().strip()

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = '\n'.join(chunk for chunk in chunks if chunk)

            logger.info(f"Successfully scraped static content from {url}")
            logger.info(f"Content length: {len(text_content)} characters")

            return {
                'success': True,
                'content': text_content,
                'title': title,
                'error': ''
            }

        except requests.exceptions.Timeout:
            logger.error(f"Timeout scraping URL: {url}")
            return {
                'success': False,
                'content': '',
                'title': '',
                'error': 'Request timed out'
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error scraping URL {url}: {e}")
            return {
                'success': False,
                'content': '',
                'title': '',
                'error': f'HTTP error: {e.response.status_code}'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error scraping URL {url}: {e}")
            return {
                'success': False,
                'content': '',
                'title': '',
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error parsing content from {url}: {e}")
            return {
                'success': False,
                'content': '',
                'title': '',
                'error': f'Parsing error: {str(e)}'
            }

    def extract_metadata(self, url):
        """
        Extract metadata from URL (title, company, deadline, etc.).

        Args:
            url (str): The URL to analyze

        Returns:
            dict: Dictionary containing extracted metadata
        """
        try:
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=10
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            metadata = {
                'title': '',
                'company': '',
                'location': '',
                'deadline': ''
            }

            # Try to extract title
            title_tag = soup.find('h1')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()

            # Try to extract company from meta tags or specific elements
            # This varies greatly by website, so we'll keep it simple
            company_meta = soup.find('meta', attrs={'property': 'og:site_name'})
            if company_meta:
                metadata['company'] = company_meta.get('content', '').strip()

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata from {url}: {e}")
            return {
                'title': '',
                'company': '',
                'location': '',
                'deadline': ''
            }


# Singleton instance
_scraper_service = None


def get_scraper_service():
    """
    Get or create singleton instance of ScraperService.

    Returns:
        ScraperService: The singleton service instance
    """
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ScraperService()
    return _scraper_service
