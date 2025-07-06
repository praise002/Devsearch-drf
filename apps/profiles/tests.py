from rest_framework.test import APITestCase

from apps.common.utils import TestUtil
from apps.profiles.models import Profile


class TestProfiles(APITestCase):
    login_url = "/api/v1/auth/token/"
    profile_list_url = "/api/v1/profiles/"
    profile_url = "/api/v1/profiles/<str:username>/"
    skill_create_url = "/api/v1/profiles/skill/"
    skill_detail_url = "/api/v1/profiles/skill/<uuid:id>/"

    def setUp(self):
        # user
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)

    def test_profile_detail_get(self):
        username = self.profile1.user.username

        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.profile_url.replace("<str:username>", username))
        self.assertEqual(response.status_code, 200)

        # Unauthenticated User
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url.replace("<str:username>", username))
        self.assertEqual(response.status_code, 200)

    def test_profile_patch(self):
        username = self.profile1.user.username

        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            self.profile_url.replace("<str:username>", username),
            {"bio": "Updated bio"},
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["data"]["bio"], "Updated bio")

        # 403
        response = self.client.patch(
            self.profile_url.replace("<str:username>", self.profile2.user.username),
            {"bio": "Updated bio"},
        )

        self.assertEqual(response.status_code, 403)

        # Unauthenticated User
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            self.profile_url.replace("<str:username>", username),
            {"bio": "Updated bio"},
        )
        self.assertEqual(response.status_code, 401)

    def test_profile_list_get(self):
        # Test for successful retrieval
        response = self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code, 200)

        # Test for empty project list.
        TestUtil.delete_all_profiles()
        response = self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_skill_create_post(self):
        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.skill_create_url,
            {"name": "Python"},
        )

        self.assertEqual(response.status_code, 201)

        # Invalid Data - 400 Bad Request
        response = self.client.post(
            self.skill_create_url,
            {"name": ""},
        )
        self.assertEqual(response.status_code, 422)

        # Unauthenticated User
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.skill_create_url,
            {"name": "Python"},
        )
        self.assertEqual(response.status_code, 401)

    def test_skill_detail_get(self):
        skill = TestUtil.add_skill("Django", self.profile1)
        skill_id = skill.id

        other_skill = TestUtil.add_skill("FASTAPI", self.profile2)
        other_skill_id = other_skill.id

        # Unauthenticated User
        response = self.client.get(
            self.skill_detail_url.replace("<uuid:id>", str(skill_id))
        )

        self.assertEqual(response.status_code, 401)

        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            self.skill_detail_url.replace("<uuid:id>", str(skill_id))
        )

        self.assertEqual(response.status_code, 200)

        # Non-Existent Skill
        response = self.client.get(
            self.skill_detail_url.replace(
                "<uuid:id>", "b88b7979-bb72-451d-b5ec-f9dca693a962"
            ),
        )

        self.assertEqual(response.status_code, 404)

        # Invalid skill id
        response = self.client.get(self.skill_detail_url.replace("<uuid:id>", "9999"))

        self.assertEqual(response.status_code, 404)

        # Update someone else skill error - 404
        response = self.client.get(
            self.skill_detail_url.replace("<uuid:id>", str(other_skill_id)),
            {"name": "Django Updated"},
        )

        self.assertEqual(response.status_code, 403)

    def test_skill_patch(self):
        skill = TestUtil.add_skill("Django", self.profile1)
        skill_id = skill.id

        other_skill = TestUtil.add_skill("FASTAPI", self.profile2)
        other_skill_id = other_skill.id

        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            self.skill_detail_url.replace("<uuid:id>", str(skill_id)),
            {"name": "Django Updated"},
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["data"].get("name"), "Django Updated")

        # Non-Existent Skill
        response = self.client.patch(
            self.skill_detail_url.replace(
                "<uuid:id>", "3d628b38-e176-4560-987b-db412a05ff32"
            ),
            {"name": "Skill Updated"},
        )
        self.assertEqual(response.status_code, 404)

        # Get someone else skill error - 403
        response = self.client.patch(
            self.skill_detail_url.replace("<uuid:id>", str(other_skill_id)),
            {"name": "Django Updated"},
        )
        self.assertEqual(response.status_code, 403)

        # Unauthenticated User
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            self.skill_detail_url.replace("<uuid:id>", str(skill_id)),
            {"name": "Django Updated"},
        )
        self.assertEqual(response.status_code, 401)

    def test_skill_delete(self):
        skill = TestUtil.add_skill("Django", self.profile1)
        skill_id = skill.id

        other_skill = TestUtil.add_skill("FASTAPI", self.profile2)
        other_skill_id = other_skill.id

        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(
            self.skill_detail_url.replace("<uuid:id>", str(skill_id)),
        )
        self.assertEqual(response.status_code, 204)

        # Non-Existent Skill
        response = self.client.delete(
            self.skill_detail_url.replace(
                "<uuid:id>", "3d628b38-e176-4560-987b-db412a05ff32"
            ),
        )
        self.assertEqual(response.status_code, 404)

        # Delete someone else skill error - 403
        response = self.client.delete(
            self.skill_detail_url.replace("<uuid:id>", str(other_skill_id)),
            {"name": "Django Updated"},
        )
        self.assertEqual(response.status_code, 403)

        # Unauthenticated User
        self.client.force_authenticate(user=None)
        response = self.client.delete(
            self.skill_detail_url.replace("<uuid:id>", str(skill_id)),
            {"name": "Django Updated"},
        )
        self.assertEqual(response.status_code, 401)
