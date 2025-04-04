import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


async def upload_avatar(file: UploadFile) -> str:
    try:
        result = cloudinary.uploader.upload(
            file.file, folder="avatars", resource_type="auto"
        )
        return result["secure_url"]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload avatar: {str(e)}"
        )
