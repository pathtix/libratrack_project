# libratrack/library/urls.py

from django.urls import path
# Import all the shelf and book views we created
from .views import (
    ShelfListView,
    ShelfDetailView,
    ShelfCreateView,
    ShelfUpdateView,
    ShelfDeleteView,
    # Import Book views
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView,
)

# Define URL patterns for the library app
# app_name = 'library' # Optional: Add this for namespacing URLs if needed later

urlpatterns = [
    # --- Shelf URLs ---
    # /library/shelves/ -> List all shelves belonging to the user
    path('shelves/', ShelfListView.as_view(), name='shelf_list'),

    # /library/shelves/new/ -> Page to create a new shelf
    path('shelves/new/', ShelfCreateView.as_view(), name='shelf_create'),

    # /library/shelves/<int:pk>/ -> Detail view for a specific shelf (pk is the primary key)
    path('shelves/<int:pk>/', ShelfDetailView.as_view(), name='shelf_detail'),

    # /library/shelves/<int:pk>/update/ -> Page to update a specific shelf
    path('shelves/<int:pk>/update/', ShelfUpdateView.as_view(), name='shelf_update'),

    # /library/shelves/<int:pk>/delete/ -> Page to confirm deletion of a specific shelf
    path('shelves/<int:pk>/delete/', ShelfDeleteView.as_view(), name='shelf_delete'),


    # --- Book URLs ---

    # /library/shelves/<int:shelf_pk>/books/new/ -> Page to add a new book to a specific shelf
    # Note: We include the shelf's pk in the URL to associate the book correctly
    path('shelves/<int:shelf_pk>/books/new/', BookCreateView.as_view(), name='book_create'),

    # /library/books/<int:pk>/ -> Detail view for a specific book
    # We don't necessarily need the shelf pk here, just the book's pk
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),

    # /library/books/<int:pk>/update/ -> Page to update a specific book
    path('books/<int:pk>/update/', BookUpdateView.as_view(), name='book_update'),

    # /library/books/<int:pk>/delete/ -> Page to confirm deletion of a specific book
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    

]
