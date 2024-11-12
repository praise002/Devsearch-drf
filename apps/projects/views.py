from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer, SuccessResponseSerializer

from .models import Project, Tag, Review
from .serializers import ProjectSerializer, TagSerializer, ReviewSerializer

tags = ["Projects"]

class ProjectListView(APIView):
    serializer_class = ProjectSerializer
    
    @extend_schema(
        summary="Retrieve a list of user projects",
        description="This endpoint allows authenticated and unauthenticated users to view a list of all user projects in the system.",
        operation_id="list_projects",
        tags=tags,
        responses={
            200: SuccessResponseSerializer, 
            #TODO: ADD OTHER ERRORS
        },
    )
    
    def get(self, request):
        projects = Project.objects.select_related("owner").prefetch_related("tags")
        serializer = self.serializer_class(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectDetailView(APIView):
    serializer_class = ProjectSerializer
    
    @extend_schema(
        summary="View a project details",
        description="This endpoint allows authenticated and unauthenticated users to view detailed information about a specific project.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer, 
            404: ErrorResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
    )
    
    def get(self, request, slug):
        try:
            project = (
                Project.objects.select_related("owner__user")
                .prefetch_related("tags")
                .get(slug=slug)
            )
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )


class RelatedProjectsView(APIView):
    """
    API view to retrieve related projects for a specific project.
    """
    serializer_class = ProjectSerializer
    
    @extend_schema(
        summary="View related projects for a specific project",
        description="This endpoint allows users to view a list of projects that are related to a specific project. The related projects are determined based on project categories, tags, or other relevant factors. Users can retrieve a list of related projects, which may help them discover similar or complementary projects within the platform.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer, 
            404: ErrorResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ProjectCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer 
    
    @extend_schema(
        summary="Create a new project",
        description="This endpoint allows authenticated users to create a new project. The user must be logged in to submit project details. Once the project is created, it is saved in the system and can be retrieved or updated later.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer, 
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user.profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectEditDeleteView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer 
    
    @extend_schema(
        summary="Edit a specific project",
        description="This endpoint allows authenticated users to edit the details of an existing project. The user must be the project owner to edit the project.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer, 
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            #TODO: ADD OTHER ERRORS
        },
    )

    def patch(self, request, slug):
        profile = request.user.profile

        project = get_object_or_404(profile.projects, slug=slug)
        serializer = self.serializer_class(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a specific project",
        description="This endpoint allows authenticated users to delete an existing project. Only the project owner can delete the project. The project will be permanently removed from the system.",
        tags=tags,
        responses={
            204: ErrorResponseSerializer,  # Successfully deleted project (no content in response body)
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )

    def delete(self, request, slug):
        profile = request.user.profile

        project = get_object_or_404(profile.projects, slug=slug)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TagSerializer 

    @extend_schema(
        summary="Create a new tag",
        description="This endpoint allows authenticated users to create a new tag. Tags can be used to categorize or organize projects. Only authenticated users are allowed to create new tags.",
        tags=tags,
        responses={
            201: SuccessResponseSerializer,  # Successfully created tag
            400: ErrorResponseSerializer,  # Validation error or bad request
            401: ErrorResponseSerializer,
        }, 
    )

    def post(self, request, slug):
        profile = request.user.profile
        project = get_object_or_404(profile.projects, slug=slug)

        # Get tag name from request and handle missing or empty value
        tag_name = request.data.get("name")
        if not tag_name:
            return Response(
                {"error": "Tag name is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        tag_name = tag_name.lower()

        tag, _ = Tag.objects.get_or_create(name=tag_name)

        # Link the tag to the project
        project.tags.add(tag)

        serializer = self.serializer_class(tag)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagRemoveView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Remove a tag from a project",
        description="This endpoint allows authenticated users to remove a specific tag from a project. The user must be authenticated and the tag will be removed based on the provided project slug and tag ID.",
        tags=tags,
        responses={
            204: SuccessResponseSerializer,  # Successfully removed tag
            404: ErrorResponseSerializer,  # Project or tag not found
            400: ErrorResponseSerializer,  # Bad request
            401: ErrorResponseSerializer,
        },
    ) 

    def delete(self, request, project_slug, tag_id):
        """Remove a tag from a specific project."""
        profile = request.user.profile

        # Get the project based on the slug
        project = get_object_or_404(profile.projects, slug=project_slug)

        # Get the tag based on the tag ID
        tag = get_object_or_404(Tag, pk=tag_id)

        # Check if the tag is associated with the project
        if tag not in project.tags.all():
            return Response(
                {"error": "Tag not associated with this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Remove the association of this tag from the project
        project.tags.remove(tag)

        return Response(
            {"message": "Tag removed from the project successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


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
        },
    )


    def post(self, request, slug):
        # Retrieve the project
        project = get_object_or_404(Project, slug=slug)

        # Check if the user is trying to review their own project
        if project.owner == request.user.profile:
            return Response(
                {"error": "You cannot review your own project."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if the user has already reviewed the project
        existing_review = project.reviews.filter(reviewer=request.user.profile).first()
        if existing_review:
            return Response(
                {"error": "You have already reviewed this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a review using the request data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the review and associate it with the project
        serializer.save(reviewer=request.user.profile, project=project)

        project.review_percentage

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        },
    )


    def get(self, request, slug):
        # Retrieve all reviews for the specified project ID
        reviews = Review.objects.filter(project__slug=slug)
        # Serialize the queryset
        serializer = self.serializer_class(reviews, many=True)
        # Return serialized data in response
        return Response(serializer.data, status=status.HTTP_200_OK)
