from rest_framework.test import APITestCase
from apps.common.utils import TestUtil
from apps.accounts.models import Otp
from unittest import mock

valid_data = {
    "first_name": "Test",
    "last_name": "User",
    "email": "testuser@example.com",
    "password": "strong_password",
}

invalid_data = {
    "first_name": "Test",
    "last_name": "User",
    "email": "invalid_email",
    "password": "short",
}


class TestAccounts(APITestCase):
    register_url = "/api/v1/auth/register/"
    login_url = "/api/v1/auth/token/"
    token_refresh_url = "/api/v1/auth/token/refresh/"
    logout_url = "/api/v1/auth/token/revoke"

    send_email_url = "/api/v1/auth/otp"
    verify_email_url = "/api/v1/auth/otp/verify/"

    password_change_url = "/api/v1/auth/password-change/"
    password_reset_request_url = "/api/v1/auth/password-reset/"
    password_reset_confirm_url = "/api/v1/auth/password-reset/done/"

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
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 400)

        # Clear OTP After Verification
        otp_cleared = not Otp.objects.filter(user_id=self.new_user.id).exists()
        self.assertTrue(otp_cleared, "OTP should be cleared after verification.")

    def test_send_email(self):
        new_user = self.new_user
        mock.patch("apps.accounts.emails.SendEmail", return_value=None)

        # OTP Sent for Existing User
        response = self.client.post(self.send_email_url, {"email": new_user.email})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "message": "OTP sent successfully.",
            },
        )

        # Non-existent User
        response = self.client.post(self.send_email_url, {"email": "user@gmail.com"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"error": "No account is associated with this email."},
        )

        # Invalid email
        response = self.client.post(self.send_email_url, {"email": "user"})
        self.assertEqual(response.status_code, 400)

    def test_verify_email(self):
        new_user = self.new_user
        otp = "111111"
        mock.patch("apps.accounts.emails.SendEmail", new="")
        
        # Invalid OTP
        response = self.client.post(
            self.verify_email_url, {"email": new_user.email, "otp": "hgtr"}
        )
        self.assertEqual(response.status_code, 400)
        
        # OTP does not exist
        response = self.client.post(
            self.verify_email_url, {"email": new_user.email, "otp": int(otp)}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "error": "Invalid OTP provided.",
            },
        )
        
        # Valid OTP Verification
        otp = Otp.objects.create(user_id=new_user.id, otp=int(otp))
        response = self.client.post(
            self.verify_email_url,
            {"email": new_user.email, "otp": otp.otp},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Email verified successfully."},
        )
        
        # Expired OTP
        # Already Verified User
        otp = Otp.objects.create(user_id=new_user.id, otp=int("876547"))
        response = self.client.post(
            self.verify_email_url,
            {"email": new_user.email, "otp": otp.otp},
        ) #Or use verified user variable
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Email address already verified!"},
        )
        
        # Clear OTP After Verification
        otp_cleared = not Otp.objects.filter(user_id=new_user.id).exists()
        self.assertTrue(otp_cleared, "OTP should be cleared after verification.")

    def test_logout(self):
        auth_token = TestUtil.auth_token(self.verified_user)

        # Ensures if authorized user logs out successfully
        bearer = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}
        response = self.client.get(self.logout_url, **bearer)
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Logout successful."},
        )
    # def test_logout(self):
    #     # Successful Logout
        
    #    # Log in the user and get the refresh token
    #     verified_user = self.verified_user
    #     login_response = self.client.post(
    #         self.login_url,
    #         {"email": "testverifieduser@example.com", "password": "testpassword"},  # Ensure password matches
    #     )

    #     # Check login response and extract refresh token
    #     print(login_response.json())
    #     self.assertEqual(login_response.status_code, 200)
    #     refresh_token = login_response.json().get("access")
    #     self.assertIsNotNone(refresh_token, "Refresh token should be provided upon login")

    #     # Successful Logout using the refresh token
    #     bearer_headers = {"HTTP_AUTHORIZATION": f"Bearer {refresh_token}"}
    #     response = self.client.post(self.logout_url, **bearer_headers)

    #     # Check for successful logout response
    #     print(response.json())
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(
    #         response.json(),
    #         {"message": "Logout successful."},
    #     )

        # Invalid or Missing Refresh Token
        # self.bearer = {"HTTP_AUTHORIZATION": f"invalid_token"}
        # response = self.client.get(self.logout_url, **self.bearer)
        # # self.assertEqual(response.status_code, 401)
        # # self.assertEqual(
        # #     response.json(),
        # #     {
        # #         "message": "Auth Token is Invalid or Expired!",
        # #     },
        # # )
        # print(response.status_code)
        # print(response.json())

    def test_password_change(self):
        # Valid Password Change
        # Incorrect Current Password
        # Weak New Password
        pass

    def test_password_reset_request(self):
        # Send OTP to Registered Email
        # Non-existent Email
        # Clear Existing OTPs
        pass
    
    def test_password_reset_done(self):
        # Valid OTP Verification and Password Reset
        # Invalid OTP
        # Expired OTP
        # Clear OTP After Password Reset
        # Weak New Password
        pass


# python manage.py test apps.accounts.tests.TestAccounts.test_register
