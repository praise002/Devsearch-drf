from django.urls import path
from .import views

urlpatterns = [
    path('inbox/', views.InboxGenericView.as_view()),
    path('<uuid:id>/', views.ViewMessage.as_view()),
    path('<str:username>/', views.CreateMessage.as_view()),
    path('<uuid:message_id>/', views.DeleteMessage.as_view()),
]
