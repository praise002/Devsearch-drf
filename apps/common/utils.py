from apps.accounts.models import User
from apps.accounts.auth import Authentication

class TestUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "username": "test-name",
            "email": "test@example.com",
            "password": "testpassword",
        }
        user = User.objects.create_user(**user_dict)
        return user
    
    def verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Verified",
            "username": "test-verified",
            "email": "testverifieduser@example.com",
            "is_email_verified": True,
            "password": "testpassword",
        }
        user = User.objects.create_user(**user_dict)
        return user
    
    def other_verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Other",
            "username": "test-other",
            "email": "testotheruser@example.com",
            "is_email_verified": True,
            "password": "testpassword",
        }
        user = User.objects.create_user(**user_dict)
        return user
    
    def auth_token(verified_user):
        verified_user.access = Authentication.create_access_token(
            {"user_id": str(verified_user.id), "username": verified_user.username}
        )
        verified_user.refresh = Authentication.create_refresh_token()
        verified_user.save()
        return verified_user.access