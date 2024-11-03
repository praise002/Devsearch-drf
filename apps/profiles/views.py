from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.http import Http404

from apps.accounts.validators import validate_uuid

from .models import Profile, Skill
from .serializers import ProfileSerializer, SkillSerializer

class MyProfileView(APIView):  # view account and edit it
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProfileListView(APIView): #TODO: MIGHT CREATE A DIFF SERIALIZER LATER FOR ONLY WHAT IS NEEDED
    def get(self, request):
        profiles = Profile.objects.select_related('user') \
            .prefetch_related('skills').all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileDetailView(APIView):
    def get(self, request, username):
        try: #TODO: USE GET_OBJ_OR_404
            profile = Profile.objects.select_related('user') \
                .prefetch_related('skills').get(user__username=username)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            raise Http404("Profile not found.")
    
class SkillCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user.profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SkillDetailView(APIView): # detail, edit, delete
    permission_classes = (IsAuthenticated,)
    
    def get_object(self, id):
        if not validate_uuid(id):
            raise Http404('Invalid skill id')
        return get_object_or_404(Skill, id=id, user=self.request.user.profile)
    
    def get(self, request, id):
        skill = self.get_object(id)
        serializer = SkillSerializer(skill)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id): #TODO: PUT OR PATCH
        skill = self.get_object(id)
        serializer = SkillSerializer(skill, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        skill = self.get_object(id)
        skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# UserAccountView or MyProfileView