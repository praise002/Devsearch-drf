from django_filters import rest_framework as filters

from apps.profiles.models import Profile

class ProfileFilter(filters.FilterSet):
    location = filters.CharFilter(lookup_expr='icontains')
    skills = filters.CharFilter(field_name='skills__name', lookup_expr='icontains')  

    class Meta:
        model = Profile
        fields = ['skills', 'location']