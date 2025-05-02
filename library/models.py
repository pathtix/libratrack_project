# libratrack/library/models.py
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings # To reference the User model
from django.dispatch import receiver
from django.db.models.signals import post_save
# Import validators for positive numbers
from django.core.validators import MinValueValidator

# Create your models here.

class Shelf(models.Model):
    """
    Represents a shelf in a user's library.
    Each shelf belongs to a specific user and can optionally have row/column dimensions.
    """
    # Name of the shelf (e.g., "Fiction", "Programming Books")
    name = models.CharField(max_length=200, help_text="Enter a name for the shelf")
    # Optional description for the shelf
    description = models.TextField(blank=True, null=True, help_text="Optional: Enter a description for the shelf")
    # Link to the user who owns this shelf.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shelves'
    )
    # --- NEW FIELDS ---
    # Optional number of rows for visualization
    num_rows = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)], # Ensure value is at least 1 if provided
        help_text="Optional: Number of rows on the shelf (for visualization)"
    )
    # Optional number of columns/compartments per row
    num_columns = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)], # Ensure value is at least 1 if provided
        help_text="Optional: Number of columns/sections on the shelf (for visualization)"
    )
    # --- END NEW FIELDS ---


    def __str__(self):
        """String for representing the Model object (e.g., in Admin site)."""
        dims = ""
        if self.num_rows and self.num_columns:
            dims = f" ({self.num_rows}x{self.num_columns})"
        elif self.num_rows:
            dims = f" ({self.num_rows} rows)"
        elif self.num_columns:
            dims = f" ({self.num_columns} cols)"

        return f"{self.name}{dims} (Owner: {self.owner.username})"

    class Meta:
        # Ensures a user cannot have two shelves with the same name
        unique_together = ('owner', 'name')
        # Correct plural name in Django admin
        verbose_name_plural = "Shelves"


class Book(models.Model):
    """
    Represents a book within a user's library, placed on a specific shelf,
    optionally at a specific row/column.
    """
    title = models.CharField(max_length=255, help_text="Enter the title of the book")
    author = models.CharField(max_length=255, help_text="Enter the author(s) of the book")
    isbn = models.CharField(
        'ISBN',
        max_length=13,
        unique=True,
        blank=True,
        null=True,
        help_text='Optional: 13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'
    )
    description = models.TextField(blank=True, null=True, help_text="Optional: Enter a description or synopsis")
    cover_image_url = models.URLField(max_length=2000, blank=True, null=True, help_text="Optional: URL for the book cover image")
    shelf = models.ForeignKey(
        Shelf,
        on_delete=models.CASCADE,
        related_name='books'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='books'
    )
    date_added = models.DateTimeField(auto_now_add=True)

    # --- NEW FIELDS for Book Position ---
    row_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Optional: The row number where the book is placed on the shelf (starting from 1)"
    )
    column_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Optional: The column/section number where the book is placed (starting from 1)"
    )
    # --- END NEW FIELDS ---

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['-date_added']
        unique_together = ('owner', 'title', 'author') # Consider if row/col should affect uniqueness

# --- NEW: Profile Model ---
class Profile(models.Model):
    """
    Stores additional user profile information, including profile picture.
    Linked one-to-one with the built-in User model.
    """
    # One-to-one link: Each User has exactly one Profile, and vice versa.
    # If the User is deleted, the Profile is also deleted.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # ImageField to store the profile picture.
    # 'upload_to' specifies the subdirectory within MEDIA_ROOT where images will be stored.
    # 'default' specifies a placeholder image if none is uploaded.
    # 'blank=True', 'null=True' make the field optional initially.
    image = models.ImageField(
        default='profile_pics/default.png', # Path relative to MEDIA_ROOT
        upload_to='profile_pics',
        blank=True,
        null=True
        )

    def __str__(self):
        return f"{self.user.username}'s Profile"

# --- Signal to auto-create/update Profile when User is created/saved ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile when a new User is created.
    Save the profile whenever the User object is saved.
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save() # Use lowercase 'profile' (the auto-created related name)