from rest_framework.test import APITestCase
from apps.common.utils import TestUtil
from unittest import mock

class TestProfile(APITestCase):
    login_url = "/api/v1/auth/token/"
    profile_list_url = "/api/v1/profiles/"
    my_profile_url = "/api/v1/profiles/account/"
    profile_detail_url = "/api/v1/profiles/<str:username>/"
    skill_create_url = "/api/v1/profiles/skill/add/"
    skill_detail_url = "/api/v1/profiles/skill/<str:id>/"

    
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
        
    def test_my_profile_get(self):
        # Authenticated User
        # Unauthenticated User
        pass
    
    def test_my_profile_patch(self):
        # Authenticated User
        # Unauthenticated User
        # Invalid Data - 400 Bad Request
        pass
    
    def test_profile_list_get(self):
        # Test that both authenticated and unauthenticated users can retrieve a list of profiles.
        # Test that the project list contains the correct information (e.g., owner, tags).
        # Test for empty project list.
        # Test for any errors in fetching data (e.g., database issues).
        # sucess
        pass
    
    def test_profile_detail_get(self):
        # Non-Existent Profile
        # Successful retrieval
        pass
    
    def test_skill_create_post(self):
        # Authenticated User
        # Unauthenticated User
        # Invalid Data - 400 Bad Request
        pass
    
    def test_skill_detail_get(self):
        # Authenticated User
        # Non-Existent Skill
        # Unauthenticated User
        pass
    
    def test_skill_detail_put(self):
        # Authenticated User
        # Non-Existent Skill
        # Unauthenticated User
        # Invalid Data - 400 Bad Request
        pass
    
    def test_skill_detail_delete(self):
        # Authenticated User
        # Non-Existent Skill
        # Unauthenticated User
        pass
        
