from rest_framework.test import APITestCase

from apps.common.utils import TestUtil
from apps.profiles.models import Profile


class TestProfiles(APITestCase):

    profile_list_url = "/api/v1/profiles/"
    profile_url = "/api/v1/profiles/<str:username>/"
    skill_create_list_url = "/api/v1/profiles/skills/"
    skill_u_d_url = "/api/v1/profiles/skills/<uuid:id>/"

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

    def test_skill_post(self):
        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.skill_create_list_url,
            {"name": "Python"},
        )

        self.assertEqual(response.status_code, 201)

        # Invalid Data
        response = self.client.post(
            self.skill_create_list_url,
            {"name": ""},
        )
        self.assertEqual(response.status_code, 422)

        # Unauthenticated User
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.skill_create_list_url,
            {"name": "Python"},
        )
        self.assertEqual(response.status_code, 401)

    def test_skill_patch(self):
        skill = TestUtil.add_skill(
            "Django",
            "Expert in Python development with Django and Flask frameworks",
            self.profile1,
        )

        skill_id = skill.id

        other_skill = TestUtil.add_skill(
            "FASTAPI",
            "Expert in Python development with FASTAPI",
            self.profile2,
        )
        other_skill_id = other_skill.id

        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            self.skill_u_d_url.replace("<uuid:id>", str(skill_id)),
            {"description": "Django Updated"},
        )

        print(response.json())
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["data"].get("description"), "Django Updated")

        # Non-Existent Skill
        response = self.client.patch(
            self.skill_u_d_url.replace(
                "<uuid:id>", "3d628b38-e176-4560-987b-db412a05ff32"
            ),
            {"description": "Skill Updated"},
        )
        self.assertEqual(response.status_code, 404)

        #  403
        response = self.client.patch(
            self.skill_u_d_url.replace("<uuid:id>", str(other_skill_id)),
            {"description": "Django Updated"},
        )
        self.assertEqual(response.status_code, 403)

        # Unauthenticated User
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            self.skill_u_d_url.replace("<uuid:id>", str(skill_id)),
            {"description": "Django Updated"},
        )
        self.assertEqual(response.status_code, 401)

    def test_skill_delete(self):
        skill = TestUtil.add_skill(
            "Django",
            "Expert in Python development with Django framework",
            self.profile1,
        )
        skill_id = skill.id

        other_skill = TestUtil.add_skill(
            "FASTAPI",
            "Expert in Python development with FASTAPI",
            self.profile2,
        )
        other_skill_id = other_skill.id

        # Authenticated User
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(
            self.skill_u_d_url.replace("<uuid:id>", str(skill_id)),
        )
        self.assertEqual(response.status_code, 204)

        # Non-Existent Skill
        response = self.client.delete(
            self.skill_u_d_url.replace(
                "<uuid:id>", "3d628b38-e176-4560-987b-db412a05ff32"
            ),
        )
        self.assertEqual(response.status_code, 404)

        # Delete someone else skill error - 403
        response = self.client.delete(
            self.skill_u_d_url.replace("<uuid:id>", str(other_skill_id))
        )
        self.assertEqual(response.status_code, 403)

        # Unauthenticated User
        self.client.force_authenticate(user=None)
        response = self.client.delete(
            self.skill_u_d_url.replace("<uuid:id>", str(skill_id))
        )
        self.assertEqual(response.status_code, 401)


# python manage.py test apps.profiles.tests.TestProfiles.test_skill_create_post
