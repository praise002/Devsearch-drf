from django.urls import path
from .import views

urlpatterns = [
    path('inbox/', views.InboxGenericView.as_view()),
    path('<str:id>/', views.ViewMessage.as_view()),
    path('create/<str:profile_id>/', views.CreateMessage.as_view()),
    path('delete/<str:message_id>/', views.DeleteMessage.as_view()),
]
