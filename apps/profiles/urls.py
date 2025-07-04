from django.urls import path
from .import views

urlpatterns = [
    path('', views.ProfileListGenericView.as_view()),
    path('account/', views.MyProfileView.as_view()),
    path('account/', views.ProfileUpdateView.as_view()),
    path('<str:username>/', views.ProfileDetailView.as_view()),
    path("profile/image/", views.ImageUpdateView.as_view()),
    path('skill/add/', views.SkillCreateView.as_view()),
    path('skill/<uuid:id>/', views.SkillDetailView.as_view()),
]
