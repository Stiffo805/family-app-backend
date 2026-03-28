"""
URL configuration for family_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from markdownx.views import MarkdownifyView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

from family_app.views import IsAliveView

urlpatterns = [
    path('alive/', IsAliveView.as_view(), name='is-alive'),
    path('admin/', admin.site.urls),
    path('recipes/', include("recipes.urls")),
    path('shopping/', include("shopping.urls")),
    path('markdownx/markdownify/', MarkdownifyView.as_view(), name='markdownx_markdownify'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/login/', obtain_auth_token, name='api_token_auth'),
    # Endpoint for the Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]