from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.errors import ErrorCode
from apps.common.schema_examples import (
    AVATAR_URL,
    EMAIL_EXAMPLE,
    ERR_RESPONSE_STATUS,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
)
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer
from apps.profiles.serializers import (
    ProfileSerializer,
    ProfileSkillSerializer,
    SkillSerializer,
)

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
    "avatar_url": AVATAR_URL,
}

SKILL_EXAMPLE_1 = {
    "id": "6beeb28d-683d-4c48-984b-f7ce25a6f216",
    "name": "Frontend Developer",
    "description": "",
}

SKILL_EXAMPLE_2 = {
    "id": "6beeb28d-683d-4c48-984b-f7ce25a6f216",
    "name": "Backend Developer",
    "description": "Lorem ipsum",
}

SKILLS_EXAMPLE = (
    [
        {
            "id": "b8dab62e-3fc4-4f0d-bd92-ce5279396b7a",
            "name": "firebase",
        },
        {
            "id": "0d249872-b8ac-4871-a4af-edfbf5884bc2",
            "name": "django",
        },
    ],
)

PROFILE_EXAMPLES = [
    {
        "user": {
            "id": "84196b4d-4e67-4523-9abd-49d4463a774b",
            "username": "hannah-montana",
            "email": "hannah@gmail.com",
            "first_name": "Hannah",
            "last_name": "Montana",
        },
        "short_intro": "",
        "bio": "",
        "location": "",
        "social_github": "",
        "social_stackoverflow": "",
        "social_twitter": "",
        "social_linkedin": "",
        "skills": [],
        "avatar_url": AVATAR_URL,
    },
    {
        "user": {
            "id": "57a7ec20-24d7-487a-aa07-4d23ce6a066c",
            "username": "ese-oghene",
            "email": "admin@gmail.com",
            "first_name": "Ese",
            "last_name": "Oghene",
        },
        "short_intro": "",
        "bio": "",
        "location": "",
        "social_github": "",
        "social_stackoverflow": "",
        "social_twitter": "",
        "social_linkedin": "",
        "skills": [],
        "avatar_url": AVATAR_URL,
    },
]

PROFILE_LIST_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=ProfileSerializer,
        description="Profiles Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Profiles retrieved successfully.",
                    "data": PROFILE_EXAMPLES,
                },
            ),
        ],
    ),
}

PROFILE_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=ProfileSerializer,
        description="Profile Update Successful",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Profile updated successfully.",
                    "data": PROFILE_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        description="Permission Denied",
        response=ErrorResponseSerializer,
        examples=[
            OpenApiExample(
                name="Permission Denied",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You can only update your own profile.",
                    "code": ErrorCode.FORBIDDEN,
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}


PROFILE_DETAIL_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Profile Retrieve Successful",
        response=ProfileSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Profile detail retrieved successfully.",
                    "data": PROFILE_EXAMPLE,
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
}

IMAGE_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Image Update Successful",
        response=ProfileSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Profile image updated successfully.",
                    "data": {
                        "avatar_url": AVATAR_URL,
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

SKILL_LIST_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Skills Fetched",
        response=SkillSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Skills retrieved successfully.",
                    "data": SKILLS_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}

SKILL_CREATE_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        description="Skill Create Successful",
        response=ProfileSkillSerializer,
        examples=[
            OpenApiExample(
                name="Success Response with empty description",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Skill created successfully.",
                    "data": SKILL_EXAMPLE_1,
                },
            ),
            OpenApiExample(
                name="Success Response with description",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Skill created successfully.",
                    "data": SKILL_EXAMPLE_2,
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

# TODO: REMOVE LATER IF NOT USED
SKILL_GET_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Skill Retrieved",
        response=ProfileSkillSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Skill retrieved successfully.",
                    "data": SKILL_EXAMPLE_2,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        description="Permission Denied",
        response=ErrorResponseSerializer,
        examples=[
            OpenApiExample(
                name="Permission Denied",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You don't have permission to access this skill.",
                    "code": ErrorCode.FORBIDDEN,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Skill not found",
        examples=[
            OpenApiExample(
                name="Skill not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Skill not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

SKILL_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Skill Update Successfull",
        response=ProfileSkillSerializer,
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Skill updated successfully.",
                    "data": SKILL_EXAMPLE_2,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        description="Permission Denied",
        response=ErrorResponseSerializer,
        examples=[
            OpenApiExample(
                name="Permission Denied",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You don't have permission to access this skill.",
                    "code": ErrorCode.FORBIDDEN,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Skill not found",
        examples=[
            OpenApiExample(
                name="Skill not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Skill not found.",
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

SKILL_DELETE_RESPONSE_EXAMPLE = {
    204: None,
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        description="Permission Denied",
        response=ErrorResponseSerializer,
        examples=[
            OpenApiExample(
                name="Permission Denied",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You don't have permission to access this skill.",
                    "code": ErrorCode.FORBIDDEN,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Skill not found",
        examples=[
            OpenApiExample(
                name="Skill not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Skill not found.",
                    "code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
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
