"""Image upload functionality for imgbb.com API."""

import requests
import sys
from typing import Optional, Tuple
from configenv import ConfigEnv
from configconstants import ConfigConstants

# Constants
CONFIG_FILE = 'config.env'
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Load environment variables using ConfigEnv
config = ConfigEnv(filepath=CONFIG_FILE, include_os_env=True)
IMGBB_API_KEY: Optional[str] = config.get(ConfigConstants.IMGBB_API_KEY)
if not IMGBB_API_KEY:
    raise ValueError(f"{ConfigConstants.IMGBB_API_KEY} environment variable not set")


class ImgBBUploader:
    """Handles image uploads to imgbb.com."""

    def __init__(self, api_key: str = IMGBB_API_KEY) -> None:
        """Initialize with API key.
        
        Args:
            api_key: ImgBB API key
        """
        self.api_key: str = api_key
        self.upload_url: str = IMGBB_UPLOAD_URL

    def upload_image(self, image_path: str) -> Tuple[str, str]:
        """Upload image to imgbb and return URL and delete URL.

        Args:
            image_path: Path to the image file to upload

        Returns:
            Tuple containing image_url and delete_url

        Raises:
            Exception: If upload fails
        """
        with open(image_path, "rb") as file:
            response: requests.Response = requests.post(
                self.upload_url,
                data={"key": self.api_key},
                files={"image": file}
            )

        if response.status_code == 200:
            json_data: dict = response.json()["data"]
            return (json_data["url"], json_data["delete_url"])

        raise Exception(f"Upload failed: {response.status_code} {response.text}")


def upload_to_imgbb(image_path: str) -> Tuple[str, str]:
    """Convenience function for direct upload without class instantiation.

    Args:
        image_path: Path to the image file to upload

    Returns:
        Tuple containing image_url and delete_url
    """
    uploader: ImgBBUploader = ImgBBUploader()
    image_url: str
    delete_url: str
    image_url, delete_url = uploader.upload_image(image_path)
    if delete_url:
        print(
            f"Delete uploaded image in the browser using {delete_url}",
            file=sys.stderr
        )
    return image_url, delete_url
