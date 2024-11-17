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

    def test_my_profile_get(self):
        # Authenticated User
        response = self.client.get(self.my_profile_url, **self.bearer)
        self.assertEqual(response.status_code, 200)

        # Unauthenticated User
        response = self.client.get(self.my_profile_url)
        self.assertEqual(response.status_code, 401)

    def test_my_profile_patch(self):
        # Authenticated User
        response = self.client.patch(
            self.my_profile_url,
            {"bio": "Updated bio"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("bio"), "Updated bio")

        # Unauthenticated User
        response = self.client.patch(
            self.my_profile_url,
            {"bio": "Updated bio"},
        )
        self.assertEqual(response.status_code, 401)

        # Invalid Data - 400 Bad Request
        response = self.client.patch(
            self.my_profile_url,
            {"photo": "5"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 400)

    def test_profile_list_get(self):
        # Test for successful retrieval
        response = self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code, 200)

        # Test for empty project list.
        TestUtil.delete_all_profiles()
        response = self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_profile_detail_get(self):
        # Successful retrieval
        response = self.client.get(
            self.profile_detail_url.replace(
                "<str:username>", self.verified_user.username
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().get("user").get("username"), self.verified_user.username
        )

        # Non-Existent Profile
        response = self.client.get(
            self.profile_detail_url.replace("<str:username>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)


    def test_skill_create_post(self):
        # Authenticated User
        response = self.client.post(
            self.skill_create_url,
            {"name": "Python"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 201)

        # Unauthenticated User
        response = self.client.post(
            self.skill_create_url,
            {"name": "Python"},
        )
        self.assertEqual(response.status_code, 401)

        # Invalid Data - 400 Bad Request
        response = self.client.post(
            self.skill_create_url,
            {"name": ""},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 400)

    def test_skill_detail_get(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        skill = TestUtil.add_skill("Django", profile)
        skill_id = skill.id
        
        other_profile = TestUtil.get_profile(user=self.other_verified_user)
        other_skill = TestUtil.add_skill("FASTAPI", other_profile)
        other_skill_id = other_skill.id 

        # Authenticated User
        response = self.client.get(
            self.skill_detail_url.replace("<str:id>", str(skill_id)), **self.bearer
        )
        self.assertEqual(response.status_code, 200)

        # Non-Existent Skill
        response = self.client.get(
            self.skill_detail_url.replace(
                "<str:id>", "b88b7979-bb72-451d-b5ec-f9dca693a962"
            ),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

        # Invalid skill id
        response = self.client.get(
            self.skill_detail_url.replace("<str:id>", "9999"), **self.bearer
        )
        self.assertEqual(response.status_code, 404)

        # Unauthenticated User
        response = self.client.get(
            self.skill_detail_url.replace("<str:id>", str(skill_id))
        )
        self.assertEqual(response.status_code, 401)
        
         # Update someone else skill error - 404
        response = self.client.get(
            self.skill_detail_url.replace("<str:id>", str(other_skill_id)),
            {"name": "Django Updated"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

    def test_skill_detail_put(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        skill = TestUtil.add_skill("Django", profile)
        skill_id = skill.id
        
        other_profile = TestUtil.get_profile(user=self.other_verified_user)
        other_skill = TestUtil.add_skill("FASTAPI", other_profile)
        other_skill_id = other_skill.id 

        # Authenticated User
        response = self.client.put(
            self.skill_detail_url.replace("<str:id>", str(skill_id)),
            {"name": "Django Updated"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("name"), "Django Updated")

        # Non-Existent Skill
        response = self.client.put(
            self.skill_detail_url.replace(
                "<str:id>", "3d628b38-e176-4560-987b-db412a05ff32"
            ),
            {"name": "Skill Updated"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

        # Unauthenticated User
        response = self.client.put(
            self.skill_detail_url.replace("<str:id>", str(skill_id)),
            {"name": "Django Updated"},
        )
        self.assertEqual(response.status_code, 401)

        # Get someone else skill error - 404
        response = self.client.put(
            self.skill_detail_url.replace("<str:id>", str(other_skill_id)),
            {"name": "Django Updated"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

    def test_skill_detail_delete(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        skill = TestUtil.add_skill("Django", profile)
        skill_id = skill.id
        
        other_profile = TestUtil.get_profile(user=self.other_verified_user)
        other_skill = TestUtil.add_skill("FASTAPI", other_profile)
        other_skill_id = other_skill.id 

        # Authenticated User
        response = self.client.delete(
            self.skill_detail_url.replace("<str:id>", str(skill_id)),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 204)

        # Non-Existent Skill
        response = self.client.delete(
            self.skill_detail_url.replace(
                "<str:id>", "3d628b38-e176-4560-987b-db412a05ff32"
            ),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

        # Unauthenticated User
        response = self.client.delete(
            self.skill_detail_url.replace("<str:id>", str(skill_id)),
            {"name": "Django Updated"},
        )
        self.assertEqual(response.status_code, 401)
        
        # Delete someone else skill error - 404
        response = self.client.delete(
            self.skill_detail_url.replace("<str:id>", str(other_skill_id)),
            {"name": "Django Updated"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)
