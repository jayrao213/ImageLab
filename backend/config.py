"""
Configuration management for PhotoApp
Loads settings from environment variables (.env)
"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
]


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # RDS Database settings
    rds_endpoint: str = Field(..., alias="RDS_ENDPOINT")
    rds_port: int = Field(..., alias="RDS_PORT")
    rds_region: str = Field(..., alias="RDS_REGION")
    rds_username: str = Field(..., alias="RDS_USERNAME")
    rds_password: str = Field(..., alias="RDS_PASSWORD")
    rds_database: str = Field(..., alias="RDS_DATABASE")
    
    # S3 settings
    s3_bucket_name: str = Field(..., alias="S3_BUCKET_NAME")
    s3_region: str = Field(..., alias="S3_REGION")
    
    # S3 Read-only credentials
    s3_readonly_region: str = Field(..., alias="S3_READONLY_REGION")
    s3_readonly_access_key: str = Field(..., alias="S3_READONLY_ACCESS_KEY")
    s3_readonly_secret_key: str = Field(..., alias="S3_READONLY_SECRET_KEY")
    
    # S3 Read-write credentials
    s3_readwrite_region: str = Field(..., alias="S3_READWRITE_REGION")
    s3_readwrite_access_key: str = Field(..., alias="S3_READWRITE_ACCESS_KEY")
    s3_readwrite_secret_key: str = Field(..., alias="S3_READWRITE_SECRET_KEY")

    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
