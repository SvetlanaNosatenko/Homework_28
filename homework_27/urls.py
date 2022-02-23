"""homework_27 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from ads import views
from homework_27 import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.AdDetailView.as_view()),
    path('ads/', views.DataAds.as_view()),
    path('ad/create/', views.AdsCreateView.as_view()),
    path('ad/<int:pk>/upload_image/', views.AdsImageView.as_view()),
    path('ad/', views.AdsView.as_view()),
    path('ad/<int:pk>/delete/', views.AdsDeleteView.as_view()),
    path('ad/<int:pk>/update/', views.AdsUpdateView.as_view()),
    path('cat/<int:pk>/delete/', views.CatDeleteView.as_view()),
    path('cat/<int:pk>/update/', views.CatUpdateView.as_view()),
    path('cat/create/', views.CatCreateView.as_view()),
    path('cat/', views.CatView.as_view()),
    path('cat/<int:pk>/', views.CatDetailView.as_view()),
    path('user/', include('users.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

