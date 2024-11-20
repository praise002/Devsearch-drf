from django_filters import rest_framework as filters

from apps.projects.models import Project

class ProjectFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__name', lookup_expr='icontains')  

    class Meta:
        model = Project
        fields = ['tags']