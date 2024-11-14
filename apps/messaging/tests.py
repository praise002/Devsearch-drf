from rest_framework.test import APITestCase
from apps.common.utils import TestUtil
from unittest import mock

class TestProjects(APITestCase):
    login_url = "/api/v1/auth/token/"
    
    inbox_url = "/api/v1/messages/inbox/"
    view_message_url = "/api/v1/messages/message/{id}/"
    create_message_url = "/api/v1/messages/message/create-message/{id}/"
    delete_message_url = "/api/v1/messages/message/delete-message/{id}/"
    
    def setUp(self):
        # user
        verified_user = TestUtil.verified_user()
        another_verified_user = TestUtil.another_verified_user()
        self.verified_user = verified_user

        # auth
        verified_user = self.verified_user
        login_response = self.client.post(
            self.login_url,
            {
                "email": verified_user.email,
                "password": "testpassword",
            },  
        )

        access_token = login_response.json().get("access")
        self.bearer = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}
    
    def test_inbox_get(self):
        # Test that authenticated users can retrieve their inbox messages.
        # Test that the correct number of unread messages is returned.
        # Test that unauthenticated users receive a 401 error.
        pass
    
    def test_view_message_get(self):
        # Test that authenticated users can retrieve a specific message by ID.
        # Test that a 404 error is returned for an invalid or non-existent message ID.
        # Test that the message is marked as read when viewed for the first time.
        # Test that unauthenticated users receive a 401 error.
        pass
    
    def test_create_message_post(self):
        # Test that authenticated and unauthenticated users can send a message to another user.
        # Test that users cannot message themselves.
        # Test that the correct recipient is set for the message.
        # Test that a 404 error is returned for an invalid recipient ID.
        # Test that a 400 error is returned for invalid data.
        pass
    
    def test_delete_message(self):
        # Test that authenticated users can delete a message they received.
        # Test that a 404 error is returned if the message does not belong to the user.
        # Test that a 404 error is returned for an invalid message ID.
        # Test that unauthenticated users cannot delete messages.
        pass