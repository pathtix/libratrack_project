from django.contrib import admin
from .models import Shelf, Book # Import the models from models.py in the same directory

# Register your models here.

# Basic registration (simplest way):
# admin.site.register(Shelf)
# admin.site.register(Book)

# --- OR ---

# More customizable registration using ModelAdmin classes (Recommended):

@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    """
    Customizes the display and behavior of the Shelf model in the Django admin.
    """
    # Fields to display in the list view of shelves
    list_display = ('name', 'owner', 'description')
    # Fields that can be used to filter the list view
    list_filter = ('owner',)
    # Fields that can be searched
    search_fields = ('name', 'description', 'owner__username') # Search by shelf name, description, or owner's username

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Customizes the display and behavior of the Book model in the Django admin.
    """
    # Fields to display in the list view of books
    list_display = ('title', 'author', 'shelf', 'owner', 'date_added', 'isbn')
    # Fields that can be used to filter the list view
    list_filter = ('shelf', 'owner', 'date_added')
    # Fields that can be searched
    search_fields = ('title', 'author', 'isbn', 'shelf__name', 'owner__username') # Search by book fields, shelf name, or owner username
    # Fields to automatically populate based on others (e.g., slug from title) - not needed here yet
    # prepopulated_fields = {}
    # Make date hierarchies navigable
    date_hierarchy = 'date_added'

