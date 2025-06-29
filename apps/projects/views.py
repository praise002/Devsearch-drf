from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
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
from apps.profiles.schema_examples import build_avatar_request_schema
from apps.projects.filters import ProjectFilter
from apps.projects.schema_examples import (
    PROJECT_CREATE_RESPONSE_EXAMPLE,
    PROJECT_DETAIL_RESPONSE_EXAMPLE,
    PROJECT_LIST_EXAMPLE,
    RELATED_PROJECT_RESPONSE_EXAMPLE,
)

from .models import Project, Review, Tag
from .serializers import (
    FeaturedImageSerializer,
    ProjectCreateSerializer,
    ProjectSerializer,
    ReviewSerializer,
    TagSerializer,
)

tags = ["Projects"]


class ProjectListCreateView(APIView):
    paginator_class = CustomPagination()
    paginator_class.page_size = 10

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self, request=None):
        """
        Helper method to select serializer class based on request method.
        """
        if request and request.method == "POST":
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Helper to get an instance of the correct serializer.
        """
        serializer_class = self.get_serializer_class(
            kwargs.get("request") or self.request
        )
        return serializer_class(*args, **kwargs)

    @extend_schema(
        summary="Retrieve a list of user projects",
        description="This endpoint allows authenticated and unauthenticated users to view a list of all user projects in the system.",
        operation_id="list_projects",
        tags=tags,
        responses=PROJECT_LIST_EXAMPLE,
    )
    def get(self, request):
        projects = Project.objects.select_related("owner").prefetch_related("tags")
        paginated_projects = self.paginator_class.paginate_queryset(projects, request)
        serializer = self.get_serializer(paginated_projects, many=True)

        return self.paginator_class.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Create a new project",
        description="This endpoint allows authenticated users to create a new project. The user must be logged in to submit project details. Once the project is created, it is saved in the system and can be retrieved or updated later.",
        tags=tags,
        responses=PROJECT_CREATE_RESPONSE_EXAMPLE,
    )
    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        project = serializer.save()
        project_serializer = ProjectSerializer(project)  # re-serialize
        return CustomResponse.success(
            message="Project created successfully.",
            data=project_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class ProjectListCreateGenericView(ListCreateAPIView):
    queryset = Project.objects.select_related("owner__user").prefetch_related(
        "tags", "reviews"
    )

    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProjectFilter
    search_fields = ["title", "description", "tags__name"]
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCreateSerializer
        return ProjectSerializer

    @extend_schema(
        summary="Retrieve a list of user projects",
        description="This endpoint allows authenticated and unauthenticated users to view a list of all user projects in the system.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search across title, description, and tags.",
            ),
            OpenApiParameter(
                name="tags",
                description=("Filter projects by tags."),
            ),
        ],
        operation_id="list_projects",
        tags=tags,
        responses=PROJECT_LIST_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve projects with pagination, search, and filtering.
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
            message="Projects retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Create a new project",
        description="This endpoint allows authenticated users to create a new project. The user must be logged in to submit project details. Once the project is created, it is saved in the system and can be retrieved or updated later.",
        tags=tags,
        responses=PROJECT_CREATE_RESPONSE_EXAMPLE,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()

        project_serializer = ProjectSerializer(project)  # re-serialize
        return CustomResponse.success(
            message="Project created successfully.",
            data=project_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class ProjectRetrieveUpdateDestroyView(APIView):

    def get_object(self, profile, slug):
        try:
            project = Project.objects.get(owner=profile, slug=slug)
            return project
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self, request=None):
        """
        Helper method to select serializer class based on request method.
        """
        if request and request.method != "GET":
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Helper to get an instance of the correct serializer.
        """
        serializer_class = self.get_serializer_class(
            kwargs.get("request") or self.request
        )
        return serializer_class(*args, **kwargs)

    @extend_schema(
        summary="View a project details",
        description="This endpoint allows authenticated and unauthenticated users to view detailed information about a specific project.",
        tags=tags,
        responses=PROJECT_DETAIL_RESPONSE_EXAMPLE,
    )
    def get(self, request, slug):
        try:
            project = (
                Project.objects.select_related("owner__user")
                .prefetch_related("tags")
                .get(slug=slug)
            )
            serializer = self.get_serializer(project)
            return CustomResponse.success(
                message="Project detail retrieved successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

    @extend_schema(
        summary="Edit a specific project",
        description="This endpoint allows authenticated users to edit the details of an existing project. The user must be the project owner to edit the project.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def patch(self, request, slug):
        profile = request.user.profile

        project = self.get_object(profile, slug)
        serializer = self.get_serializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()

        project_serializer = ProjectSerializer(project)
        return CustomResponse.success(
            message="Project updated successfully.",
            data=project_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a specific project",
        description="This endpoint allows authenticated users to delete an existing project. Only the project owner can delete the project. The project will be permanently removed from the system.",
        tags=tags,
        responses={
            204: None,  # Successfully deleted project (no content in response body)
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def delete(self, request, slug):
        profile = request.user.profile

        project = self.get_object(profile, slug)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RelatedProjectsView(APIView):
    """
    API view to retrieve related projects for a specific project.
    """

    serializer_class = ProjectSerializer

    @extend_schema(
        summary="View related projects for a specific project",
        description="This endpoint allows users to view a list of projects that are related to a specific project. The related projects are determined based on project categories, tags, or other relevant factors. Users can retrieve a list of related projects, which may help them discover similar or complementary projects within the platform.",
        tags=tags,
        responses=RELATED_PROJECT_RESPONSE_EXAMPLE,
    )
    def get(self, request, slug):
        try:
            project = (
                Project.objects.select_related("owner__user")
                .prefetch_related("tags")
                .get(slug=slug)
            )

            # Get related projects based on shared tags
            related_projects = (
                Project.objects.select_related("owner__user")
                .filter(tags__in=project.tags.all())
                .exclude(id=project.id)
                .distinct()[:4]
            )

            serializer = ProjectSerializer(related_projects, many=True)

            return CustomResponse.success(
                message="Related projects retrieved successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")


class FeaturedImageUpdateView(APIView):
    serializer_class = FeaturedImageSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update project featured image",
        description="This endpoint allows authenticated users to upload or update their project featured image.",
        tags=tags,
        request=build_avatar_request_schema(
            prop1="featured_image", desc="Featured Image file"
        ),
        responses={},
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        project_serializer = ProjectSerializer(project)  # re-serialize

        return CustomResponse.success(
            message="Project updated successfully.",
            data=project_serializer.data,
            status_code=status.HTTP_200_OK,
        )


class TagListCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TagSerializer
    
    def get(self, request):
        # all tags - not specific to anyone
        pass

    @extend_schema(
        summary="Create a new tag",
        description="This endpoint allows authenticated users to create a new tag. Tags can be used to categorize or organize projects. Only authenticated users are allowed to create new tags. Tags are converted to lowercase when created.",
        tags=tags,
        responses={
            201: SuccessResponseSerializer,  # Successfully created tag
            400: ErrorResponseSerializer,  # Validation error or bad request
            401: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def post(self, request, slug):
        profile = request.user.profile
        try:
            project = Project.objects.get(owner=profile, slug=slug)
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

        # Get tag name from request and handle missing or empty value
        tag_name = request.data.get("name")
        if not tag_name:
            return CustomResponse.error(
                err_msg="Tag name is required.",
                err_code=ErrorCode.BAD_REQUEST,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        tag_name = tag_name.lower()

        tag, _ = Tag.objects.get_or_create(name=tag_name)

        # Link the tag to the project
        project.tags.add(tag)

        serializer = self.serializer_class(tag)
        return CustomResponse.success(
            message="Tag created successfully.",
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )


class TagRemoveView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, id):
        try:
            return Tag.objects.get(pk=id)
        except Tag.DoesNotExist:
            raise NotFoundError(err_msg="Tag not found.")

    @extend_schema(
        summary="Remove a tag from a project",
        description="This endpoint allows authenticated users to remove a specific tag from a project. The user must be authenticated and the tag will be removed based on the provided project slug and tag ID.",
        tags=tags,
        responses={
            204: SuccessResponseSerializer,  # Successfully removed tag
            404: ErrorResponseSerializer,  # Project or tag not found
            401: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def delete(self, request, project_slug, tag_id):
        """Remove a tag from a specific project."""
        profile = request.user.profile

        # Get the project based on the slug
        try:
            project = Project.objects.get(owner=profile, slug=project_slug)
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

        # Get the tag based on the tag ID
        tag = self.get_object(tag_id)

        # Check if the tag is associated with the project
        if tag not in project.tags.all():
            raise NotFoundError(
                err_msg="Tag not associated with this project.",
            )

        # Remove the association of this tag from the project
        project.tags.remove(tag)

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

class ReviewListCreateView(APIView):
    def get(self, request):
        pass
    
    def post(self, request):
        pass
    
class ReviewCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReviewSerializer

    @extend_schema(
        summary="Create a new review for a project",
        description="This endpoint allows authenticated users to submit a review for a specific project. Users cannot review their own project, and they can only submit one review per project. The review will be associated with the project and the user submitting it.",
        tags=tags,
        responses={
            201: SuccessResponseSerializer,  # Successfully created review
            400: ErrorDataResponseSerializer,  # User already reviewed this project
            403: ErrorResponseSerializer,  # User cannot review their own project
            404: ErrorResponseSerializer,  # Project not found
            401: ErrorResponseSerializer,
        },  # TODO: PUT IN SCHEMA LATER
    )
    def post(self, request, slug):
        # Retrieve the project
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

        # Check if the user is trying to review their own project
        if project.owner == request.user.profile:
            return CustomResponse.error(
                message="You cannot review your own project.",
                err_code=ErrorCode.FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Check if the user has already reviewed the project
        existing_review = project.reviews.filter(reviewer=request.user.profile).first()
        if existing_review:
            return CustomResponse.error(
                message="You have already reviewed this project.",
                status_code=status.HTTP_409_CONFLICT,
                err_code=ErrorCode.ALREADY_EXISTS,
            )

        # Create a review using the request data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the review and associate it with the project
        serializer.save(reviewer=request.user.profile, project=project)

        project.review_percentage

        return CustomResponse.success(
            message="Review added successfully.",
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ProjectReviewListView(APIView):
    """
    API view to retrieve a list of reviews for a specific project.
    """

    serializer_class = ReviewSerializer

    @extend_schema(
        summary="Retrieve all reviews for a project",
        description="This endpoint allows users to retrieve a list of all reviews for a specific project. It provides a collection of reviews with details such as the reviewer, rating, and feedback for the project.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,  # List of reviews for the project
            404: ErrorResponseSerializer,  # Project not found
        },  # TODO: PUT IN SCHEMA LATER
    )
    def get(self, slug):
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found")

        # Retrieve all reviews for the specified project
        reviews = Review.objects.filter(project=project)

        # Serialize the queryset
        serializer = self.serializer_class(reviews, many=True)
        # Return serialized data in response

        return CustomResponse.success(
            message="Project with reviews retrieved successfully.",
            data=serializer.data,
            status=status.HTTP_200_OK,
        )
