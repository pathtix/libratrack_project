# libratrack/library/views.py


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count

from django.db.models import Q

# Import forms and models
from .forms import CustomUserCreationForm, ShelfForm, BookForm, UserUpdateForm, ProfileUpdateForm
from .models import Book, Shelf, Profile # Ensure Profile is imported

# --- Registration View (Existing) ---
def register(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect(reverse_lazy('home'))
        else:
             messages.error(request, 'Registration unsuccessful. Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- Homepage View (Existing) ---
def home(request):
    """
    Renders the homepage.
    Displays different content based on authentication status.
    Fetches recent books for authenticated users.
    """
    recent_books = [] # Initialize as empty list

    if request.user.is_authenticated:
        # If logged in, fetch the 5 most recently added books for THIS user
        try:
            recent_books = Book.objects.filter(owner=request.user).order_by('-date_added')[:5]
        except Exception as e:
            # Optional: Add some logging here in case of unexpected errors during query
            print(f"Error fetching recent books for user {request.user.username}: {e}")
            recent_books = [] # Ensure it's an empty list on error

    # Prepare the context dictionary to pass to the template
    context = {
        'recent_books': recent_books
    }
    # Render the homepage template with the context
    return render(request, 'home.html', context)


# --- NEW: Shelf Management Views (Class-Based Views) ---

class ShelfListView(LoginRequiredMixin, ListView):
    """Displays a list of shelves owned by the logged-in user."""
    model = Shelf
    template_name = 'library/shelf_list.html'
    context_object_name = 'shelves'

    def get_queryset(self):
        """Ensure users only see their own shelves and annotate with book count."""
        # Filter shelves by owner
        queryset = Shelf.objects.filter(owner=self.request.user)
        # Annotate each shelf with the count of its related books
        # Ensure we only count books owned by the current user as well for consistency
        queryset = queryset.annotate(
            book_count=Count('books', filter=Q(books__owner=self.request.user))
        ).order_by('name')
        return queryset

class ShelfDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Displays the details of a specific shelf and the books on it."""
    model = Shelf
    template_name = 'library/shelf_detail.html'
    context_object_name = 'shelf' # Name for the shelf object in the template

    def test_func(self):
        """Check if the logged-in user owns the shelf they are trying to view."""
        shelf = self.get_object()
        return self.request.user == shelf.owner

    # --- VERIFY THIS METHOD ---
    def get_context_data(self, **kwargs):
        """Add the list of books on this shelf to the template context."""
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Get the shelf object the view is displaying
        shelf = self.get_object()
        # Query the Book model for books that belong to this shelf AND this user
        books_query = Book.objects.filter(shelf=shelf, owner=self.request.user).order_by('title')
        # Add the queryset to the context with the key 'books_on_shelf'
        context['books_on_shelf'] = books_query
        # Optional: Log for debugging
        # print(f"Context for shelf {shelf.pk}: Found books - {list(books_query)}")
        return context

class ShelfCreateView(LoginRequiredMixin, CreateView):
    model = Shelf
    # Use the custom ShelfForm instead of 'fields'
    form_class = ShelfForm
    template_name = 'library/shelf_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Shelf '{form.instance.name}' created successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('shelf_detail', kwargs={'pk': self.object.pk})

class ShelfUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Shelf
    # Use the custom ShelfForm instead of 'fields'
    form_class = ShelfForm
    template_name = 'library/shelf_form.html'

    def test_func(self):
        shelf = self.get_object()
        return self.request.user == shelf.owner

    def form_valid(self, form):
        messages.success(self.request, f"Shelf '{form.instance.name}' updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('shelf_detail', kwargs={'pk': self.object.pk})

class ShelfDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Handles the deletion of a shelf."""
    model = Shelf
    template_name = 'library/shelf_confirm_delete.html' # Confirmation template
    context_object_name = 'shelf' # Name for the object in the template

    def test_func(self):
        """Check if the logged-in user owns the shelf they are trying to delete."""
        shelf = self.get_object()
        return self.request.user == shelf.owner

    def get_success_url(self):
        """Redirect to the shelf list view after successful deletion."""
        # We need to store the shelf name *before* deletion for the message
        shelf_name = self.object.name
        messages.success(self.request, f"Shelf '{shelf_name}' deleted successfully.")
        return reverse_lazy('shelf_list') # Redirect to the list of shelves

# Add other views (Book CRUD etc.) later

# --- NEW: Book Management Views ---

class BookDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Displays the details of a specific book."""
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def test_func(self):
        """Check if the logged-in user owns the book."""
        book = self.get_object()
        # Check ownership via the book itself or the shelf it belongs to
        return self.request.user == book.owner

class BookCreateView(LoginRequiredMixin, CreateView):
    """Handles adding a new book to a specific shelf."""
    model = Book
    form_class = BookForm # We will create this form next
    template_name = 'library/book_form.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to get the shelf object and ensure the user owns it.
        Store the shelf for later use in form_valid and get_context_data.
        """
        # Get the shelf's primary key from the URL kwargs
        shelf_pk = self.kwargs.get('shelf_pk')
        # Retrieve the shelf, ensuring it exists and belongs to the current user
        self.shelf = get_object_or_404(Shelf, pk=shelf_pk, owner=request.user)
        # If the shelf doesn't exist or doesn't belong to the user, get_object_or_404 will raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add the shelf object to the template context."""
        context = super().get_context_data(**kwargs)
        context['shelf'] = self.shelf # Make shelf available in the template
        return context

    def form_valid(self, form):
        """Set the owner and shelf before saving the book."""
        form.instance.owner = self.request.user
        form.instance.shelf = self.shelf # Assign the shelf obtained in dispatch
        messages.success(self.request, f"Book '{form.instance.title}' added to shelf '{self.shelf.name}' successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to the detail view of the shelf the book was added to."""
        return reverse('shelf_detail', kwargs={'pk': self.shelf.pk})


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Handles updating an existing book."""
    model = Book
    form_class = BookForm # Reuse the book form
    template_name = 'library/book_form.html'

    def test_func(self):
        """Check if the logged-in user owns the book."""
        book = self.get_object()
        return self.request.user == book.owner

    def get_context_data(self, **kwargs):
        """Add the book object to the context (useful for the template title)."""
        context = super().get_context_data(**kwargs)
        context['book'] = self.get_object() # Make book available in template
        return context

    def form_valid(self, form):
        """Add a success message upon successful update."""
        messages.success(self.request, f"Book '{form.instance.title}' updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to the detail view of the book."""
        return reverse('book_detail', kwargs={'pk': self.object.pk})


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Handles the deletion of a book."""
    model = Book
    template_name = 'library/book_confirm_delete.html' # Confirmation template
    context_object_name = 'book'

    def test_func(self):
        """Check if the logged-in user owns the book."""
        book = self.get_object()
        return self.request.user == book.owner

    def get_success_url(self):
        """Redirect back to the detail view of the shelf the book was on."""
        book = self.get_object() # Get book object before deleting
        shelf_pk = book.shelf.pk # Get the shelf's pk
        book_title = book.title # Get the title for the message
        messages.success(self.request, f"Book '{book_title}' deleted successfully.")
        # Redirect to the shelf detail page
        return reverse('shelf_detail', kwargs={'pk': shelf_pk})


# --- NEW: Search Results View ---
@login_required # Ensure only logged-in users can search
def search_results(request):
    """Displays search results for books based on a query."""
    query = request.GET.get('q', '') # Get the search query from GET parameter 'q', default to empty string
    results = [] # Initialize empty list for results

    if query:
        # If a query exists, filter books owned by the current user
        # Search in title, author, and optionally ISBN or description
        # Use Q objects for OR conditions and icontains for case-insensitive search
        results = Book.objects.filter(
            Q(owner=request.user) & # Must belong to the user AND match one of the following:
            (
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query) # Optionally search ISBN
                # Q(description__icontains=query) # Optionally search description
            )
        ).distinct().order_by('title') # Use distinct() in case a book matches multiple fields

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'library/search_results.html', context)

# --- NEW: Live Search API View ---
@login_required
def live_search_books(request):
    """Handles asynchronous requests for book search preview."""
    query = request.GET.get('q', '').strip() # Get query, remove leading/trailing whitespace
    books_data = [] # Initialize empty list for book data

    # Only perform search if query is not empty (adjust min length if needed)
    if query and len(query) >= 1:
        # Limit the number of results for the preview (e.g., top 5-7)
        limit = 7
        results = Book.objects.filter(
            Q(owner=request.user) &
            (
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )
        ).distinct().order_by('title')[:limit] # Apply limit

        # Format the results into a list of dictionaries suitable for JSON
        for book in results:
            books_data.append({
                'id': book.pk,
                'title': book.title,
                'author': book.author,
                'cover_url': book.cover_image_url if book.cover_image_url else None, # Include cover URL
                # Add other fields if needed by the frontend preview
            })

    # Return the data as a JSON response
    return JsonResponse({'books': books_data})

@login_required # Ensure user is logged in
def profile_view(request):
    """Displays the user's profile page."""
    # We can add more context here later (e.g., user's email, shelf count)
    context = {
        'user': request.user
    }
    return render(request, 'registration/profile.html', context)

# --- NEW: Profile Update View ---
# --- UPDATED: Profile Update View ---
@login_required
def profile_update_view(request):
    """Handles updating the user's profile information and picture."""
    # Get or create the profile instance for the current user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Populate forms with submitted data and files
        # instance=request.user tells the form which User object to update
        # instance=profile uses the profile object we just fetched or created
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # Pass request.FILES to handle the image upload
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile) # Use profile instance

        # Check if both forms are valid
        if u_form.is_valid() and p_form.is_valid():
            u_form.save() # Save the User object changes
            p_form.save() # Save the Profile object changes (including image)
            messages.success(request, 'Your profile has been updated successfully!')
            # Redirect back to the profile page
            return redirect('profile')
        else:
            # If forms are invalid, show error message
            messages.error(request, 'Please correct the errors below.')

    else: # GET request
        # Populate forms with the current user's data
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile) # Use profile instance

    # Prepare context for the template
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    # Render the profile update template
    return render(request, 'registration/profile_update_form.html', context)