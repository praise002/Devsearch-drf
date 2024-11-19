from django.urls import path
from .import views

urlpatterns = [
    path('', views.ProjectListGenericView.as_view(), name='project_list'),
    path('add/', views.ProjectCreateView.as_view()),
    path('<slug:slug>/', views.ProjectDetailView.as_view()),
    path('<slug:slug>/edit-delete/', views.ProjectEditDeleteView.as_view()),
    path('<slug:slug>/related/', views.RelatedProjectsView.as_view()),
    
    # Tags
    path('<slug:slug>/tag/add/', views.TagCreateView.as_view()),
    path('<slug:project_slug>/tag/<str:tag_id>/', views.TagRemoveView.as_view()),
    
    # Reviews
    path('<slug:slug>/review/add/', views.ReviewCreateView.as_view()),
    path('<slug:slug>/reviews/', views.ProjectReviewListView.as_view()),
]
