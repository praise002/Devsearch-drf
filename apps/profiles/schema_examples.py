from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.schema_examples import (
    AVATAR_URL,
    EMAIL_EXAMPLE,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
)
from apps.common.serializers import ErrorDataResponseSerializer
from apps.profiles.serializers import ProfileSerializer

PROFILE_EXAMPLE = {
    "user": {
        "id": UUID_EXAMPLE,
        "email": EMAIL_EXAMPLE,
        "username": "bob-joe",
        "first_name": "Bob",
        "last_name": "Doe",
    },
    "short_intro": "",
    "bio": "",
    "location": "",
    "social_github": "",
    "social_stackoverflow": "",
    "social_twitter": "",
    "social_linkedin": "",
    "skills": [],
    "image_url": AVATAR_URL,
}


PROFILE_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=ProfileSerializer,
        description="Profile Update Successful",
        examples=[
            OpenApiExample(
                name="Profile Update Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Profile updated successfully.",
                    "data": PROFILE_EXAMPLE,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
    401: UNAUTHORIZED_USER_RESPONSE,
}

PROFILE_RETRIEVE_RESPONSE_EXAMPLE = {
    # 200: ShippingAddressResponseSerializer,
    #     401: ErrorResponseSerializer
    200: OpenApiResponse(
        description="Profile Retrieve Successful",
        response=ProfileSerializer,
        examples=[
            OpenApiExample(
                name="Profile Retrieve Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Profile retrieved successfully.",
                    "data": PROFILE_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}


def build_avatar_request_schema(prop1="image", desc="Profile image file"):
    return {
        "multipart/form-data": {
            "type": "object",
            "properties": {
                prop1: {
                    "type": "string",
                    "format": "binary",
                    "description": desc,
                },
            },
            "required": [prop1],
        }
    }
