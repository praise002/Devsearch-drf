import logging
import os
from pathlib import Path

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from apps.accounts.models import User
from apps.common.management.commands.data import (
    PROFILES_DATA,
    PROJECTS_DATA,
    REVIEWS_DATA,
    USERS_DATA,
)
from apps.profiles.models import AVATAR_FOLDER, Profile, Skill
from apps.projects.models import Project, Review, Tag

logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).resolve().parent

test_images_directory = os.path.join(CURRENT_DIR, "images")


class CreateData:
    def __init__(self):
        with transaction.atomic():
            self.create_superuser()
            self.create_user_groups()
            self.create_users()

        with transaction.atomic():
            self.update_profiles()
            self.create_projects()
            self.create_reviews()

    def get_image(self, images_list, substring):
        return [s for s in images_list if s.startswith(substring)]

    def create_superuser(self) -> User:
        user_dict = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": settings.SUPERUSER_EMAIL,
            "password": settings.SUPERUSER_PASSWORD,
            "is_email_verified": True,
        }
        superuser = User.objects.get_or_none(email=user_dict["email"])

        if not superuser:
            superuser = User.objects.create_superuser(**user_dict)

        return superuser

    def create_user_groups(self) -> Group:
        """Create user groups and assign permissions."""
        moderators, created = Group.objects.get_or_create(name="Moderators")
        if created:
            logger.info("Created 'Moderators' group")

        user_content_type = ContentType.objects.get_for_model(User)
        print(user_content_type)  # returns Accounts | user

        print(
            Permission.objects.filter(
                content_type=user_content_type,
                codename__in=[
                    "view_user",
                    "can_toggle_user_status",
                    "view_profile",
                    "view_project",
                    "view_review",
                    "delete_project",
                    "delete_review",
                ],
            )
        )

        print(
            *Permission.objects.filter(
                content_type=user_content_type,
                codename__in=[
                    "view_user",
                    "can_toggle_user_status",
                    "view_profile",
                    "view_project",
                    "view_review",
                    "delete_project",
                    "delete_review",
                ],
            )
        )

        moderators.permissions.add(
            *Permission.objects.filter(
                content_type=user_content_type,
                codename__in=[
                    "view_user",
                    "can_toggle_user_status",
                    "view_profile",
                    "view_project",
                    "view_review",
                    "delete_project",
                    "delete_review",
                ],
            )
        )

        user_dict = {
            "first_name": "Moderator",
            "last_name": "Manager",
            "email": settings.MODERATOR_EMAIL,
            "password": settings.MODERATOR_PASSWORD,
            "is_staff": True,
            "is_email_verified": True,
        }

        moderator_user = User.objects.get_or_none(email=user_dict["email"])

        if not moderator_user:
            moderator_user = User.objects.create_user(**user_dict)
            moderator_user.groups.add(moderators)
            logger.info(f"Created user 'Moderator' and added to 'Moderators' group")

    def create_users(self) -> User:
        """Creates users from USERS_DATA if they don't exist."""
        created_count = 0
        skipped_count = 0

        for user_data in USERS_DATA:
            if User.objects.filter(email=user_data["email"]).exists():
                logger.debug(f"User '{user_data['email']}' already exists. Skipping.")
                skipped_count += 1
                continue

            try:
                user = User.objects.create_user(**user_data)

                created_count += 1
                logger.debug(f"User Created: {user.first_name}")

            except Exception as e:
                logger.error(f"Error creating user '{user_data['email']}': {str(e)}")

        logger.info(
            f"Successfully created {created_count} users, skipped {skipped_count}."
        )

        return

    def get_images_path(self):
        images = os.listdir(test_images_directory)
        image_path_list = []

        image_file_name = self.get_image(images, "avatar")

        for file_name in image_file_name:
            image_path = os.path.join(test_images_directory, file_name)
            image_path_list.append(image_path)

        return image_path_list, image_file_name

    def update_profiles(self) -> Profile:
        """Updates profiles with data from PROFILES_DATA."""
        # Prefetch all users and profiles in one query
        user_emails = [user["email"] for user in USERS_DATA]
        users = User.objects.filter(email__in=user_emails).select_related("profile")
        user_map = {user.email: user for user in users}

        image_path_list, image_file_name = self.get_images_path()

        # Prepare profile updates
        profiles_to_update = []
        all_skills_data = []  # Stores (profile, skill_data) tuples

        for user_data, profile_data, image_path, file_name in zip(
            USERS_DATA, PROFILES_DATA, image_path_list, image_file_name
        ):
            user = user_map.get(user_data["email"])

            if not user:
                logger.warning(
                    f"User with email {user_data['email']} not found. Skipping."
                )
                continue

            profile = user.profile

            # Update profile fields
            for field in ["short_intro", "bio", "location"]:
                setattr(profile, field, profile_data.get(field, ""))

            # profile.short_intro = profile_data["short_intro"]
            # profile.bio = profile_data["bio"]
            # profile.location = profile_data["location"]

            # Update social links
            socials = profile_data.get("social", {})
            for field in ["github", "stackoverflow", "twitter", "linkedin", "website"]:
                setattr(profile, f"social_{field}", socials.get(field, ""))

            # profile.social_github = socials.get("github", "")
            # profile.social_stackoverflow = socials.get("stackoverflow", "")
            # profile.social_twitter = socials.get("twitter", "")
            # profile.social_linkedin = socials.get("linkedin", "")
            # profile.social_website = socials.get("website", "")

            # Update avatar
            if not profile.avatar:
                with open(image_path, "rb") as image_file:
                    file_storage = MediaCloudinaryStorage()
                    file_path = file_storage.save(
                        f"{AVATAR_FOLDER}{file_name}", image_file
                    )

                    profile.avatar = file_path

            profiles_to_update.append(profile)
            all_skills_data.append((profile, profile_data.get("skills", [])))

            print(f"Profile {profile}")

        # Bulk update profiles
        print(f"Profiles to update: {profiles_to_update}")
        if profiles_to_update:
            Profile.objects.bulk_update(
                profiles_to_update,
                fields=[
                    "short_intro",
                    "bio",
                    "location",
                    "avatar",
                    "social_github",
                    "social_stackoverflow",
                    "social_twitter",
                    "social_linkedin",
                    "social_website",
                ],
            )

        for profile, skills in all_skills_data:
            if not profile.skills:
                Skill.objects.bulk_create(
                    [
                        Skill(
                            name=skill["name"],
                            description=skill["description"],
                            user=profile,
                        )
                        for skill in skills
                    ]
                )

        logger.info(f"Updated {len(profiles_to_update)} profiles with skills")

    def create_projects(self):
        """Creates projects and links them to profiles with proper tags."""
        profiles = list(Profile.objects.filter(user__is_staff=False).all())

        if not profiles:
            logger.error("No profiles exist! Create profiles first.")
            return

        for index, project_data in enumerate(PROJECTS_DATA):
            profile = profiles[index % len(profiles)]
            print(profile)
            project = Project.objects.create(
                title=project_data["title"],
                owner=profile,
                description=project_data["description"],
                source_link=project_data["source_link"],
                demo_link=project_data["demo_link"],
            )

            for tag_name in project_data["tags"]:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                project.tags.add(tag)

            logger.info(f"Created project: {project.title}")

        logger.info(f"Successfully created {len(PROJECTS_DATA)} projects")

    def create_reviews(self):
        projects = list(Project.objects.all())
        profiles = list(Profile.objects.filter(user__is_staff=False).all())
        has_reviewed = []
        print(has_reviewed)
        created_count = 0

        if not projects or not profiles or len(profiles) < 2:
            logger.error("Need at least 2 profiles and some projects to create reviews")
            return

        for i, review_data in enumerate(REVIEWS_DATA):
            try:
                project = projects[i % len(projects)]
                print(project)
                available_reviewers = [p for p in profiles if p != project.owner]
                print(available_reviewers)

                if not available_reviewers:
                    logger.warning(
                        f"No available reviewers for project {project.title}"
                    )
                    continue

                review_created = False

                # Phase 1: Try reviewers who haven't reviewed ANY project yet
                unused_reviewers = [
                    r for r in available_reviewers if r not in has_reviewed
                ]
                if unused_reviewers:
                    for reviewer in unused_reviewers:
                        if not Review.objects.filter(
                            project=project, reviewer=reviewer
                        ).exists():
                            Review.objects.create(
                                project=project,
                                reviewer=reviewer,
                                content=review_data["content"],
                                value=review_data["value"],
                            )
                            created_count += 1
                            review_created = True
                            has_reviewed.append(reviewer)
                            logger.info(
                                f"Created review for project '{project.title}' by {reviewer.user.email} (first-time reviewer)"
                            )
                            break
                        
                # Phase 2: If no unused reviewers available, allow rotation
                if not review_created:
                    logger.debug(f"All reviewers have reviewed at least one project. Allowing rotation for project {project.title}")
                    
                    for reviewer in available_reviewers:
                        if not Review.objects.filter(project=project, reviewer=reviewer).exists():
                            Review.objects.create(
                                project=project,
                                reviewer=reviewer,
                                content=review_data["content"],
                                value=review_data["value"],
                            )
                            created_count += 1
                            review_created = True
                            has_reviewed.append(reviewer)
                            project.review_percentage
                            logger.info(
                                f"Created review for project '{project.title}' by {reviewer.user.email}"
                            )
                            break

                if not review_created:
                    logger.debug(
                        f"All potential reviewers have already reviewed project {project.title}"
                    )

            except Exception as e:
                logger.error(f"Error creating review: {str(e)}")

            logger.info(f"Successfully created {created_count} reviews")

    def create_reviews_2(self):
        """Creates reviews for projects."""
        projects = list(Project.objects.all())
        profiles = list(Profile.objects.filter(user__is_staff=False).all())
        print(profiles)
        if not projects or not profiles or len(profiles) < 2:
            logger.error("Need at least 2 profiles and some projects to create reviews")
            return

        created_count = 0

        for i, review_data in enumerate(REVIEWS_DATA):
            try:
                project = projects[i % len(projects)]
                print(project)
                available_reviewers = [p for p in profiles if p != project.owner]
                print(available_reviewers)

                if not available_reviewers:
                    logger.warning(
                        f"No available reviewers for project {project.title}"
                    )
                    continue

                # Try each available reviewer until we find one without existing review
                review_created = False
                for reviewer in available_reviewers:
                    if not Review.objects.filter(
                        project=project, reviewer=reviewer
                    ).exists():
                        Review.objects.create(
                            project=project,
                            reviewer=reviewer,
                            content=review_data["content"],
                            value=review_data["value"],
                        )
                        created_count += 1
                        review_created = True
                        project.review_percentage
                        logger.info(
                            f"Created review for project '{project.title}' by {reviewer.user.email}"
                        )
                        break

                if not review_created:
                    logger.debug(
                        f"All potential reviewers have already reviewed project {project.title}"
                    )

            except Exception as e:
                logger.error(f"Error creating review: {str(e)}")

        logger.info(f"Successfully created {created_count} reviews")

    def create_messages():
        pass