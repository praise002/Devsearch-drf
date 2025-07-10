import os

from apps.common.management.commands.data import PROFILES_DATA, USERS_DATA

CURRENT_DIR = r"C:\Users\Praise Idowu\Documents\back-end\projects\devsearch-api\apps\common\management\commands"


test_images_directory = os.path.join(CURRENT_DIR, "images")


def update_profiles():
    """Updates profiles with data from PROFILES_DATA."""
    for user_data, profile_data in zip(USERS_DATA, PROFILES_DATA):
        print(user_data, profile_data)


# update_profiles()


def get_image(images_list, substring):
    return [s for s in images_list if s.startswith(substring)]


def get_images_path():
    images = os.listdir(test_images_directory)

    image_file_name = get_image(images, "avatar")
    
    for file_name in image_file_name:
        image_path = os.path.join(test_images_directory, file_name)
        print(image_path)


get_images_path()
