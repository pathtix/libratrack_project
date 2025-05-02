# libratrack/library/forms.py

from django import forms # Import Django forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User # Or your custom user model if you have one

# Import the Shelf model
from .models import Shelf, Book, Profile

class CustomUserCreationForm(UserCreationForm):
    # ... (code remains the same) ...
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields


# --- Shelf Form (Updated) ---
class ShelfForm(forms.ModelForm):
    """
    Form for creating and updating Shelf objects.
    """
    class Meta:
        model = Shelf
        # Add the new fields to the list
        fields = ['name', 'description', 'num_rows', 'num_columns']
        # Exclude 'owner' because it will be set automatically in the view

        # Define widgets to customize appearance
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'e.g., Fiction, Cookbooks, Sci-Fi Classics'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'rows': 3,
                'placeholder': 'Optional: Add a short description about the books on this shelf'
            }),
            # Add widgets for the new fields
            'num_rows': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'e.g., 3',
                'min': '1' # HTML5 validation for minimum value
            }),
            'num_columns': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'e.g., 5',
                'min': '1' # HTML5 validation for minimum value
            }),
        }
        # Optional: Customize labels if needed
        labels = {
            'num_rows': 'Number of Rows',
            'num_columns': 'Number of Columns/Sections',
        }


class BookForm(forms.ModelForm):
    """
    Form for creating and updating Book objects.
    """
    class Meta:
        model = Book
        # Add the new fields to the list
        fields = [
            'title', 'author', 'isbn', 'description', 'cover_image_url',
            'row_number', 'column_number' # New fields added
        ]
        # Exclude 'owner' and 'shelf' as they are set automatically in the view

        # Define widgets for styling and placeholders
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'Enter the book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'Enter the author(s)'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'Optional: Enter 13-digit ISBN'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Optional: Add a synopsis or notes about the book'
            }),
            'cover_image_url': forms.URLInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'Optional: Enter URL for cover image (e.g., https://...)'
            }),
            # Add widgets for the new fields
            'row_number': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'Optional: Row number (e.g., 1)',
                'min': '1' # HTML5 validation
            }),
            'column_number': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'Optional: Column/section number (e.g., 3)',
                'min': '1' # HTML5 validation
            }),
        }
        # Optional: Customize labels
        labels = {
            'isbn': 'ISBN',
            'cover_image_url': 'Cover Image URL',
            'row_number': 'Row Number',
            'column_number': 'Column/Section Number',
        }

# --- NEW: User Update Form ---
class UserUpdateForm(forms.ModelForm):
    """Form for updating basic User information like username."""
    # Email field removed from here

    class Meta:
        model = User # Based on the built-in User model
        # UPDATED: Removed 'email' from the fields list
        fields = ['username'] # Only allow username update
        widgets = {
             'username': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-stone-300 rounded-md shadow-sm placeholder-stone-400 focus:outline-none focus:ring-stone-500 focus:border-stone-500 sm:text-sm',
            }),
             # Email widget removed
        }


# --- NEW: Profile Update Form ---
class ProfileUpdateForm(forms.ModelForm):
    """Form for updating the user's Profile, specifically the image."""
    class Meta:
        model = Profile # Based on our Profile model
        fields = ['image'] # Only include the image field for upload
        widgets = {
            # Use FileInput for image uploads
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-stone-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-stone-100 file:text-stone-700 hover:file:bg-stone-200'
            })
        }
        labels = {
            'image': 'Profile Picture'
        }
