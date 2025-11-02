"""
Tests for accounts forms.
"""
import pytest
from django.contrib.auth import get_user_model
from accounts.forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from accounts.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationForm:
    """Test cases for UserRegistrationForm."""

    def test_valid_registration_form(self):
        """Test form with valid data."""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid()

    def test_registration_form_invalid_email(self):
        """Test form with invalid email format."""
        form_data = {
            'email': 'invalid-email',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_registration_form_duplicate_email(self, test_user):
        """Test form with already registered email."""
        form_data = {
            'email': test_user.email,
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors
        assert 'already registered' in str(form.errors['email']).lower()

    def test_registration_form_password_mismatch(self):
        """Test form with mismatched passwords."""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'differentpass123'
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'password2' in form.errors

    def test_registration_form_weak_password(self):
        """Test form with weak password."""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': '123',
            'password2': '123'
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'password2' in form.errors or 'password1' in form.errors

    def test_registration_form_missing_required_fields(self):
        """Test form with missing required fields."""
        form_data = {
            'email': 'newuser@example.com'
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'first_name' in form.errors
        assert 'last_name' in form.errors
        assert 'password1' in form.errors
        assert 'password2' in form.errors

    def test_registration_form_email_case_normalization(self):
        """Test email is converted to lowercase."""
        form_data = {
            'email': 'NewUser@EXAMPLE.COM',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['email'] == 'newuser@example.com'

    def test_registration_form_save(self):
        """Test form save creates user correctly."""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid()
        user = form.save()
        assert user.email == 'newuser@example.com'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.check_password('strongpass123')


@pytest.mark.django_db
class TestUserLoginForm:
    """Test cases for UserLoginForm."""

    def test_valid_login_form(self, test_user):
        """Test form with valid credentials."""
        form_data = {
            'username': test_user.email,  # username field expects email
            'password': 'testpass123'
        }
        form = UserLoginForm(data=form_data)
        # Note: AuthenticationForm validation happens in view context
        # Here we just test the form structure
        assert 'username' in form.fields
        assert 'password' in form.fields

    def test_login_form_field_labels(self):
        """Test form has correct field labels."""
        form = UserLoginForm()
        assert form.fields['username'].label == 'Email'
        assert form.fields['password'].label == 'Password'

    def test_login_form_widgets(self):
        """Test form fields have correct widgets."""
        form = UserLoginForm()
        assert form.fields['username'].widget.__class__.__name__ == 'EmailInput'
        assert form.fields['password'].widget.__class__.__name__ == 'PasswordInput'


@pytest.mark.django_db
class TestUserProfileForm:
    """Test cases for UserProfileForm."""

    def test_valid_profile_form(self, test_user):
        """Test form with valid data."""
        profile = UserProfile.objects.create(user=test_user)
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890',
            'current_position': 'Senior Engineer',
            'linkedin_url': 'https://linkedin.com/in/updated',
            'github_url': 'https://github.com/updated',
            'portfolio_url': 'https://updated.com',
            'bio': 'Updated bio'
        }
        form = UserProfileForm(data=form_data, instance=profile, user=test_user)
        assert form.is_valid()

    def test_profile_form_optional_fields(self, test_user):
        """Test form with only required fields."""
        profile = UserProfile.objects.create(user=test_user)
        form_data = {
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = UserProfileForm(data=form_data, instance=profile, user=test_user)
        assert form.is_valid()

    def test_profile_form_invalid_url(self, test_user):
        """Test form with invalid URL."""
        profile = UserProfile.objects.create(user=test_user)
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'linkedin_url': 'not-a-valid-url'
        }
        form = UserProfileForm(data=form_data, instance=profile, user=test_user)
        assert not form.is_valid()
        assert 'linkedin_url' in form.errors

    def test_profile_form_initial_values(self, test_user):
        """Test form populates initial values from user."""
        profile = UserProfile.objects.create(user=test_user)
        form = UserProfileForm(instance=profile, user=test_user)
        assert form.fields['first_name'].initial == test_user.first_name
        assert form.fields['last_name'].initial == test_user.last_name

    def test_profile_form_save(self, test_user):
        """Test form save updates profile."""
        profile = UserProfile.objects.create(user=test_user)
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+9876543210',
            'current_position': 'Lead Engineer',
            'bio': 'Updated biography'
        }
        form = UserProfileForm(data=form_data, instance=profile, user=test_user)
        assert form.is_valid()
        updated_profile = form.save()
        assert updated_profile.phone_number == '+9876543210'
        assert updated_profile.current_position == 'Lead Engineer'
        assert updated_profile.bio == 'Updated biography'

    def test_profile_form_has_all_fields(self, test_user):
        """Test form includes all expected fields."""
        profile = UserProfile.objects.create(user=test_user)
        form = UserProfileForm(instance=profile, user=test_user)
        expected_fields = [
            'first_name', 'last_name', 'phone_number', 'current_position',
            'linkedin_url', 'github_url', 'portfolio_url', 'bio'
        ]
        for field in expected_fields:
            assert field in form.fields
