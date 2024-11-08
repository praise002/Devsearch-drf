from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.http import Http404

from drf_spectacular.utils import extend_schema

from apps.accounts.validators import validate_uuid
from apps.common.serializers import ErrorResponseSerializer, SuccessResponseSerializer

from .models import Profile, Skill
from .serializers import ProfileSerializer, SkillSerializer

tags = ["Profiles"]

class MyProfileView(APIView):  # view account and edit it
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    
    @extend_schema(
        summary="View a user profile",
        description="This endpoint allows authenticated users to view their profile details. Users can retrieve their account information, including name, email, and other personal data. Only the account owner can access their profile.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer, 
            #TODO: ADD OTHER ERRORS
        },
    )

    def get(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update user profile",
        description="This endpoint allows authenticated users to edit their profile details. Users can update their personal information. Only the account owner can modify their profile.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer, 
            #TODO: ADD OTHER ERRORS
        },
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileListView(
    APIView
):  # TODO: MIGHT CREATE A DIFF SERIALIZER LATER FOR ONLY WHAT IS NEEDED
    @extend_schema(
        summary="Retrieve a list of user profiles",
        description="This endpoint allows authenticated and unauthenticated users to view a list of all user profiles in the system. It returns essential details about each profile, such as name, email, and other public information.",
        operation_id="list_profiles",  # Unique operationId
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
    )
    
    def get(self, request):
        profiles = (
            Profile.objects.select_related("user").prefetch_related("skills").all()
        )
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileDetailView(APIView):
    serializer_class = ProfileSerializer
    
    @extend_schema(
        summary="View a user's profile details",
        description="This endpoint allows any user, whether authenticated or not, to view detailed information about a specific user's profile. It provides publicly available details such as the user's name, bio, and other visible information, depending on profile settings. This information is accessible to anyone.",
        # operation_id="retrieve_profile_by_username",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
    )
    
    def get(self, request, username):
        try:  # TODO: USE GET_OBJ_OR_404
            profile = (
                Profile.objects.select_related("user")
                .prefetch_related("skills")
                .get(user__username=username)
            )
            serializer = self.serializer_class(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            raise Http404("Profile not found.")


class SkillCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SkillSerializer
    
    @extend_schema(
        summary="Add a new skill to your profile",
        description="This endpoint allows authenticated users to add a new skill to their profile. The user can specify skill details, which will be saved and associated with their profile. This endpoint requires authentication and is only accessible to logged-in users.",
        tags=tags,
        responses={
            201: "",
            #TODO: ADD OTHER ERRORS
        },
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user.profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SkillDetailView(APIView):  # detail, edit, delete
    permission_classes = (IsAuthenticated,)
    serializer_class = SkillSerializer

    def get_object(self, id):
        if not validate_uuid(id):
            raise Http404("Invalid skill id")
        return get_object_or_404(Skill, id=id, user=self.request.user.profile)

    @extend_schema(
        summary="View a specific skill",
        description="This endpoint allows authenticated users to retrieve the details of a specific skill. Users must be logged in to access this functionality, as it is restricted to authenticated users only.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
    )
    
    def get(self, request, id):
        skill = self.get_object(id)
        serializer = self.serializer_class(skill)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a specific skill",
        description="This endpoint allows authenticated users to update a specific skill. Users must be logged in to access this functionality, as it is restricted to authenticated users only.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
    )
    
    def put(self, request, id):  # TODO: PUT OR PATCH
        skill = self.get_object(id)
        serializer = self.serializer_class(skill, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a specific skill",
        description="This endpoint allows authenticated users to delete a specific skill from their profile. Users must be logged in to access this functionality, as it is restricted to authenticated users only.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
    )
    
    def delete(self, request, id):
        skill = self.get_object(id)
        skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# UserAccountView or MyProfileView
