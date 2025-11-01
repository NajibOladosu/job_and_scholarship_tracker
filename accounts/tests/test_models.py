"""
Tests for accounts models.
"""
import pytest
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test cases for User model."""

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.check_password('testpass123')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_without_email(self):
        """Test creating user without email raises error."""
        with pytest.raises(ValueError, match='The Email field must be set'):
            User.objects.create_user(email='', password='testpass123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        assert user.email == 'admin@example.com'
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True

    def test_create_superuser_without_is_staff(self):
        """Test creating superuser with is_staff=False raises error."""
        with pytest.raises(ValueError, match='Superuser must have is_staff=True'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )

    def test_create_superuser_without_is_superuser(self):
        """Test creating superuser with is_superuser=False raises error."""
        with pytest.raises(ValueError, match='Superuser must have is_superuser=True'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )

    def test_user_str_representation(self, test_user):
        """Test user string representation."""
        assert str(test_user) == test_user.email

    def test_user_get_full_name(self, test_user):
        """Test user get_full_name method."""
        full_name = test_user.get_full_name()
        assert full_name == f"{test_user.first_name} {test_user.last_name}"

    def test_user_get_full_name_without_names(self, db):
        """Test get_full_name returns email when names are empty."""
        user = User.objects.create_user(
            email='noname@example.com',
            password='testpass123'
        )
        assert user.get_full_name() == user.email

    def test_email_normalization(self, db):
        """Test email is normalized when creating user."""
        user = User.objects.create_user(
            email='Test@EXAMPLE.COM',
            password='testpass123'
        )
        assert user.email == 'Test@example.com'  # Domain lowercased

    def test_user_ordering(self, db):
        """Test users are ordered by date_joined descending."""
        user1 = User.objects.create_user(email='user1@example.com', password='pass')
        user2 = User.objects.create_user(email='user2@example.com', password='pass')
        users = list(User.objects.all())
        assert users[0] == user2  # Most recent first
        assert users[1] == user1


@pytest.mark.django_db
class TestUserProfileModel:
    """Test cases for UserProfile model."""

    def test_create_user_profile(self, test_user):
        """Test creating a user profile."""
        profile = UserProfile.objects.create(
            user=test_user,
            phone_number='+1234567890',
            current_position='Software Engineer',
            linkedin_url='https://linkedin.com/in/testuser',
            github_url='https://github.com/testuser',
            portfolio_url='https://testuser.com',
            bio='Test bio'
        )
        assert profile.user == test_user
        assert profile.phone_number == '+1234567890'
        assert profile.current_position == 'Software Engineer'
        assert profile.linkedin_url == 'https://linkedin.com/in/testuser'
        assert profile.github_url == 'https://github.com/testuser'
        assert profile.portfolio_url == 'https://testuser.com'
        assert profile.bio == 'Test bio'

    def test_user_profile_str_representation(self, test_user_with_profile):
        """Test user profile string representation."""
        profile = test_user_with_profile.profile
        expected = f"Profile for {test_user_with_profile.get_full_name()}"
        assert str(profile) == expected

    def test_user_profile_optional_fields(self, test_user):
        """Test user profile with optional fields blank."""
        profile = UserProfile.objects.create(user=test_user)
        assert profile.phone_number == ''
        assert profile.current_position == ''
        assert profile.linkedin_url == ''
        assert profile.github_url == ''
        assert profile.portfolio_url == ''
        assert profile.bio == ''

    def test_user_profile_one_to_one_relationship(self, test_user):
        """Test one-to-one relationship between User and UserProfile."""
        profile1 = UserProfile.objects.create(user=test_user)
        # Attempting to create another profile for same user should fail
        with pytest.raises(Exception):  # IntegrityError
            UserProfile.objects.create(user=test_user)

    def test_user_profile_cascade_delete(self, test_user):
        """Test profile is deleted when user is deleted."""
        profile = UserProfile.objects.create(user=test_user)
        profile_id = profile.user_id
        test_user.delete()
        assert not UserProfile.objects.filter(user_id=profile_id).exists()

    def test_user_profile_timestamps(self, test_user):
        """Test profile has created_at and updated_at timestamps."""
        profile = UserProfile.objects.create(user=test_user)
        assert profile.created_at is not None
        assert profile.updated_at is not None
        assert profile.created_at <= profile.updated_at

    def test_user_profile_ordering(self, db):
        """Test profiles are ordered by created_at descending."""
        user1 = User.objects.create_user(email='user1@example.com', password='pass')
        user2 = User.objects.create_user(email='user2@example.com', password='pass')
        profile1 = UserProfile.objects.create(user=user1)
        profile2 = UserProfile.objects.create(user=user2)
        profiles = list(UserProfile.objects.all())
        assert profiles[0] == profile2  # Most recent first
        assert profiles[1] == profile1
