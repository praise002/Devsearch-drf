from rest_framework.test import APITestCase
from apps.common.utils import TestUtil
from unittest import mock

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
        
    def test_project_list_get(self):
        # Test that both authenticated and unauthenticated users can retrieve a list of projects.
        # Test that the project list contains the correct information (e.g., owner, tags).
        # Test for empty project list.
        # Test for any errors in fetching data (e.g., database issues).
        pass
    
    def test_project_detail_get(self):
        # Test that both authenticated and unauthenticated users can view project details.
        # Test that a project is retrieved correctly by its slug.
        # Test that the correct project details are returned (e.g., owner, tags).
        # Test that a 404 Not Found is returned for a non-existent project.
        pass
    
    def test_related_projects_get(self):
        # Test that both authenticated and unauthenticated users can view related projects.
        # Test for cases when there are no related projects.
        # est that a 404 Not Found error is returned if the project does not exist.
        pass
    
    def test_project_create_post(self):
        # Test that only authenticated users can create a new project.
        # Test the creation of a project with valid data.
        # Test the creation of a project with invalid data (e.g., missing required fields).
        # Test that the owner is correctly assigned to the created project.
        pass
    
    def test_project_edit_delete_patch(self):
        # Test that only the project owner can edit a project.
        # Test that a project can be edited successfully.
        # Test that a 404 Not Found error is returned when editing a nonexistent project.
        pass
    
    def test_project_edit_delete_del(self):
        # Test that only the project owner can delete a project.
        # Test that a project is successfully deleted.
        pass
    
    def test_tag_create_post(self):
        # Test that only authenticated users can create tags.
        # Test the creation of a new tag.
        # Test that an error is returned when the tag name is missing or invalid.
        # Test that the tag is correctly associated with the project.
        pass
    
    def test_tag_remove(self):
        # Test that only authenticated users can remove tags from a project.
        # Test the removal of a tag from a project successfully.
        # Test that a 404 Not Found error is returned when the project or tag does not exist.
        # Test that a 400 Bad Request is returned when trying to remove a tag not associated with the project.
        pass
    
    def test_review_create_post(self):
        # Test that only authenticated users can submit a review.
        # Test that users cannot review their own projects.
        # Test that users can only submit one review per project.
        # Test that a review is created successfully when valid data is provided.
        # Test that a 404 Not Found error is returned for a nonexistent project.
        pass
    
    def test_review_list_get(self):
        # Test that users can retrieve reviews for a project.
        # Test that the correct reviews are returned based on the project slug.
        # Test that a 404 Not Found error is returned for a nonexistent project.
        pass