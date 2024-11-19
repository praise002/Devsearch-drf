from django_filters import rest_framework as filters

from apps.projects.models import Project

class ProjectFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    tags = filters.CharFilter(field_name='tags__name', lookup_expr='icontains')  

    class Meta:
        model = Project
        fields = ['title', 'description', 'tags']