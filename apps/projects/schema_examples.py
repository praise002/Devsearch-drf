from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.errors import ErrorCode
from apps.common.schema_examples import ERR_RESPONSE_STATUS, SUCCESS_RESPONSE_STATUS
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer
from apps.projects.serializers import ProjectResponseSerializer, ProjectSerializer

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
    200: ProjectResponseSerializer,
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
    422: ErrorDataResponseSerializer,
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
