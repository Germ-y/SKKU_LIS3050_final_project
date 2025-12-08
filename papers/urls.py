from django.urls import path
from .views import paper_list, paper_detail

urlpatterns = [
    path("", paper_list, name="paper_list"),
    path("<int:pk>/", paper_detail, name="paper_detail"),
]
