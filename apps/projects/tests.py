from rest_framework.test import APITestCase
from apps.common.utils import TestUtil


class TestProjects(APITestCase):
    # Project URLs
    project_list_url = "/api/v1/projects/"
    project_create_url = "/api/v1/projects/add/"
    project_detail_url = "/api/v1/projects/<slug:slug>/"
    project_edit_delete_url = "/api/v1/projects/<slug:slug>/edit-delete/"
    project_related_url = "/api/v1/projects/<slug:slug>/related/"

    # Tag URLs
    tag_create_url = "/api/v1/projects/<slug:slug>/tag/add/"
    tag_remove_url = "/api/v1/projects/<slug:project_slug>/tag/<str:tag_id>/"

    # Review URLs
    review_create_url = "/api/v1/projects/<slug:slug>/review/add/"
    project_reviews_url = "/api/v1/projects/<slug:slug>/reviews/"

    # Login URL
    login_url = "/api/v1/auth/token/"

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

    def test_project_list_get(self):
        # Successful retrieval
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, 200)

        # Test for empty project list
        TestUtil.delete_all_projects()
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get("results")), 0)

    def test_project_detail_get(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        project = TestUtil.create_project(owner=profile)

        # Success
        response = self.client.get(
            self.project_detail_url.replace("<slug:slug>", project.slug)
        )
        self.assertEqual(response.status_code, 200)

        # Test that the correct project details are returned (e.g., owner, tags).
        self.assertEqual(response.json().get("title"), project.title)

        # Test that a 404 Not Found is returned for a non-existent project.
        response = self.client.get(
            self.project_detail_url.replace("<slug:slug>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)

    def test_related_projects_get(self):
        # Non-existent project
        response = self.client.get(
            self.project_related_url.replace("<slug:slug>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)

    def test_project_create_post(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        project_data = {
            "title": "Test project",
            "slug": "test-project",
            "owner": profile.id,
            "description": "A test project",
        }

        # Authenticated and valid data.
        response = self.client.post(
            self.project_create_url, data=project_data, **self.bearer
        )
        self.assertEqual(response.status_code, 201)

        # Test the creation of a project with invalid data (e.g., missing required fields).
        response = self.client.post(self.project_create_url, data={}, **self.bearer)
        self.assertEqual(response.status_code, 400)

        # Test that the owner is correctly assigned to the created project.
        response = self.client.post(
            self.project_create_url,
            data=project_data,
            **self.bearer,
        )
        self.assertEqual(response.json().get("owner"), profile.user.full_name)

        # Unauthenticated users
        response = self.client.post(self.project_create_url, data=project_data)
        self.assertEqual(response.status_code, 401)

    def test_project_edit_delete_patch(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        project = TestUtil.create_project(owner=profile)

        # project data is invalid
        response = self.client.patch(
            self.project_edit_delete_url.replace("<slug:slug>", project.slug),
            data={"featured_image": "Updated Image"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 400)

        # Test that only the project owner can edit a project and is authenticated and is valid data.
        response = self.client.patch(
            self.project_edit_delete_url.replace("<slug:slug>", project.slug),
            data={"title": "Updated Title"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 200)

        # Nonexistent project.
        response = self.client.patch(
            self.project_edit_delete_url.replace("<slug:slug>", "nonexistent"),
            data={"title": "Updated Title"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

    def test_project_edit_delete_del(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        project = TestUtil.create_project(owner=profile)

        # Nonexistent project.
        response = self.client.delete(
            self.project_edit_delete_url.replace("<slug:slug>", "nonexistent"),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

        # Unauthenticated
        response = self.client.delete(
            self.project_edit_delete_url.replace("<slug:slug>", project.slug),
        )
        self.assertEqual(response.status_code, 401)

        # Test that only the project owner can delete a project and authenticated.
        response = self.client.delete(
            self.project_edit_delete_url.replace("<slug:slug>", project.slug),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 204)  # No Content for successful delete

        # Test that a project is successfully deleted.
        response = self.client.get(
            self.project_detail_url.replace("<slug:slug>", project.slug)
        )
        self.assertEqual(response.status_code, 404)  # Not found after deletion

    def test_tag_create_post(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        project = TestUtil.create_project(owner=profile)

        # Unauthenticated users
        response = self.client.post(
            self.tag_create_url.replace("<slug:slug>", project.slug),
            data={"name": "New Tag"},
        )
        self.assertEqual(response.status_code, 401)

        # Test that only authenticated users can create tags and data is valid.
        response = self.client.post(
            self.tag_create_url.replace("<slug:slug>", project.slug),
            data={"name": "New Tag"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 201)

        # Test that an error is returned when the tag name is missing or invalid.
        response = self.client.post(
            self.tag_create_url.replace("<slug:slug>", project.slug),
            data={},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 400)

        # Test that the tag is correctly associated with the project.
        response = self.client.get(
            self.project_detail_url.replace("<slug:slug>", project.slug)
        )
        self.assertIn("new tag", response.json().get("tags")[0].get("name"))

    def test_tag_remove(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        project = TestUtil.create_project(owner=profile)

        # Unauthenticated users cannot delete a tag
        tag = project.tags.create(name="Old Tag")
        response = self.client.delete(
            self.tag_remove_url.replace("<slug:project_slug>", project.slug).replace(
                "<str:tag_id>", str(tag.id)
            ),
        )
        self.assertEqual(response.status_code, 401)

        # Authenticated users and success.
        tag = project.tags.create(name="Old Tag")
        response = self.client.delete(
            self.tag_remove_url.replace("<slug:project_slug>", project.slug).replace(
                "<str:tag_id>", str(tag.id)
            ),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 204)

        # Non-existent tag(invalid uuid)
        response = self.client.delete(
            self.tag_remove_url.replace("<slug:project_slug>", project.slug).replace(
                "<str:tag_id>", "nonexistent"
            ),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

        # Non-existent tag - tag valid but not found
        response = self.client.delete(
            self.tag_remove_url.replace("<slug:project_slug>", project.slug).replace(
                "<str:tag_id>", "b88b7979-bb72-451d-b5ec-f9dca693a962"
            ),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

        # Non-existent project and tag
        response = self.client.delete(
            self.tag_remove_url.replace("<slug:project_slug>", "nonexistent").replace(
                "<str:tag_id>", "b88b7979-bb72-451d-b5ec-f9dca693a962"
            ),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

        # Test that a 404 is returned when trying to remove a tag not associated with the project.
        response = self.client.delete(
            self.tag_remove_url.replace("<slug:project_slug>", project.slug).replace(
                "<str:tag_id>", "nonexistent"
            ),
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

    def test_review_create_post(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        project = TestUtil.create_project(owner=profile)

        other_profile = TestUtil.get_profile(user=self.other_verified_user)
        other_project = TestUtil.create_project(owner=other_profile)

        # Unauthenticated
        response = self.client.post(
            self.review_create_url.replace("<slug:slug>", project.slug),
            data={"content": "Great Project", "value": "up"},
        )
        self.assertEqual(response.status_code, 401)

        # Authenticated and invalid review
        response = self.client.post(
            self.review_create_url.replace("<slug:slug>", other_project.slug),
            data={"content": "Great Project", "value": 4},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 400)

        # Authenticated and data is valid.
        response = self.client.post(
            self.review_create_url.replace("<slug:slug>", other_project.slug),
            data={"content": "Great Project", "value": "up"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 201)

        # Test that users cannot review their own projects.
        response = self.client.post(
            self.review_create_url.replace("<slug:slug>", project.slug),
            data={"content": "My Own Project", "value": "up"},
            **self.bearer,
        )

        self.assertEqual(response.status_code, 403)

        # Test that users can only submit one review per project.
        response = self.client.post(
            self.review_create_url.replace("<slug:slug>", other_project.slug),
            data={"content": "Second Review", "value": "down"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 400)

        # Test that a 404 Not Found error is returned for a nonexistent project.
        response = self.client.post(
            self.review_create_url.replace("<slug:slug>", "nonexistent"),
            data={"content": "Second Review", "value": "down"},
            **self.bearer,
        )
        self.assertEqual(response.status_code, 404)

    def test_review_list_get(self):
        profile = TestUtil.get_profile(user=self.verified_user)
        project = TestUtil.create_project(owner=profile)

        other_profile = TestUtil.get_profile(user=self.other_verified_user)

        # Test that users can retrieve reviews for a project.
        TestUtil.create_review(project=project, reviewer=other_profile)
        response = self.client.get(
            self.project_reviews_url.replace("<slug:slug>", project.slug)
        )
        self.assertEqual(response.status_code, 200)

        # Test that the correct reviews are returned based on the project slug.
        self.assertEqual(len(response.json()), 1)

        # nonexistent project.
        response = self.client.get(
            self.project_reviews_url.replace("<slug:slug>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)
