from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.errors import ErrorCode
from apps.common.schema_examples import (
    AVATAR_URL,
    ERR_RESPONSE_STATUS,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
)
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer
from apps.projects.serializers import ProjectSerializer, ReviewSerializer, TagSerializer

TAGS = [
    {"id": "cd975686-d423-4591-9207-655ab8b5c04d", "name": "React"},
    {"id": "090604e6-2f7e-46e3-be6e-73d1521a4697", "name": "Django"},
]

TAG = {"id": "9b57e617-3937-45c7-8acf-7fee0f44d7e3", "name": "supabase"}

REVIEW = {
    "id": "1d9ea9d4-e158-4095-a8e5-b340a80d3cbd",
    "value": "up",
    "content": "Test",
}

REVIEWS = [
    {
        "id": "1d9ea9d4-e158-4095-a8e5-b340a80d3cbd",
        "value": "up",
        "content": "Review 1",
    },
    {"id": UUID_EXAMPLE, "value": "down", "content": "Review 2"},
]

PROJECTS = [
    {
        "id": "82e84127-9c15-45d1-b919-0cd3e4124169",
        "title": "E-commerce Platform",
        "slug": "e-commerce-platform",
        "owner": "Ese Oghene",
        "featured_image": "null",
        "featured_image_url": AVATAR_URL,
        "description": "A full-featured e-commerce platform with payment integration and inventory management.",
        "source_link": "https://github.com/user/ecommerce-platform",
        "demo_link": "https://ecommerce-demo.example.com",
        "tags": [
            {"id": "cd975686-d423-4591-9207-655ab8b5c04d", "name": "React"},
            {"id": "090604e6-2f7e-46e3-be6e-73d1521a4697", "name": "Django"},
        ],
        "vote_total": 0,
        "vote_ratio": 0,
        "review_percentage": "null",
    },
    {
        "id": "8421d7f0-fca2-4f08-a030-2d92963fd697",
        "title": "Event Management System",
        "slug": "event-management-system",
        "owner": "Ese Oghene",
        "featured_image": "null",
        "featured_image_url": "",
        "description": "Platform for organizing and managing events with ticket sales.",
        "source_link": "https://github.com/user/event-system",
        "demo_link": "https://events-demo.example.com",
        "tags": [],
        "vote_total": 0,
        "vote_ratio": 0,
        "review_percentage": "null",
    },
    {
        "id": "43d78658-3d02-4c73-99be-e35bc1e136c4",
        "title": "Language Learning App",
        "slug": "language-learning-app",
        "owner": "Ese Oghene",
        "featured_image": "null",
        "featured_image_url": "",
        "description": "Interactive platform for learning new languages with speech recognition.",
        "source_link": "https://github.com/user/language-app",
        "demo_link": "https://language-demo.example.com",
        "tags": [],
        "vote_total": 0,
        "vote_ratio": 0,
        "review_percentage": "null",
    },
]

PROJECT_EXAMPLE = {
    "id": "82e84127-9c15-45d1-b919-0cd3e4124169",
    "title": "E-commerce Platform",
    "slug": "e-commerce-platform",
    "owner": "Ese Oghene",
    "featured_image": "null",
    "featured_image_url": "",
    "description": "A full-featured e-commerce platform with payment integration and inventory management.",
    "source_link": "https://github.com/user/ecommerce-platform",
    "demo_link": "https://ecommerce-demo.example.com",
    "tags": [
        {"id": "cd975686-d423-4591-9207-655ab8b5c04d", "name": "React"},
        {"id": "090604e6-2f7e-46e3-be6e-73d1521a4697", "name": "Django"},
    ],
    "vote_total": 0,
    "vote_ratio": 0,
    "review_percentage": "null",
}


PROJECT_EXAMPLE_1 = [
    {
        "id": "6fd745ef-24f9-45d7-88f2-2a5a51af0502",
        "title": "Event Management System",
        "slug": "event-management-system",
        "owner": "Ese Oghene",
        "featured_image": "null",
        "featured_image_url": "",
        "description": "Platform for organizing and managing events with ticket sales.",
        "source_link": "https://github.com/user/event-system",
        "demo_link": "https://events-demo.example.com",
        "tags": [{"id": "090604e6-2f7e-46e3-be6e-73d1521a4697", "name": "Django"}],
        "vote_total": 0,
        "vote_ratio": 0,
        "review_percentage": "null",
    }
]

PROJECT_CREATE_EXAMPLE = {
    "id": "8421d7f0-fca2-4f08-a030-2d92963fd697",
    "title": "Event Management System",
    "slug": "event-management-system",
    "owner": "Ese Oghene",
    "featured_image": "null",
    "featured_image_url": "",
    "description": "Platform for organizing and managing events with ticket sales.",
    "source_link": "https://github.com/user/event-system",
    "demo_link": "https://events-demo.example.com",
    "tags": [],
    "vote_total": 0,
    "vote_ratio": 0,
    "review_percentage": "null",
}


PROJECT_LIST_EXAMPLE = {
    200: OpenApiResponse(
        description="Projects Fetched",
        response=ProjectSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Projects retrieved successfully.",
                    "data": PROJECTS,
                },
            ),
        ],
    ),
}

PROJECT_CREATE_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        description="Project Create Successfull",
        response=ProjectSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Project created successfully.",
                    "data": PROJECT_CREATE_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}


PROJECT_DETAIL_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Project retrieval Successfull",
        response=ProjectSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Project detail retrieved successfully.",
                    "data": PROJECT_EXAMPLE,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Project not found",
        examples=[
            OpenApiExample(
                name="Project not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Project not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

PROJECT_UPDATE_EXAMPLE = {
    200: OpenApiResponse(
        description="Project Update Successfull",
        response=ProjectSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Project updated successfully.",
                    "data": PROJECT_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Permission Denied",
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Project not found",
        examples=[
            OpenApiExample(
                name="Project not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Project not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}

PROJECT_DELETE_RESPONSE = {
    204: None,
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Permission Denied",
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Project not found",
        examples=[
            OpenApiExample(
                name="Project not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Project not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

RELATED_PROJECT_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Related Project retrieval Successfull",
        response=ProjectSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Related projects retrieved successfully.",
                    "data": PROJECT_EXAMPLE_1,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Project not found",
        examples=[
            OpenApiExample(
                name="Project not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Project not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

FEATURED_IMAGE_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Featured Image Update Successful",
        response=ProjectSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Project image updated successfully.",
                    "data": {
                        "featured_image_url": AVATAR_URL,
                    },
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}

TAG_LIST_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Tags Fetched",
        response=TagSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Tags retrieved successfully.",
                    "data": TAGS,
                },
            ),
        ],
    ),
}

TAG_CREATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Tag Added to Project",
        response=TagSerializer,
        examples=[
            OpenApiExample(
                name="Success Response 1",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Existing tag added to project successfully.",
                    "data": TAG,
                },
            ),
            OpenApiExample(
                name="Success Response 2",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Tag already associated with this project.",
                    "data": TAG,
                },
            ),
        ],
    ),
    201: OpenApiResponse(
        description="Tag Created and Added to Project",
        response=TagSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "New tag created and added to project successfully.",
                    "data": TAG,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Permission Denied",
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Project not found",
        examples=[
            OpenApiExample(
                name="Project not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Project not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}

TAG_REMOVE_RESPONSE_EXAMPLE = {
    204: None,
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Permission Denied",
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Not found",
        examples=[
            OpenApiExample(
                name="Project not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Project not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
            OpenApiExample(
                name="Tag not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Tag not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

REVIEW_GET_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Reviews Fetched",
        response=ReviewSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Project reviews retrieved successfully.",
                    "data": REVIEWS,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Project not found",
        examples=[
            OpenApiExample(
                name="Project not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Project not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

REVIEW_CREATE_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        description="Review Added to Project",
        response=ReviewSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Review added successfully.",
                    "data": REVIEW,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        description="Permission Denied",
        response=ReviewSerializer,
        examples=[
            OpenApiExample(
                name="Permission Denied",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You cannot review your own project.",
                    "code": ErrorCode.FORBIDDEN,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Project not found",
        examples=[
            OpenApiExample(
                name="Project not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Project not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
    409: OpenApiResponse(
        description="Already reviewed Project",
        response=ReviewSerializer,
        examples=[
            OpenApiExample(
                name="Existing Review",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You have already reviewed this project.",
                    "code": ErrorCode.ALREADY_EXISTS,
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}
