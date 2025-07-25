from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import NotFoundError
from apps.common.pagination import DefaultPagination
from apps.common.responses import CustomResponse

from apps.profiles.filters import ProfileFilter
from apps.profiles.schema_examples import (
    IMAGE_UPDATE_RESPONSE_EXAMPLE,
    PROFILE_DETAIL_RESPONSE_EXAMPLE,
    PROFILE_LIST_RESPONSE_EXAMPLE,
    PROFILE_UPDATE_RESPONSE_EXAMPLE,
    SKILL_CREATE_RESPONSE_EXAMPLE,
    SKILL_DELETE_RESPONSE_EXAMPLE,
    SKILL_LIST_RESPONSE_EXAMPLE,
    SKILL_UPDATE_RESPONSE_EXAMPLE,
    build_avatar_request_schema,
)

from .models import Profile, ProfileSkill, Skill
from .serializers import (
    AvatarSerializer,
    ProfileSerializer,
    ProfileSkillCreateSerializer,
    ProfileSkillSerializer,
    ProfileUpdateSerializer,
    SkillSerializer,
)

tags = ["Profiles"]


class ProfileRetrieveUpdateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self, request=None):
        """
        Helper method to select serializer class based on request method.
        """
        if request and request.method != "GET":
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Helper to get an instance of the correct serializer.
        """
        serializer_class = self.get_serializer_class(
            kwargs.get("request") or self.request
        )
        return serializer_class(*args, **kwargs)

    @extend_schema(
        summary="View a user's profile details",
        description="View any user's public profile or your own private profile details.",
        tags=tags,
        responses=PROFILE_DETAIL_RESPONSE_EXAMPLE,
    )
    def get(self, request, username):
        try:
            profile = (
                Profile.objects.select_related("user")
                .prefetch_related(
                    Prefetch(
                        "profileskill_set",
                        queryset=ProfileSkill.objects.select_related("skill").order_by(
                            "skill__name"
                        ),
                    )
                )
                .get(user__username=username)
            )

            serializer = self.get_serializer(profile)
            return CustomResponse.success(
                message="Profile detail retrieved successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )

        except Profile.DoesNotExist:
            raise NotFoundError(err_msg="Profile not found.")

    @extend_schema(
        summary="Update user profile",
        description="This endpoint allows authenticated users to edit their profile details. Users can update their personal information. Only the account owner can modify their profile.",
        tags=tags,
        responses=PROFILE_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request, username):
        if request.user.username != username:
            raise PermissionDenied("You can only update your own profile.")

        profile = request.user.profile
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return CustomResponse.success(
            message="Profile updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ProfileListGenericView(ListAPIView):
    queryset = Profile.objects.select_related("user").prefetch_related(
        Prefetch(
            "profileskill_set",
            queryset=ProfileSkill.objects.select_related("skill").order_by(
                "skill__name"
            ),
        )
    )
    serializer_class = ProfileSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProfileFilter
    search_fields = ["bio", "short_intro", "skills__name"]
    pagination_class = DefaultPagination

    @extend_schema(
        summary="Retrieve a list of user profiles",
        description="This endpoint allows authenticated and unauthenticated users to view a list of all user profiles in the system. It returns essential details about each profile.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search across bio, short intro, and skills.",
            ),
            OpenApiParameter(
                name="skills",
                description=("Filter profiles by skllls."),
            ),
            OpenApiParameter(
                name="location",
                description=("Filter profiles by location."),
            ),
        ],
        operation_id="list_profiles",
        tags=["Profiles"],
        responses=PROFILE_LIST_RESPONSE_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve profiles with pagination, search, and filtering.
        """
        return super().get(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data)
            return CustomResponse.success(
                message="Profiles retrieved successfully.",
                data=paginated_data.data,
                status_code=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="Profiles retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class AvatarUpdateView(APIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update user image",
        description="This endpoint allows authenticated users to upload or update their profile image.",
        tags=tags,
        request=build_avatar_request_schema(),
        responses=IMAGE_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        return CustomResponse.success(
            message="Profile image updated successfully.",
            data={
                "avatar_url": profile.avatar_url,
            },
            status_code=status.HTTP_200_OK,
        )


class SkillListCreateGenericView(ListCreateAPIView):
    queryset = Skill.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProfileSkillCreateSerializer
        return SkillSerializer

    @extend_schema(
        summary="Retrieve a list of skills",
        description="This endpoint allows authenticated users to view a list of all skills.",
        tags=tags,
        responses=SKILL_LIST_RESPONSE_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data)
            return CustomResponse.success(
                message="Skills retrieved successfully.",
                data=paginated_data.data,
                status_code=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="Skills retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Add a new skill to your profile",
        description="This endpoint allows authenticated users to add a new skill to their profile.",
        tags=tags,
        responses=SKILL_CREATE_RESPONSE_EXAMPLE,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile_skill = serializer.save()
        profile_serializer = ProfileSkillSerializer(profile_skill)

        return CustomResponse.success(
            message="Skill added successfully.",
            data=profile_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class SkillCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSkillSerializer

    @extend_schema(
        summary="Add a new skill to your profile",
        description="This endpoint allows authenticated users to add a new skill to their profile. The user can specify skill details, which will be saved and associated with their profile. This endpoint requires authentication and is only accessible to logged-in users.",
        tags=tags,
        responses=SKILL_CREATE_RESPONSE_EXAMPLE,
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user.profile)
        return CustomResponse.success(
            message="Skill created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class SkillUpdateDestroyView(APIView):  # detail, edit, delete
    permission_classes = (IsAuthenticated,)  # 1 - check auth
    serializer_class = ProfileSkillSerializer

    def get_object(self, id):
        try:
            profile_skill = ProfileSkill.objects.select_related("skill").get(
                skill__id=id, profile=self.request.user.profile
            )
            return profile_skill
        except ProfileSkill.DoesNotExist:
            # Only reaches here if skill doesn't exist AND user is authenticated
            raise NotFoundError(err_msg="Skill not found.")

    @extend_schema(
        summary="Update a specific skill",
        description="This endpoint allows authenticated users to update a specific skill. Users must be logged in to access this functionality, as it is restricted to authenticated users only.",
        tags=tags,
        responses=SKILL_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request, id):
        profile_skill = self.get_object(id)
        serializer = self.serializer_class(
            profile_skill, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return CustomResponse.success(
            message="Skill updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a specific skill",
        description="This endpoint allows authenticated users to delete a specific skill from their profile. Users must be logged in to access this functionality, as it is restricted to authenticated users only.",
        tags=tags,
        responses=SKILL_DELETE_RESPONSE_EXAMPLE,
    )
    def delete(self, request, id):
        profile_skill = self.get_object(id)
        profile_skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
