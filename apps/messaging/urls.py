from django.urls import path

from . import views

urlpatterns = [
    path("inbox/", views.InboxGenericView.as_view()),
    path("<uuid:id>/", views.MessageRetrieveDestroyView.as_view()),
    path("<str:username>/", views.CreateMessage.as_view()),
]
