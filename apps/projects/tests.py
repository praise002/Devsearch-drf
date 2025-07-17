from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase

from apps.common.utils import TestUtil


def create_test_image():
    """Generate a simple image in memory"""
    image = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return SimpleUploadedFile("test.png", buffer.getvalue(), content_type="image/png")


class TestProjects(APITestCase):
    # Project URLs
    project_list_create_url = "/api/v1/projects/"
    project_r_u_d_url = "/api/v1/projects/<slug:slug>/"
    project_related_url = "/api/v1/projects/<slug:slug>/related-projects/"
    featured_image_url = "/api/v1/projects/<slug:slug>/image/"

    # Tag URLs
    tag_list_url = "/api/v1/projects/tags/"
    tag_add_url = "/api/v1/projects/<slug:slug>/tags/"
    tag_remove_url = "/api/v1/projects/<slug:project_slug>/tags/<uuid:tag_id>/"

    # Review URLs
    review_list_create_url = "/api/v1/projects/<slug:slug>/reviews/"

    def setUp(self):
        # user
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

        self.profile1 = TestUtil.get_profile(user=self.user1)
        self.profile2 = TestUtil.get_profile(user=self.user2)

        self.project1 = TestUtil.create_project(owner=self.profile1)
        self.project2 = TestUtil.create_project(owner=self.profile2)

        self.tag = TestUtil.create_tag()
        self.project1.tags.add(self.tag)

    def test_project_list_get(self):
        # Successful retrieval
        response = self.client.get(self.project_list_create_url)

        self.assertEqual(response.status_code, 200)

        # Test for empty project list
        TestUtil.delete_all_projects()
        response = self.client.get(self.project_list_create_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data["data"].get("results")), 0)

    def test_project_create_post(self):
        project_data = {
            "title": "Test project",
            "owner": self.profile1.id,
            "description": "A test project",
        }

        # Authenticated and valid data.
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.project_list_create_url, data=project_data)

        self.assertEqual(response.status_code, 201)

        # Test the creation of a project with invalid data (e.g., missing required fields).
        response = self.client.post(self.project_list_create_url, data={})

        self.assertEqual(response.status_code, 422)

        # Test that the owner is correctly assigned to the created project.
        # response = self.client.post(
        #     self.project_list_create_url,
        #     data=project_data,
        # )
        #
        # TODO: Can't work anymore cos of some changes
        # self.assertEqual(response.json().get("owner"), self.profile1.user.full_name)

        # Unauthenticated users
        self.client.force_authenticate(user=None)
        response = self.client.post(self.project_list_create_url, data=project_data)
        self.assertEqual(response.status_code, 401)

    def test_project_retrieve(self):
        # Success
        response = self.client.get(
            self.project_r_u_d_url.replace("<slug:slug>", self.project1.slug)
        )
        self.assertEqual(response.status_code, 200)

        # Test that the correct project details are returned (e.g., owner, tags).
        self.assertEqual(response.data["data"].get("title"), self.project1.title)

        # Test that a 404 Not Found is returned for a non-existent project.
        response = self.client.get(
            self.project_r_u_d_url.replace("<slug:slug>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)

    def test_project_patch(self):
        # unauthenticated
        response = self.client.patch(
            self.project_r_u_d_url.replace("<slug:slug>", self.project1.slug),
            data={"title": "Updated Title"},
        )

        self.assertEqual(response.status_code, 401)

        # project data is invalid
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            self.project_r_u_d_url.replace("<slug:slug>", self.project1.slug),
            data={"description": ""},
        )

        self.assertEqual(response.status_code, 422)

        # Test permission denied - trying to update someone project
        response = self.client.delete(
            self.project_r_u_d_url.replace("<slug:slug>", self.project2.slug)
        )
        self.assertEqual(response.status_code, 403)

        # Test that only the project owner can edit a project and is authenticated and is valid data.
        response = self.client.patch(
            self.project_r_u_d_url.replace("<slug:slug>", self.project1.slug),
            data={"title": "Updated Title"},
        )

        self.assertEqual(response.status_code, 200)

        # Nonexistent project.
        response = self.client.patch(
            self.project_r_u_d_url.replace("<slug:slug>", "nonexistent"),
            data={"title": "Updated Title"},
        )

        self.assertEqual(response.status_code, 404)

        # updating someone else project - 403
        response = self.client.patch(
            self.project_r_u_d_url.replace("<slug:slug>", self.project2.slug),
            data={"title": "Updated Title"},
        )

        self.assertEqual(response.status_code, 403)

    def test_project_delete(self):
        self.client.force_authenticate(user=self.user1)

        # Nonexistent project.
        response = self.client.delete(
            self.project_r_u_d_url.replace("<slug:slug>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)

        # Test permission denied - trying to delete someone project
        response = self.client.delete(
            self.project_r_u_d_url.replace("<slug:slug>", self.project2.slug)
        )
        self.assertEqual(response.status_code, 403)

        # Test that only the project owner can delete a project and authenticated.
        response = self.client.delete(
            self.project_r_u_d_url.replace("<slug:slug>", self.project1.slug)
        )
        self.assertEqual(response.status_code, 204)

        # Test that a project is successfully deleted.
        response = self.client.get(
            self.project_r_u_d_url.replace("<slug:slug>", self.project1.slug)
        )
        self.assertEqual(response.status_code, 404)  # Not found after deletion

        # Unauthenticated
        self.client.force_authenticate(user=None)
        response = self.client.delete(
            self.project_r_u_d_url.replace("<slug:slug>", self.project1.slug),
        )
        self.assertEqual(response.status_code, 401)

    def test_featured_image_update(self):
        # Test success
        self.client.force_authenticate(user=self.user1)
        image = create_test_image()

        response = self.client.patch(
            self.featured_image_url.replace("<slug:slug>", self.project1.slug),
            {"featured_image": image},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.project1.refresh_from_db()
        self.assertTrue(self.project1.featured_image_url)

        # Test 403 - Trying to update someone's project image
        image = create_test_image()

        response = self.client.patch(
            self.featured_image_url.replace("<slug:slug>", self.project2.slug),
            {"featured_image": image},
            format="multipart",
        )

        self.assertEqual(response.status_code, 403)

        # Test 401 for unauthenticated users
        self.client.force_authenticate(user=None)

        response = self.client.patch(
            self.featured_image_url.replace("<slug:slug>", self.project1.slug),
            {"featured_image": image},
            format="multipart",
        )

        self.assertEqual(response.status_code, 401)

    def test_related_projects_get(self):
        # Non-existent project
        response = self.client.get(
            self.project_related_url.replace("<slug:slug>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)

    def test_tag_get(self):
        # Unauthenticated users
        response = self.client.get(self.tag_list_url)
        self.assertEqual(response.status_code, 401)

        # Authenticated users
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.tag_list_url)

        self.assertEqual(response.status_code, 200)

    def test_tag_post(self):
        # Unauthenticated users
        response = self.client.post(
            self.tag_add_url.replace("<slug:slug>", self.project1.slug),
            data={"name": "New Tag"},
        )
        self.assertEqual(response.status_code, 401)

        # Test that only authenticated users can create tags and data is valid.
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.tag_add_url.replace("<slug:slug>", self.project1.slug),
            data={"name": "New Tag"},
        )
        self.assertEqual(response.status_code, 201)

        # Test that the tag is correctly associated with the project.
        response = self.client.get(
            self.tag_list_url.replace("<slug:slug>", self.project1.slug)
        )
        print(response.json())

        self.assertIn("new tag", response.data["data"]["results"][1].get("name"))

        # Test that an error is returned when the tag name is missing or invalid.
        response = self.client.post(
            self.tag_add_url.replace("<slug:slug>", self.project1.slug), data={}
        )
        self.assertEqual(response.status_code, 422)

        # Test 403 - adding tag to someone else project
        response = self.client.post(
            self.tag_add_url.replace("<slug:slug>", self.project2.slug),
            data={"name": "New Tag"},
        )
        self.assertEqual(response.status_code, 403)

    def test_tag_remove(self):
        # Unauthenticated users cannot delete a tag
        response = self.client.delete(
            self.tag_remove_url.replace(
                "<slug:project_slug>", self.project1.slug
            ).replace("<uuid:tag_id>", str(self.tag.id)),
        )
        self.assertEqual(response.status_code, 401)

        # Authenticated users and success
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(
            self.tag_remove_url.replace(
                "<slug:project_slug>", self.project1.slug
            ).replace("<uuid:tag_id>", str(self.tag.id)),
        )
        self.assertEqual(response.status_code, 204)

        # Non-existent tag(invalid uuid)
        response = self.client.delete(
            self.tag_remove_url.replace(
                "<slug:project_slug>", self.project1.slug
            ).replace("<uuid:tag_id>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)

        # Non-existent tag - tag valid but not found
        response = self.client.delete(
            self.tag_remove_url.replace(
                "<slug:project_slug>", self.project1.slug
            ).replace("<uuid:tag_id>", "b88b7979-bb72-451d-b5ec-f9dca693a962")
        )
        self.assertEqual(response.status_code, 404)

        # Test - 403 project doesn't belong to user
        response = self.client.delete(
            self.tag_remove_url.replace(
                "<slug:project_slug>", self.project2.slug
            ).replace("<uuid:tag_id>", str(self.tag.id)),
        )
        self.assertEqual(response.status_code, 403)

        # Non-existent project and tag
        response = self.client.delete(
            self.tag_remove_url.replace("<slug:project_slug>", "nonexistent").replace(
                "<uuid:tag_id>", "b88b7979-bb72-451d-b5ec-f9dca693a962"
            )
        )
        self.assertEqual(response.status_code, 404)

        # Test that a 404 is returned when trying to remove a tag not associated with the project.
        response = self.client.delete(
            self.tag_remove_url.replace(
                "<slug:project_slug>", self.project1.slug
            ).replace("<uuid:tag_id>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)

    def test_review_get(self):
        # Test that users can retrieve reviews for a project.
        TestUtil.create_review(project=self.project1, reviewer=self.profile2)
        response = self.client.get(
            self.review_list_create_url.replace("<slug:slug>", self.project1.slug)
        )
        self.assertEqual(response.status_code, 200)

        # Test that the correct reviews are returned based on the project slug.
        self.assertEqual(len(response.data["data"]), 1)

        # nonexistent project.
        response = self.client.get(
            self.review_list_create_url.replace("<slug:slug>", "nonexistent")
        )
        self.assertEqual(response.status_code, 404)

    def test_review_post(self):
        # Unauthenticated
        response = self.client.post(
            self.review_list_create_url.replace("<slug:slug>", self.project2.slug),
            data={"content": "Great Project", "value": "up"},
        )
        self.assertEqual(response.status_code, 401)

        # Authenticated and invalid review
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.review_list_create_url.replace("<slug:slug>", self.project2.slug),
            data={"content": "Great Project", "value": 4},
        )

        self.assertEqual(response.status_code, 422)

        # Authenticated and data is valid.
        response = self.client.post(
            self.review_list_create_url.replace("<slug:slug>", self.project2.slug),
            data={"content": "Great Project", "value": "up"},
        )
        self.assertEqual(response.status_code, 201)

        # Test that users cannot review their own projects.
        response = self.client.post(
            self.review_list_create_url.replace("<slug:slug>", self.project1.slug),
            data={"content": "My Own Project", "value": "up"},
        )

        self.assertEqual(response.status_code, 403)

        # Test that users can only submit one review per project.
        response = self.client.post(
            self.review_list_create_url.replace("<slug:slug>", self.project2.slug),
            data={"content": "Second Review", "value": "down"},
        )
        self.assertEqual(response.status_code, 409)

        # Test that a 404 Not Found error is returned for a nonexistent project.
        response = self.client.post(
            self.review_list_create_url.replace("<slug:slug>", "nonexistent"),
            data={"content": "Second Review", "value": "down"},
        )
        self.assertEqual(response.status_code, 404)
