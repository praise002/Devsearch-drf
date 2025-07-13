from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.errors import ErrorCode
from apps.common.exceptions import NotFoundError
from apps.common.pagination import CustomPagination, DefaultPagination
from apps.common.responses import CustomResponse
from apps.profiles.schema_examples import build_avatar_request_schema
from apps.projects.filters import ProjectFilter
from apps.projects.mixins import HeaderMixin
from apps.projects.permissions import IsProjectOwner
from apps.projects.schema_examples import (
    FEATURED_IMAGE_UPDATE_RESPONSE_EXAMPLE,
    PROJECT_CREATE_RESPONSE_EXAMPLE,
    PROJECT_DELETE_RESPONSE,
    PROJECT_DETAIL_RESPONSE_EXAMPLE,
    PROJECT_LIST_EXAMPLE,
    PROJECT_UPDATE_EXAMPLE,
    RELATED_PROJECT_RESPONSE_EXAMPLE,
    REVIEW_CREATE_RESPONSE_EXAMPLE,
    REVIEW_GET_RESPONSE_EXAMPLE,
    TAG_CREATE_RESPONSE_EXAMPLE,
    TAG_LIST_RESPONSE_EXAMPLE,
    TAG_REMOVE_RESPONSE_EXAMPLE,
)

from .models import Project, Review, Tag
from .serializers import (
    FeaturedImageSerializer,
    ProjectCreateSerializer,
    ProjectSerializer,
    ReviewSerializer,
    TagCreateSerializer,
    TagSerializer,
)

tags = ["Projects"]


class ProjectListCreateView(HeaderMixin, APIView):
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

        serializer.save()
        # project_serializer = ProjectSerializer(project)  # re-serialize
        headers = self.get_success_headers(serializer.data)

        return CustomResponse.success(
            message="Project created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
            headers=headers,
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
        serializer.save()

        headers = self.get_success_headers(serializer.data)

        return CustomResponse.success(
            message="Project created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
            headers=headers,
        )


class ProjectRetrieveUpdateDestroyView(APIView):

    def get_object(self, slug):
        try:
            obj = Project.objects.prefetch_related("tags").get(slug=slug)
            # TODO: MIGHT CHANGE LATER IF IT AFFECTS QUERY PERFORMANCE
            self.check_object_permissions(self.request, obj) # This triggers has_object_permission
            return obj
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")
        
    def get_project(self, slug):
        try:
            project = Project.objects.prefetch_related("tags").get(slug=slug)
            return project
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsProjectOwner()]

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
        project = self.get_project(slug)

        serializer = self.get_serializer(project)
        return CustomResponse.success(
            message="Project detail retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Edit a specific project",
        description="This endpoint allows authenticated users to edit the details of an existing project. The user must be the project owner to edit the project.",
        tags=tags,
        responses=PROJECT_UPDATE_EXAMPLE,
    )
    def patch(self, request, slug):
        project = self.get_object(slug)

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
        responses=PROJECT_DELETE_RESPONSE,
    )
    def delete(self, request, slug):
        project = self.get_object(slug)
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
    permission_classes = [IsAuthenticated, IsProjectOwner]
    
    def get_object(self, slug):
        try:
            obj = Project.objects.prefetch_related("tags").get(slug=slug)
            # TODO: MIGHT CHANGE LATER IF IT AFFECTS QUERY PERFORMANCE
            self.check_object_permissions(self.request, obj) # This triggers has_object_permission
            return obj
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

    @extend_schema(
        summary="Update project featured image",
        description="This endpoint allows authenticated users to upload or update their project featured image.",
        tags=tags,
        request=build_avatar_request_schema(
            prop1="featured_image", desc="Featured Image file"
        ),
        responses=FEATURED_IMAGE_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request, slug):
        project = self.get_object(slug)
        serializer = self.serializer_class(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return CustomResponse.success(
            message="Project image updated successfully.",
            data={
                "featured_image_url": project.featured_image_url,
            },
            status_code=status.HTTP_200_OK,
        )


class TagListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TagSerializer
    paginator_class = CustomPagination()
    paginator_class.page_size = 10

    @extend_schema(
        summary="Retrieve a list of tags",
        description="This endpoint allows authenticated users to view a list of all tags.",
        tags=tags,
        responses=TAG_LIST_RESPONSE_EXAMPLE,
    )
    def get(self, request):
        # all tags - not specific to anyone
        tags = Tag.objects.all()
        paginated_tags = self.paginator_class.paginate_queryset(tags, request)
        serializer = self.serializer_class(paginated_tags, many=True)

        return self.paginator_class.get_paginated_response(serializer.data)


class TagListGenericView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPagination

    @extend_schema(
        summary="Retrieve a list of tags",
        description="This endpoint allows authenticated users to view a list of all tags.",
        tags=tags,
        responses=TAG_LIST_RESPONSE_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="Tags retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ProjectTagAddView(APIView):
    permission_classes = (IsAuthenticated, IsProjectOwner)
    serializer_class = TagCreateSerializer

    def get_object(self, slug):
        try:
            obj = Project.objects.prefetch_related("tags").get(slug=slug)
            # TODO: MIGHT CHANGE LATER IF IT AFFECTS QUERY PERFORMANCE
            self.check_object_permissions(self.request, obj) # This triggers has_object_permission
            return obj
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

    @extend_schema(
        summary="Add tag to project",
        description="This endpoint allows authenticated users to add a new tag. Tags can be used to categorize or organize projects. Only authenticated users are allowed to add new tags. Tags are converted to lowercase when created.",
        tags=tags,
        responses=TAG_CREATE_RESPONSE_EXAMPLE,
    )
    def post(self, request, slug):
        project = self.get_object(slug)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        tag = None
        created = None
        tag_added = None

        with transaction.atomic():
            tag, created = serializer.save()

            current_tags = project.tags.all()

            if tag not in current_tags:
                # Link the tag to the project
                project.tags.add(tag)
                tag_added = True
            else:
                tag_added = False

        if created and tag_added:
            message = "New tag created and added to project successfully."
            status_code = status.HTTP_201_CREATED
        elif tag_added:
            message = "Existing tag added to project successfully."
            status_code = status.HTTP_200_OK
        else:
            message = "Tag already associated with this project."
            status_code = status.HTTP_200_OK

        tag_serializer = TagSerializer(tag)  # re-serialize

        return CustomResponse.success(
            message=message,
            data=tag_serializer.data,
            status_code=status_code,
        )


class TagRemoveView(APIView):
    permission_classes = (IsAuthenticated, IsProjectOwner)

    def get_tag(self, id):
        try:
            return Tag.objects.get(pk=id)
        except Tag.DoesNotExist:
            raise NotFoundError(err_msg="Tag not found.")

    def get_object(self, slug):
        try:
            obj = Project.objects.prefetch_related("tags").get(slug=slug)
            # TODO: MIGHT CHANGE LATER IF IT AFFECTS QUERY PERFORMANCE
            self.check_object_permissions(self.request, obj) # This triggers has_object_permission
            return obj
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

    @extend_schema(
        summary="Remove a tag from a project",
        description="This endpoint allows authenticated users to remove a specific tag from a project. The user must be authenticated and the tag will be removed based on the provided project slug and tag ID.",
        tags=tags,
        responses=TAG_REMOVE_RESPONSE_EXAMPLE,
    )
    def delete(self, request, project_slug, tag_id):
        """Remove a tag from a specific project."""

        # Get the project based on the slug
        project = self.get_object(project_slug)

        # Get the tag based on the tag ID
        tag = self.get_tag(tag_id)

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
    serializer_class = ReviewSerializer

    def get_project(self, slug):
        try:
            return Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise NotFoundError(err_msg="Project not found.")

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        summary="Retrieve all reviews for a project",
        description="This endpoint allows users to retrieve a list of all reviews for a specific project. It provides a collection of reviews with details such as the reviewer, rating, and feedback for the project.",
        tags=tags,
        responses=REVIEW_GET_RESPONSE_EXAMPLE,
    )
    def get(self, request, slug):
        project = self.get_project(slug)

        # Retrieve all reviews for the specified project
        reviews = Review.objects.filter(project=project)

        # Serialize the queryset
        serializer = self.serializer_class(reviews, many=True)
        # Return serialized data in response

        return CustomResponse.success(
            message="Project reviews retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Create a new review for a project",
        description="This endpoint allows authenticated users to submit a review for a specific project. Users cannot review their own project, and they can only submit one review per project. The review will be associated with the project and the user submitting it.",
        tags=tags,
        responses=REVIEW_CREATE_RESPONSE_EXAMPLE,
    )
    def post(self, request, slug):
        # Retrieve the project
        project = self.get_project(slug)

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

        # TODO: CHECK THE PERFORMANCE AND MAYBE MOVE TO LIST LATER
        project.review_percentage

        return CustomResponse.success(
            message="Review added successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )
