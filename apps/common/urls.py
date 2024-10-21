from django.urls import path
from . import views

urlpatterns = [
    # path('books/', views.BookListAPIView.as_view()),
    path('books/', views.BookListCreateAPIView.as_view()),
    # path('books/<int:pk>/', views.BookDetailAPIView.as_view()),
    path('books/<int:pk>/', views.BookDetailView.as_view()),
]
