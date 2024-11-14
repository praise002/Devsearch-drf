from rest_framework.test import APITestCase
from apps.common.utils import TestUtil
from apps.accounts.models import Otp
from unittest import mock
from datetime import timedelta
from django.utils import timezone


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
    logout_url = "/api/v1/auth/token/revoke/"

    send_email_url = "/api/v1/auth/otp/"
    verify_email_url = "/api/v1/auth/otp/verify/"

    password_change_url = "/api/v1/auth/password-change/"
    password_reset_request_url = "/api/v1/auth/password-reset/otp/"
    password_reset_verify_otp_url = "/api/v1/auth/password-reset/otp/verify/"
    password_reset_done_url = "/api/v1/auth/password-reset/done/"

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

    def test_send_verification_email(self):
        new_user = self.new_user
        mock.patch("apps.accounts.emails.SendEmail", new="")

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
        )  # Or use verified user variable
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Email address already verified!"},
        )

        # Clear OTP After Verification
        otp_cleared = not Otp.objects.filter(user_id=new_user.id).exists()
        self.assertTrue(otp_cleared, "OTP should be cleared after verification.")

    def test_logout(self):
        # Successful Logout
        # Log in the user and get the refresh token
        verified_user = self.verified_user
        login_response = self.client.post(
            self.login_url,
            {
                "email": verified_user.email,
                "password": "testpassword",
            },  # Ensure password matches
        )

        # Check login response and extract access token
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json().get("access")
        self.assertIsNotNone(access_token, "Access token should be provided upon login")

        # Successful Logout using the access token
        bearer_headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}
        response = self.client.post(self.logout_url, **bearer_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Logout successful."},
        )

        # Invalid or Missing Refresh Token
        self.bearer = {"HTTP_AUTHORIZATION": f"invalid_token"}
        response = self.client.get(self.logout_url, **self.bearer)
        self.assertEqual(response.status_code, 401)

    def test_password_change(self):
        verified_user = self.verified_user

        # Unauthenticated trying to change password
        response = self.client.post(
            self.password_change_url,
            {"old_password": verified_user.password, "new_password": "testimony74"},
        )
        self.assertEqual(response.status_code, 401)

        # Valid Password Change
        # login the user
        login_response = self.client.post(
            self.login_url,
            {"email": verified_user.email, "password": "testpassword"},
        )

        access_token = login_response.json().get("access")
        bearer_headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}
        response = self.client.post(
            self.password_change_url,
            {"old_password": "testpassword", "new_password": "testimony74"},
            **bearer_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Password changed successfully."},
        )

        # Incorrect Current Password
        response = self.client.post(
            self.password_change_url,
            {"old_password": "testpass", "new_password": "testimony74"},
            **bearer_headers,
        )

        self.assertEqual(response.status_code, 400)

        # Weak New Password
        response = self.client.post(
            self.password_change_url,
            {"old_password": "testpassword", "new_password": "test"},
            **bearer_headers,
        )

        self.assertEqual(response.status_code, 400)

    def test_password_reset_request(self):
        verified_user = self.verified_user
        mock.patch("apps.accounts.emails.SendEmail", new="")

        # Send OTP to Registered Email
        response = self.client.post(
            self.password_reset_request_url, {"email": verified_user.email}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "OTP sent successfully."},
        )

        # Non-existent Email
        response = self.client.post(
            self.password_reset_request_url, {"email": "tom@gmail.com"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"error": "User with this email does not exist."},
        )

    def test_verify_otp(self):
        verified_user = self.verified_user
        otp = "123456"
        otp_obj = Otp.objects.create(user=verified_user, otp=otp)

        # user does not exist
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": "nonexistentuser@example.com", "otp": int(otp)},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(), {"error": "No account is associated with this email."}
        )

        # Otp does not exist
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": int("123457")},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "error": "The OTP could not be found. Please enter a valid OTP or request a new one."
            },
        )

        # otp is expired
        otp_obj.created_at = timezone.now() - timedelta(hours=2)
        otp_obj.save()
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": int(otp)},
        )
        self.assertEqual(response.status_code, 410)
        self.assertEqual(
            response.json(), {"error": "OTP has expired. Please request a new one."}
        )

        # otp exists
        otp_obj.created_at = timezone.now()  # Resetting OTP's timestamp to be valid
        otp_obj.save()
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": int(otp)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "OTP verified, proceed to set new password."}
        )

        # otp is a letter or less than min or greater than min value
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": "abc123"},
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": int("123456789")},
        )
        self.assertEqual(response.status_code, 400)

        # otp is cleared after verification
        otp_cleared = not Otp.objects.filter(user_id=verified_user.id).exists()
        self.assertTrue(otp_cleared, "OTP should be cleared after password reset.")

    def test_password_reset_done(self):
        verified_user = self.verified_user

        # user does not exist
        response = self.client.post(
            self.password_reset_done_url,
            {"email": "nonexistentuser@example.com", "new_password": "newPassword123"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(), {"error": "No account is associated with this email."}
        )

        # Successful Password Reset
        response = self.client.post(
            self.password_reset_done_url,
            {
                "email": verified_user.email,
                "new_password": "newPassword123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Your password has been reset, proceed to login."},
        )

        # Weak New Password
        response = self.client.post(
            self.password_reset_done_url, {"email": verified_user.email, "new_password": "weak"}
        )
        self.assertEqual(response.status_code, 400)


# python manage.py test apps.accounts.tests.TestAccounts.test_register
