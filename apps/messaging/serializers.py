from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    # recipient = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            # "recipient",
            "name",
            "email",
            "subject",
            "body",
            "is_read",
            "created",
        ]
        read_only_fields = ["sender", "created", "is_read"]
