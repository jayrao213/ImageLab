"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel
from typing import List, Tuple, Union


# Response Models
class User(BaseModel):
    """User model"""
    userid: int
    username: str
    givenname: str
    familyname: str
    is_admin: bool = False


class Image(BaseModel):
    """Image/Asset model"""
    assetid: int
    userid: int
    localname: str
    bucketkey: str


class ImageLabel(BaseModel):
    """Image label model"""
    label: str
    confidence: int


class ImageWithLabel(BaseModel):
    """Image with label search result"""
    assetid: int
    localname: str
    label: str
    confidence: int


class PingResponse(BaseModel):
    """Ping response model"""
    bucket_items: Union[int, str]
    database_users: Union[int, str]


class ImageUploadResponse(BaseModel):
    """Response from image upload"""
    assetid: int
    message: str


class ImageDownloadResponse(BaseModel):
    """Response from image download"""
    filename: str
    data: bytes = None  # Binary data for the image


class DeleteResponse(BaseModel):
    """Response from delete operation"""
    success: bool
    message: str


# Request Models
class ImageUploadRequest(BaseModel):
    """Request to upload an image"""
    userid: int
    filename: str
    # Note: actual file upload will use FastAPI's UploadFile
