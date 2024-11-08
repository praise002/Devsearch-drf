from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiResponse


from apps.accounts.validators import validate_uuid
from apps.common.serializers import ErrorResponseSerializer
from apps.profiles.models import Profile
from .models import Message
from .serializers import MessageSerializer

tags = ["Messages"]


# View for listing inbox messages
class InboxView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Retrieve user's inbox messages",
        description="This endpoint allows authenticated users to view their inbox messages. It returns a list of messages received by the user. Additionally, it provides a count of unread messages to indicate any new notifications in the user's inbox.",
        tags=tags,
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved inbox messages and unread count",
                response=MessageSerializer,
            ),
            401: OpenApiResponse(
                description="Unauthorized access - user must be authenticated",
                response=ErrorResponseSerializer,
            ),
        },
    )
    def get(self, request):
        messages = Message.objects.filter(recipient=request.user.profile)
        serializer = MessageSerializer(messages, many=True)

        unread_count = messages.filter(is_read=False).count()

        return Response(
            {"messages": serializer.data, "unread_count": unread_count},
            status=status.HTTP_200_OK,
        )


# View for viewing a specific message
class ViewMessage(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Retrieve a specific message",
        description="This endpoint allows an authenticated user to retrieve the details of a specific message by ID. If the message is unread, it will automatically be marked as read upon retrieval.",
        tags=tags,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                description="Successfully retrieved the message details.",
            ),
            404: OpenApiResponse(
                description="Message not found or invalid message ID."
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided or invalid."
            ),
        },
    )
    def get(self, request, id):
        if not validate_uuid(id):
            raise Http404("Invalid message id")

        message = get_object_or_404(
            request.user.profile.messages.select_related("sender__user", "recipient"),
            id=id,
        )
        serializer = MessageSerializer(message)

        # Mark the message as read if it's currently unread
        if not message.is_read:
            message.is_read = True
            message.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


# View for creating a new message
class CreateMessage(APIView):
    @extend_schema(
        summary="Send a message to a specific user",
        description="This endpoint allows an anyone to send a message to a specific recipient by their profile ID. The sender's profile is automatically associated with the message if they are logged in. Users cannot message themselves.",
        tags=tags,
        responses={
            201: OpenApiResponse(
                response=MessageSerializer,
                description="Message successfully created and sent.",
            ),
            400: OpenApiResponse(
                description="Bad request - validation error (e.g., trying to message oneself)."
            ),
            404: OpenApiResponse(
                description="Recipient profile not found or invalid profile ID."
            ),
        },
    )
    def post(self, request, id):
        if not validate_uuid(id):
            raise Http404("Invalid profile id")
        recipient = get_object_or_404(Profile, id=id)

        # try:
        #     sender = request.user.profile
        # except:
        #     sender = None

        sender = request.user.profile if request.user.is_authenticated else None

        # Prevent users from messaging themselves
        if sender and sender.id == recipient.id:
            raise ValidationError("You cannot message yourself.")

        data = request.data.copy()

        data["recipient"] = recipient.id

        serializer = MessageSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=sender)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# View for deleting a message
class DeleteMessage(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Delete a specific message",
        description="This endpoint allows an authenticated user to delete a specific message they received. The message ID must be valid, and the message must belong to the authenticated user. Upon successful deletion, a confirmation message is returned.",
        tags=tags,
        responses={
            204: OpenApiResponse(description="Message deleted successfully."),
            404: OpenApiResponse(
                description="Message not found or invalid message ID."
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def delete(self, request, id):
        if not validate_uuid(id):
            raise Http404("Invalid message id")

        message = get_object_or_404(Message, id=id, recipient=request.user.profile)

        message.delete()
        return Response(
            {"detail": "Message deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
