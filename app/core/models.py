from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.utils import timezone

from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles


class UserManager(BaseUserManager):
    """Manager for users."""
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag for filtering snippets."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SourceCode(models.Model):
    """Model to store detailed information for snippet source code."""

    todo_statuses = [
        ('C', 'Checked'),
        ('U', 'Unchecked')
    ]

    rating_choices = [
        (1, 'poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=255, default='Unknown')
    code = models.TextField(unique=True)
    notes = models.TextField(default="Notes not added!")
    url = models.URLField(max_length=255, default="http://example.com")
    status = models.CharField(max_length=1, choices=todo_statuses, default='U')
    rating = models.PositiveIntegerField(choices=rating_choices, default=3)
    is_favorite = models.BooleanField(default=False)
    count_updated = models.PositiveIntegerField(default=0)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    def settitle(self):
        try:
            row_no = SourceCode.objects.filter(user=self.user).count()
            return f"title {row_no+1}"
        except Exception:
            return 'title 1'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        if not self.code:
            raise ValueError('code content is required')
        if not self.title:
            self.title = self.settitle()

        self.count_updated = self.count_updated + 1
        super(SourceCode, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Snippet(models.Model):
    """Model to stores snippets with various styles in html format."""

    LEXERS = [item for item in get_all_lexers() if item[1]]
    LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
    STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    language_name = models.CharField(
        choices=LANGUAGE_CHOICES,
        default='python',
        max_length=100,
    )
    style = models.CharField(
        choices=STYLE_CHOICES,
        default='friendly',
        max_length=100,
    )
    linenos = models.BooleanField(default=False)
    highlighted = models.TextField()
    source_code = models.OneToOneField(
        SourceCode,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    tags = models.ManyToManyField(Tag)

    def save(self, *args, **kwargs):
        lang_choice = self.language_name
        style_choice = self.style
        if not any(lang_choice in _tuple for _tuple in self.LANGUAGE_CHOICES):
            raise ValueError('Language not set correctly')
        if not any(style_choice in _tuple for _tuple in self.STYLE_CHOICES):
            raise ValueError('Style not set correctly')

        super(Snippet, self).save(*args, **kwargs)

    def __str__(self):
        return f"snippet {self.id}"
