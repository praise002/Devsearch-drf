from rest_framework.test import APITestCase
from apps.common.utils import TestUtil
from apps.accounts.models import Otp
from unittest import mock

valid_data = {
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'testuser@example.com',
    'password': 'strong_password',
}

invalid_data = {
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'invalid_email',
    'password': 'short',
}

class TestAccounts(APITestCase):
    register_url = "/api/v1/auth/register/"
    login_url = "/api/v1/auth/token/"
    token_refresh_url = "/api/v1/auth/token/refresh/"
    logout_url = "/api/v1/auth/logout/"

    send_otp_url = "/api/v1/auth/send-otp/"
    verify_otp_url = "/api/v1/auth/verify-otp/"

    password_change_url = "/api/v1/auth/password/change/"
    password_reset_request_url = "/api/v1/auth/password-reset/"
    password_reset_confirm_url = "/api/v1/auth/password-reset/reset/"
    
    def setUp(self):
        self.new_user = TestUtil.new_user()
        self.verified_user = TestUtil.verified_user()
    
    def test_register(self):
        mock.patch("apps.accounts.emails.SendEmail", new="")
        
        # Valid Registration
        response = self.client.post(self.register_url, valid_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "message": "OTP sent for email verification.",
                "email": valid_data["email"],
            },
        )
        
        # Invalid Registration
        # mock.patch("apps.accounts.emails.SendEmail", new="")
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 400)
        
    def test_send_otp(self):
        new_user = self.new_user
        mock.patch("apps.accounts.emails.SendEmail", return_value=None)
        
        # OTP Sent for Existing User
        response = self.client.post(
            self.send_otp_url, {"email": new_user.email}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "message": "OTP sent successfully.",
            },
        )
        
        # Non-existent User
        response = self.client.post(
            self.send_otp_url, {"email": 'user@gmail.com'}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "error": "No account is associated with this email."
            },
        )
        
        # Invalid email
        response = self.client.post(
            self.send_otp_url, {"email": 'user'}
        )
        self.assertEqual(response.status_code, 400)
        

        
# python manage.py test apps.accounts.tests.TestAccounts.test_register
