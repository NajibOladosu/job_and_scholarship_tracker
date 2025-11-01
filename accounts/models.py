"""
User and UserProfile models for the accounts app.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for the User model.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Uses email as the primary identifier instead of username.
    """
    username = None  # Remove username field
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Enter a valid email address.')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.email


class UserProfile(models.Model):
    """
    Extended user profile with additional information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
        help_text=_('User associated with this profile')
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        help_text=_('Contact phone number')
    )
    current_position = models.CharField(
        _('current position'),
        max_length=200,
        blank=True,
        help_text=_('Current job title or student status')
    )
    linkedin_url = models.URLField(
        _('LinkedIn URL'),
        max_length=500,
        blank=True,
        help_text=_('LinkedIn profile URL')
    )
    github_url = models.URLField(
        _('GitHub URL'),
        max_length=500,
        blank=True,
        help_text=_('GitHub profile URL')
    )
    portfolio_url = models.URLField(
        _('portfolio URL'),
        max_length=500,
        blank=True,
        help_text=_('Personal portfolio or website URL')
    )
    bio = models.TextField(
        _('biography'),
        blank=True,
        help_text=_('Brief professional biography')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        ordering = ['-created_at']

    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"
