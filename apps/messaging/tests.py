from rest_framework.test import APITestCase
from apps.common.utils import TestUtil

from apps.messaging.models import Message


class TestMessages(APITestCase):
    login_url = "/api/v1/auth/token/"

    inbox_url = "/api/v1/messages/inbox/"
    view_message_url = "/api/v1/messages/{id}/"
    create_message_url = "/api/v1/messages/create/{profile_id}/"
    delete_message_url = "/api/v1/messages/delete/{message_id}/"

    def setUp(self):
        # Create verified users
        self.verified_user = TestUtil.verified_user()
        self.other_verified_user = TestUtil.other_verified_user()

        # auth
        login_response = self.client.post(
            self.login_url,
            {
                "email": self.verified_user.email,
                "password": "testpassword",
            },
        )

        access_token = login_response.json().get("access")
        self.bearer = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

        # Create a test message
        self.message = Message.objects.create(
            sender=self.other_verified_user.profile,
            recipient=self.verified_user.profile,
            name="Test Other",
            email=self.other_verified_user.email,
            subject="Subject",
            body="Test message",
        )

    def test_inbox_get(self):
        # Test that authenticated users can retrieve their inbox messages.
        response = self.client.get(self.inbox_url, **self.bearer)
        self.assertEqual(response.status_code, 200)

        # Test that the correct number of unread messages is returned.
        self.assertEqual(response.data["unread_count"], 1)

        # Test that unauthenticated users receive a 401 error.
        response = self.client.get(self.inbox_url)
        self.assertEqual(response.status_code, 401)

    def test_view_message_get(self):
        # Authenticated and valid message ID
        url = self.view_message_url.format(id=self.message.id)
        response = self.client.get(url, **self.bearer)
        self.assertEqual(response.status_code, 200)

        # Invalid message ID
        url = self.view_message_url.replace("<str:id>", "invalid-id")
        response = self.client.get(url, **self.bearer)
        self.assertEqual(response.status_code, 404)

        # Non-existent message ID
        url = self.view_message_url.format(id="c478eeb0-7c7f-4738-ba3a-6afe69c3150e")
        response = self.client.get(url, **self.bearer)
        self.assertEqual(response.status_code, 404)

        # Test that the message is marked as read when viewed for the first time
        message = Message.objects.get(id=self.message.id)
        self.assertTrue(message.is_read)

        # Test that unauthenticated users receive a 401 error.
        url = self.view_message_url.format(id=self.message.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_create_message_post(self):
        # Test that authenticated users can send a message to another user.
        url = self.create_message_url.format(
            profile_id=self.other_verified_user.profile.id
        )
        data = {
            "name": "Test Other",
            "email": "test@gmail.com",
            "subject": "Subject",
            "body": "Test message",
        }

        response = self.client.post(url, data, **self.bearer)
        self.assertEqual(response.status_code, 201)

        # Test that unauthenticated users can send a message to another user.
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

        # Test that users cannot message themselves.
        url = self.create_message_url.format(profile_id=self.verified_user.profile.id)
        response = self.client.post(url, data, **self.bearer)
        self.assertEqual(response.status_code, 400)

        # Test that a 404 error is returned for an invalid recipient ID.
        url = self.create_message_url.format(profile_id="invalid-profile_id")
        response = self.client.post(url, data, **self.bearer)
        self.assertEqual(response.status_code, 404)

        # Test that a 404 error is returned for an non-existent recipient ID.
        url = self.create_message_url.format(
            profile_id="c478eeb0-7c7f-4738-ba3a-6afe69c3150e"
        )
        response = self.client.post(url, data, **self.bearer)
        self.assertEqual(response.status_code, 404)

        # Test that a 400 error is returned for invalid data.
        url = self.create_message_url.format(
            profile_id=self.other_verified_user.profile.id
        )
        response = self.client.post(url, {}, **self.bearer)
        self.assertEqual(response.status_code, 400)

    def test_delete_message(self):
        # Test that authenticated users can delete a message they received
        url = self.delete_message_url.format(message_id=self.message.id)
        response = self.client.delete(url, **self.bearer)
        self.assertEqual(response.status_code, 204)

        # Non-existent message id or id does not belong to user
        url = self.delete_message_url.format(
            message_id="c478eeb0-7c7f-4738-ba3a-6afe69c3150e"
        )
        response = self.client.delete(url, **self.bearer)
        self.assertEqual(response.status_code, 404)

        # Invalid message ID
        url = self.delete_message_url.format(message_id="invalid-id")
        response = self.client.delete(url, **self.bearer)
        self.assertEqual(response.status_code, 404)

        # Test that unauthenticated users cannot delete messages
        url = self.delete_message_url.format(message_id=self.message.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
