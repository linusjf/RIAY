"""Image upload functionality for imgbb.com API."""

import os
import requests
import sys
from configenv import ConfigEnv

# Constants
CONFIG_FILE = 'config.env'
IMGBB_API_KEY_VAR = "IMGBB_API_KEY"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Load environment variables using ConfigEnv
config = ConfigEnv(CONFIG_FILE)
IMGBB_API_KEY = config.get(IMGBB_API_KEY_VAR)
if not IMGBB_API_KEY:
    raise ValueError(f"{IMGBB_API_KEY_VAR} environment variable not set")


class ImgBBUploader:
    """Handles image uploads to imgbb.com."""

    def __init__(self, api_key: str = IMGBB_API_KEY):
        """Initialize with API key."""
        self.api_key = api_key
        self.upload_url = IMGBB_UPLOAD_URL

    def upload_image(self, image_path: str) -> tuple[str, str]:
        """Upload image to imgbb and return URL and delete URL.

        Args:
            image_path: Path to the image file to upload

        Returns:
            tuple: (image_url, delete_url)

        Raises:
            Exception: If upload fails
        """
        with open(image_path, "rb") as file:
            response = requests.post(
                self.upload_url,
                data={"key": self.api_key},
                files={"image": file}
            )

        if response.status_code == 200:
            json_data = response.json()["data"]
            return (json_data["url"], json_data["delete_url"])

        raise Exception(f"Upload failed: {response.status_code} {response.text}")


def upload_to_imgbb(image_path: str) -> tuple[str, str]:
    """Convenience function for direct upload without class instantiation.

    Args:
        image_path: Path to the image file to upload

    Returns:
        tuple: (image_url, delete_url)
    """
    uploader = ImgBBUploader()
    image_url, delete_url = uploader.upload_image(image_path)
    if delete_url:
        print(
            f"Delete uploaded image in the browser using {delete_url}",
            file=sys.stderr
        )
    return image_url, delete_url
