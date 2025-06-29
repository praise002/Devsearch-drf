from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProjectListCreateGenericView.as_view(), name="project_list_create"),
    # path("", views.ProjectListCreateView.as_view(), name="project_list_create"),
    path("<slug:slug>/", views.ProjectRetrieveUpdateDestroyView.as_view()),
    path("<slug:slug>/related-projects/", views.RelatedProjectsView.as_view()),
    # Tags
    path("<slug:slug>/tags/", views.TagListCreateView.as_view()),
    path("<slug:project_slug>/tags/<str:tag_id>/", views.TagRemoveView.as_view()),
    # Reviews
    path("<slug:slug>/reviews/", views.ReviewListCreateView.as_view()),
]
