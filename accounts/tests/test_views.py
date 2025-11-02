"""
Tests for accounts views.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
class TestSignUpView:
    """Test cases for SignUpView."""

    def test_signup_page_loads(self, client):
        """Test signup page loads successfully."""
        url = reverse('accounts:signup')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Sign Up' in str(response.content)

    def test_signup_with_valid_data(self, client):
        """Test signing up with valid data creates user."""
        url = reverse('accounts:signup')
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        response = client.post(url, data)
        assert response.status_code == 302  # Redirect after success
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_signup_creates_user_profile(self, client):
        """Test signup creates user profile automatically."""
        url = reverse('accounts:signup')
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        response = client.post(url, data)
        user = User.objects.get(email='newuser@example.com')
        assert UserProfile.objects.filter(user=user).exists()

    def test_signup_with_duplicate_email(self, client, test_user):
        """Test signup with existing email shows error."""
        url = reverse('accounts:signup')
        data = {
            'email': test_user.email,
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        response = client.post(url, data)
        assert response.status_code == 200  # Form re-rendered with errors
        assert 'already registered' in str(response.content).lower()

    def test_signup_redirects_to_login(self, client):
        """Test successful signup redirects to login page."""
        url = reverse('accounts:signup')
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse('accounts:login')


@pytest.mark.django_db
class TestLoginView:
    """Test cases for CustomLoginView."""

    def test_login_page_loads(self, client):
        """Test login page loads successfully."""
        url = reverse('accounts:login')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Login' in str(response.content)

    def test_login_with_valid_credentials(self, client, test_user):
        """Test login with valid credentials."""
        url = reverse('accounts:login')
        data = {
            'username': test_user.email,
            'password': 'testpass123'
        }
        response = client.post(url, data)
        assert response.status_code == 302  # Redirect after success

    def test_login_with_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials shows error."""
        url = reverse('accounts:login')
        data = {
            'username': test_user.email,
            'password': 'wrongpassword'
        }
        response = client.post(url, data)
        assert response.status_code == 200  # Form re-rendered
        assert not response.wsgi_request.user.is_authenticated

    def test_login_with_nonexistent_email(self, client):
        """Test login with non-existent email."""
        url = reverse('accounts:login')
        data = {
            'username': 'nonexistent@example.com',
            'password': 'password123'
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated

    def test_login_redirects_to_dashboard(self, client, test_user):
        """Test successful login redirects to dashboard."""
        url = reverse('accounts:login')
        data = {
            'username': test_user.email,
            'password': 'testpass123'
        }
        response = client.post(url, data, follow=False)
        assert response.status_code == 302
        # Should redirect to dashboard (exact URL depends on your URL config)

    def test_authenticated_user_redirected_from_login(self, authenticated_client):
        """Test authenticated user is redirected from login page."""
        url = reverse('accounts:login')
        response = authenticated_client.get(url)
        assert response.status_code == 302  # Redirected


@pytest.mark.django_db
class TestLogoutView:
    """Test cases for CustomLogoutView."""

    def test_logout_unauthenticated_user(self, client):
        """Test logout with unauthenticated user."""
        url = reverse('accounts:logout')
        response = client.post(url)
        assert response.status_code == 302

    def test_logout_authenticated_user(self, authenticated_client, test_user):
        """Test logout with authenticated user."""
        url = reverse('accounts:logout')
        response = authenticated_client.post(url)
        assert response.status_code == 302

    def test_logout_redirects_to_home(self, authenticated_client):
        """Test logout redirects to home page."""
        url = reverse('accounts:logout')
        response = authenticated_client.post(url, follow=False)
        assert response.status_code == 302


@pytest.mark.django_db
class TestProfileView:
    """Test cases for profile view."""

    def test_profile_requires_login(self, client):
        """Test profile view requires authentication."""
        url = reverse('accounts:profile')
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login
        assert '/login' in response.url

    def test_profile_page_loads_for_authenticated_user(self, authenticated_client, test_user):
        """Test profile page loads for authenticated user."""
        url = reverse('accounts:profile')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert 'profile' in str(response.content).lower()

    def test_profile_creates_profile_if_not_exists(self, authenticated_client, test_user):
        """Test profile view creates profile if it doesn't exist."""
        # Delete profile if exists
        UserProfile.objects.filter(user=test_user).delete()

        url = reverse('accounts:profile')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert UserProfile.objects.filter(user=test_user).exists()

    def test_profile_update_with_valid_data(self, authenticated_client, test_user):
        """Test updating profile with valid data."""
        UserProfile.objects.get_or_create(user=test_user)
        url = reverse('accounts:profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890',
            'current_position': 'Senior Engineer',
            'bio': 'Updated bio'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302  # Redirect after success

        # Verify updates
        test_user.refresh_from_db()
        assert test_user.first_name == 'Updated'
        assert test_user.last_name == 'Name'

        profile = UserProfile.objects.get(user=test_user)
        assert profile.phone_number == '+1234567890'
        assert profile.current_position == 'Senior Engineer'
        assert profile.bio == 'Updated bio'

    def test_profile_update_with_invalid_data(self, authenticated_client, test_user):
        """Test updating profile with invalid data."""
        UserProfile.objects.get_or_create(user=test_user)
        url = reverse('accounts:profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'linkedin_url': 'invalid-url'  # Invalid URL
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 200  # Form re-rendered with errors

    def test_profile_displays_user_data(self, authenticated_client, test_user_with_profile):
        """Test profile page displays user data."""
        url = reverse('accounts:profile')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert test_user_with_profile.email.encode() in response.content
        assert test_user_with_profile.first_name.encode() in response.content


@pytest.mark.django_db
class TestPasswordResetViews:
    """Test cases for password reset views."""

    def test_password_reset_page_loads(self, client):
        """Test password reset page loads."""
        url = reverse('accounts:password_reset')
        response = client.get(url)
        assert response.status_code == 200

    def test_password_reset_done_page_loads(self, client):
        """Test password reset done page loads."""
        url = reverse('accounts:password_reset_done')
        response = client.get(url)
        assert response.status_code == 200

    def test_password_reset_complete_page_loads(self, client):
        """Test password reset complete page loads."""
        url = reverse('accounts:password_reset_complete')
        response = client.get(url)
        assert response.status_code == 200
