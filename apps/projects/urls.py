from django.urls import path

from . import views

urlpatterns = [
    # Static URLs first (no dynamic parameters)
    path("", views.ProjectListCreateGenericView.as_view(), name="project_list_create"),
    # path("", views.ProjectListCreateView.as_view(), name="project_list_create"),
    path("tags/", views.TagListGenericView.as_view()),
    path("image/", views.FeaturedImageUpdateView.as_view()),
    # Dynamic URLs with slug parameters (more specific first)
    path("<slug:slug>/related-projects/", views.RelatedProjectsView.as_view()),
    path("<slug:slug>/tags/", views.ProjectTagAddView.as_view()),
    path("<slug:project_slug>/tags/<uuid:tag_id>/", views.TagRemoveView.as_view()),
    path("<slug:slug>/reviews/", views.ReviewListCreateView.as_view()),
    # Most general dynamic URL last
    path("<slug:slug>/", views.ProjectRetrieveUpdateDestroyView.as_view(), name='project_detail'),
]
