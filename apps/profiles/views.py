from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.errors import ErrorCode
from apps.common.exceptions import NotFoundError
from apps.common.pagination import CustomPagination, DefaultPagination
from apps.common.responses import CustomResponse
from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from apps.profiles.filters import ProfileFilter
from apps.profiles.schema_examples import (
    PROFILE_RETRIEVE_RESPONSE_EXAMPLE,
    PROFILE_UPDATE_RESPONSE_EXAMPLE,
    build_avatar_request_schema,
)

from .models import Profile, Skill
from .serializers import (
    ImageSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    SkillSerializer,
)

tags = ["Profiles"]


class MyProfileView(APIView):  # view account and edit it
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    @extend_schema(
        summary="View a user profile",
        description="This endpoint allows authenticated users to view their profile details. Users can retrieve their account information. Only the account owner can access their profile.",
        tags=tags,
        responses=PROFILE_RETRIEVE_RESPONSE_EXAMPLE,
    )
    def get(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile)
        return CustomResponse.success(
            message="Profile retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update user profile",
        description="This endpoint allows authenticated users to edit their profile details. Users can update their personal information. Only the account owner can modify their profile.",
        tags=tags,
        responses=PROFILE_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        profile = serializer.save()
        profile_serializer = self.serializer_class(profile)  # re-serialize

        return CustomResponse.success(
            message="Profile updated successfully.",
            data=profile_serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ProfileListView(APIView):
    serializer_class = ProfileSerializer
    paginator_class = CustomPagination()
    paginator_class.page_size = 10

    @extend_schema(
        summary="Retrieve a list of user profiles",
        description="This endpoint allows authenticated and unauthenticated users to view a list of all user profiles in the system. It returns essential details about each profile.",
        operation_id="list_profiles",  # Unique operationId
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def get(self, request):
        profiles = (
            Profile.objects.select_related("user").prefetch_related("skills").all()
        )

        paginated_profiles = self.paginator_class.paginate_queryset(profiles, request)
        serializer = self.serializer_class(paginated_profiles, many=True)

        return self.paginator_class.get_paginated_response(serializer.data)


class ProfileListGenericView(ListAPIView):
    queryset = Profile.objects.select_related("user").prefetch_related("skills").all()
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
        responses={200: SuccessResponseSerializer},  # TODO: PUT IN SCHEMA LATER
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
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="Profiles retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ProfileDetailView(APIView):
    serializer_class = ProfileSerializer

    @extend_schema(
        summary="View a user's profile details",
        description="This endpoint allows any user, whether authenticated or not, to view detailed information about a specific user's profile. It provides publicly available details. This information is accessible to anyone.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            422: ErrorDataResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def get(self, username):
        try:
            profile = (
                Profile.objects.select_related("user")
                .prefetch_related("skills")
                .get(user__username=username)
            )
            serializer = self.serializer_class(profile)
            return CustomResponse.success(
                message="Profile detail retrieved successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )

        except Profile.DoesNotExist:
            return CustomResponse.error(
                message="Profile not found.",
                err_code=ErrorCode.BAD_REQUEST,
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class ImageUpdateView(APIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update user image",
        description="This endpoint allows authenticated users to upload or update their profile image.",
        tags=tags,
        request=build_avatar_request_schema(),
        responses=PROFILE_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        profile_serializer = ProfileSerializer(profile)  # re-serialize

        return CustomResponse.success(
            message="Profile updated successfully.",
            data=profile_serializer.data,
            status_code=status.HTTP_200_OK,
        )


class SkillCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SkillSerializer

    @extend_schema(
        summary="Add a new skill to your profile",
        description="This endpoint allows authenticated users to add a new skill to their profile. The user can specify skill details, which will be saved and associated with their profile. This endpoint requires authentication and is only accessible to logged-in users.",
        tags=tags,
        responses={
            201: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
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
        try:
            skill = Skill.objects.get(id=id, user=self.request.user.profile)
            return skill
        except Skill.DoesNotExist:
            raise NotFoundError(err_msg="Skill not found.")

    @extend_schema(
        summary="View a specific skill",
        description="This endpoint allows authenticated users to retrieve the details of a specific skill. Users must be logged in to access this functionality, as it is restricted to authenticated users only.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def get(self, id):
        skill = self.get_object(id)
        serializer = self.serializer_class(skill)
        return CustomResponse.success(
            message="Skills retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update a specific skill",
        description="This endpoint allows authenticated users to update a specific skill. Users must be logged in to access this functionality, as it is restricted to authenticated users only.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def patch(self, request, id):
        skill = self.get_object(id)
        serializer = self.serializer_class(skill, data=request.data, partial=True)
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
        responses={
            204: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def delete(self, id):
        skill = self.get_object(id)
        skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# REWORK ON ALL SCHEMAS FOR THE REAL RESULT
