"""xr_fetcher URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from django.contrib import admin
from django.views.generic.base import RedirectView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .fetcher import views

admin.autodiscover()

urlpatterns = [
    path('', RedirectView.as_view(url='api/v0/', permanent=False)),
    path('admin/', admin.site.urls),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/v0/rates/', views.FetchRates.as_view()),
    path('api/v0/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v0/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
