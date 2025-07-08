from apps.accounts.models import User
from apps.profiles.models import Profile, Skill
from apps.projects.models import Project, Review, Tag


class TestUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "email": "test@example.com",
            "password": "Testpassword2008@",
        }
        user = User.objects.create_user(**user_dict)
        return user

    def verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Verified",
            "email": "testverifieduser@example.com",
            "is_email_verified": True,
            "password": "Verified2001#",
        }
        user = User.objects.create_user(**user_dict)
        return user

    def other_verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Otherisgood*5%",
            "email": "testotheruser@example.com",
            "is_email_verified": True,
            "password": "testpassword",
        }
        user = User.objects.create_user(**user_dict)
        return user

    def create_project(owner):
        project_dict = {
            "title": "Test project",
            "owner": owner,
            "description": "A test project",
        }
        project = Project.objects.create(**project_dict)
        return project
    
    def create_tag():
        tag_dict = {
            "name": "fastapi"
        }
        tag = Tag.objects.create(**tag_dict)
        return tag

    def create_review(project, reviewer):
        review_dict = {
            "project": project,
            "reviewer": reviewer,
            "value": "up",
            "content": "Good project",
        }
        return Review.objects.create(**review_dict)

    @staticmethod
    def delete_all_profiles():
        try:
            User.objects.all().delete()
        except Exception as e:
            print(f"Unexpected error occurred while deleting profiles: {e}")

    @staticmethod
    def delete_all_projects():
        try:
            Project.objects.all().delete()
        except Exception as e:
            print(f"Unexpected error occurred while deleting projects: {e}")

    def get_profile(user):
        return Profile.objects.get(user=user)

    def add_skill(name, profile):
        return Skill.objects.create(name=name, user=profile)
