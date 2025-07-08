from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.errors import ErrorCode
from apps.common.schema_examples import ERR_RESPONSE_STATUS, SUCCESS_RESPONSE_STATUS
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer
from apps.messaging.serializers import MessageSerializer

MESSAGES_EXAMPLE = [
    {
        "id": "0f13428d-6ae5-4c3e-bf62-0723a9fa10c6",
        "sender": "e2985dac-bb6b-4c19-94e1-77cffe375cda",
        "recipient": "efbfdd5b-5296-42ca-8267-7cdf951e296b",
        "name": "Hannah",
        "email": "hannah@gmail.com",
        "subject": "Test Subject",
        "body": "Test body",
        "is_read": False,
        "created": "2025-06-26T16:48:39.411093Z",
    },
    {
        "id": "acfeae69-beba-441a-8b21-a429d643b7e3",
        "sender": "null",
        "recipient": "efbfdd5b-5296-42ca-8267-7cdf951e296b",
        "name": "string",
        "email": "user@example.com",
        "subject": "string",
        "body": "string",
        "is_read": False,
        "created": "2025-06-26T16:33:58.509365Z",
    },
]

MESSAGE_EXAMPLE_1 = {
    "id": "0f13428d-6ae5-4c3e-bf62-0723a9fa10c6",
    "sender": "e2985dac-bb6b-4c19-94e1-77cffe375cda",
    "recipient": "efbfdd5b-5296-42ca-8267-7cdf951e296b",
    "name": "Hannah",
    "email": "hannah@gmail.com",
    "subject": "Test Subject",
    "body": "Test body",
    "is_read": True,
    "created": "2025-06-26T16:48:39.411093Z",
}


INBOX_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Messages Fetched",
        response=MessageSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Inbox retrieved successfully.",
                    "data": {"results": MESSAGES_EXAMPLE, "unread_count": 2},
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}

VIEW_MESSAGE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Message Retrieval Successful",
        response=MessageSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Message retrieved successfully.",
                    "data": MESSAGE_EXAMPLE_1,
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
        description="Message not found",
        examples=[
            OpenApiExample(
                name="Message not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Message not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

CREATE_MESSAGE_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        description="Message Sent Successful",
        response=MessageSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Message sent successfully.",
                },
            ),
        ],
    ),
    403: OpenApiResponse(
        description="Permission Denied",
        response=ErrorResponseSerializer,
        examples=[
            OpenApiExample(
                name="Permission Denied",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You cannot message yourself.",
                    "code": ErrorCode.FORBIDDEN,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Profile not found",
        examples=[
            OpenApiExample(
                name="Profile not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Profile not found.",
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


DELETE_MESSAGE_RESPONSE_EXAMPLE = {
    204: None,
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Permission Denied",
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Message not found",
        examples=[
            OpenApiExample(
                name="Message not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Message not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}
