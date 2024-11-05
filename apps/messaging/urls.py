from django.urls import path
from .import views

urlpatterns = [
    path('inbox/', views.InboxView.as_view()),
    path('message/<str:id>/', views.ViewMessage.as_view()),
    path('message/create-message/<str:id>/', views.CreateMessage.as_view()),
    path('message/delete-message/<str:id>/', views.DeleteMessage.as_view()),
]
