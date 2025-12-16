from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/papers/', permanent=True)),
    path('users/', include('users.urls')),
    path('papers/', include('papers.urls')),
]