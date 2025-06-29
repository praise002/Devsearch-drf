from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import NotFoundError
from apps.common.pagination import CustomPagination
from apps.common.responses import CustomResponse
from apps.messaging.schema_examples import (
    CREATE_MESSAGE_RESPONSE_EXAMPLE,
    DELETE_MESSAGE_RESPONSE_EXAMPLE,
    INBOX_RESPONSE_EXAMPLE,
    VIEW_MESSAGE_RESPONSE_EXAMPLE,
)
from apps.profiles.models import Profile

from .models import Message
from .serializers import MessageSerializer

tags = ["Messages"]


# View for listing inbox messages
class InboxGenericView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ["subject", "body"]

    @extend_schema(
        summary="Retrieve user's inbox messages",
        description=(
            "This endpoint allows authenticated users to view their inbox messages. "
            "It supports filtering messages using a search term. Additionally, it provides "
            "a count of unread messages."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search messages by (e.g., subject or body).",
            ),
        ],
        responses=INBOX_RESPONSE_EXAMPLE,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return the filtered queryset of messages for the authenticated user.
        """
        return Message.objects.filter(recipient=self.request.user.profile)

    def list(self, request, *args, **kwargs):
        """
        Override the default list method to include unread_count in the response.
        """
        queryset = self.filter_queryset(self.get_queryset())  # Apply filters
        page = self.paginate_queryset(queryset)

        unread_count = self.get_queryset().filter(is_read=False).count()  # Unread count

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {
                    "results": serializer.data,
                    "unread_count": unread_count,
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="Inbox retrieved successfully.",
            data={
                "results": serializer.data,
                "unread_count": unread_count,
            },
            status_code=status.HTTP_200_OK,
        )


# View for viewing a specific message
class ViewMessage(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer

    @extend_schema(
        summary="Retrieve a specific message",
        description="This endpoint allows an authenticated user to retrieve the details of a specific message by ID. If the message is unread, it will automatically be marked as read upon retrieval.",
        tags=tags,
        responses=VIEW_MESSAGE_RESPONSE_EXAMPLE,
    )
    def get(self, request, id):

        try:
            message = request.user.profile.messages.select_related(
                "sender__user", "recipient"
            ).get(id=id)
        except Message.DoesNotExist:
            raise NotFoundError(err_msg="Message not found.")

        serializer = self.serializer_class(message)

        # Mark the message as read if it's currently unread
        if not message.is_read:
            message.is_read = True
            message.save()

        return CustomResponse.success(
            message="Message retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


# View for creating a new message
class CreateMessage(APIView):
    serializer_class = MessageSerializer

    @extend_schema(
        summary="Send a message to a specific user",
        description="This endpoint allows an anyone to send a message to a specific recipient by their profile ID. The sender's profile is automatically associated with the message if they are logged in. Users cannot message themselves.",
        tags=tags,
        responses=CREATE_MESSAGE_RESPONSE_EXAMPLE,
    )
    def post(self, request, username):

        try:
            recipient = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFoundError(err_msg="Profile not found.")

        # try:
        #     sender = request.user.profile
        # except:
        #     sender = None

        sender = request.user.profile if request.user.is_authenticated else None

        # Prevent users from messaging themselves
        if sender and sender.id == recipient.id:
            raise ValidationError("You cannot message yourself.")

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=sender, recipient=recipient)

        return CustomResponse.success(
            message="Message sent successfully.", status_code=status.HTTP_201_CREATED
        )


# View for deleting a message
class DeleteMessage(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Delete a specific message",
        description="This endpoint allows an authenticated user to delete a specific message they received. The message ID must be valid, and the message must belong to the authenticated user. Upon successful deletion, a confirmation message is returned.",
        tags=tags,
        responses=DELETE_MESSAGE_RESPONSE_EXAMPLE,
    )
    def delete(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id, recipient=request.user.profile)
        except Message.DoesNotExist:
            raise NotFoundError(err_msg="Message not found.")

        message.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
