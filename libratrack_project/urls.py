"""
URL configuration for libratrack_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # Make sure include is imported
from django.conf import settings
from django.conf.urls.static import static
from library import views as library_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', library_views.register, name='register'),
    path('accounts/profile/', library_views.profile_view, name='profile'),
    path('accounts/profile/update/', library_views.profile_update_view, name='profile_update'),
    path('library/', include('library.urls')),
    path('search/', library_views.search_results, name='search_results'),
    path('api/live-search-books/', library_views.live_search_books, name='live_search_books'),
    path('', library_views.home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)