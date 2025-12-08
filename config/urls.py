from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/papers/', permanent=True)),  # 루트 URL을 /papers/로 리디렉션
    path('users/', include('users.urls')),
    path('papers/', include('papers.urls')),
]