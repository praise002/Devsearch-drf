from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProfileListGenericView.as_view()),
    path("profile/image/", views.ImageUpdateView.as_view()),
    path("skill/", views.SkillCreateView.as_view()),
    path("skill/<uuid:id>/", views.SkillDetailUpdateDestroyView.as_view()),
    path("<str:username>/", views.ProfileRetrieveUpdateView.as_view()),
]
