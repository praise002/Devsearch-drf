from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProfileListGenericView.as_view()),
    path("image/", views.AvatarUpdateView.as_view()),
    path("skills/", views.SkillListCreateGenericView.as_view()),
    path("skills/<uuid:id>/", views.SkillUpdateDestroyView.as_view()),
    path("<str:username>/", views.ProfileRetrieveUpdateView.as_view()),
]
