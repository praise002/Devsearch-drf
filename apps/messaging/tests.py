from rest_framework.test import APITestCase

from apps.common.utils import TestUtil
from apps.messaging.models import Message


class TestMessages(APITestCase):
    login_url = "/api/v1/auth/token/"
    inbox_url = "/api/v1/messages/inbox/"
    retrieve_del_message_url = "/api/v1/messages/{id}/"
    create_message_url = "/api/v1/messages/{username}/"

    def setUp(self):
        # Create verified users
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

        # Create a test message
        self.message1 = Message.objects.create(
            sender=self.user2.profile,
            recipient=self.user1.profile,
            name="Test Other",
            email=self.user2.email,
            subject="Subject",
            body="Test message",
        )

        self.message2 = Message.objects.create(
            sender=self.user1.profile,
            recipient=self.user2.profile,
            name="Test Other 2",
            email=self.user1.email,
            subject="Subject",
            body="Test message",
        )

    def test_inbox_get(self):
        # Test that unauthenticated users receive a 401 error.
        response = self.client.get(self.inbox_url)
        self.assertEqual(response.status_code, 401)
        # Test that authenticated users can retrieve their inbox messages.
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.inbox_url)
        self.assertEqual(response.status_code, 200)

        # Test that the correct number of unread messages is returned.
        self.assertEqual(response.data["data"]["unread_count"], 1)

    def test_message_get(self):
        # Test that unauthenticated users receive a 401 error.
        url = self.retrieve_del_message_url.format(id=self.message1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        # Authenticated and valid message ID
        self.client.force_authenticate(user=self.user1)
        url = self.retrieve_del_message_url.format(id=self.message1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Non-existent message ID
        url = self.retrieve_del_message_url.format(
            id="c478eeb0-7c7f-4738-ba3a-6afe69c3150e"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test that the message is marked as read when viewed for the first time
        message = Message.objects.get(id=self.message1.id)
        self.assertTrue(message.is_read)

        # test 403
        url = self.retrieve_del_message_url.format(id=self.message2.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_message_delete(self):
        # Test that unauthenticated users cannot delete messages
        url = self.retrieve_del_message_url.format(id=self.message1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)

        # Test that authenticated users can delete a message they received
        self.client.force_authenticate(user=self.user1)
        url = self.retrieve_del_message_url.format(id=self.message1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # Non-existent message id or id does not belong to user
        url = self.retrieve_del_message_url.format(
            id="c478eeb0-7c7f-4738-ba3a-6afe69c3150e"
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # test 403
        url = self.retrieve_del_message_url.format(id=self.message2.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_message_post(self):
        data = {
            "name": "Test Other",
            "email": "test@gmail.com",
            "subject": "Subject",
            "body": "Test message",
        }

        # Test that unauthenticated users can send a message to another user.
        url = self.create_message_url.format(username=self.user2.username)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)

        # Test that authenticated users can send a message to another user.
        self.client.force_authenticate(user=self.user1)
        url = self.create_message_url.format(username=self.user2.username)

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

        # Test that users cannot message themselves.
        url = self.create_message_url.format(username=self.user1.username)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

        # Test that a 404 error is returned for an non-existent recipient username.
        url = self.create_message_url.format(username="non-existent")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

        # Test that a 422 error is returned for invalid data.
        url = self.create_message_url.format(username=self.user2.username)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 422)
