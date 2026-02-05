"""
AWS Services (S3 and Rekognition) utilities
Migrated from photoapp.py get_bucket and get_rekognition logic
"""

import boto3
import logging
from botocore.client import Config
from config import settings


def get_bucket():
    """
    Creates and returns S3 bucket object based on configuration.
    You should call close() on the object when you are done.
    
    This function preserves the exact logic from the original photoapp.py
    
    Returns:
        S3 bucket object
    
    Raises:
        Exception: If bucket access fails
    """
    try:
        s3 = boto3.resource(
            's3',
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_readwrite_access_key,
            aws_secret_access_key=settings.s3_readwrite_secret_key,
            config=Config(
                retries={
                    'max_attempts': 3,
                    'mode': 'standard'
                }
            )
        )
        
        bucket = s3.Bucket(settings.s3_bucket_name)
        return bucket
    
    except Exception as err:
        logging.error("get_bucket():")
        logging.error(str(err))
        raise


def get_rekognition():
    """
    Creates and returns Rekognition client object based on configuration.
    You should call close() on the object when you are done.
    
    This function preserves the exact logic from the original photoapp.py
    
    Returns:
        Rekognition client object
    
    Raises:
        Exception: If client creation fails
    """
    try:
        rekognition = boto3.client(
            'rekognition',
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_readwrite_access_key,
            aws_secret_access_key=settings.s3_readwrite_secret_key,
            config=Config(
                retries={
                    'max_attempts': 3,
                    'mode': 'standard'
                }
            )
        )
        
        return rekognition
    
    except Exception as err:
        logging.error("get_rekognition():")
        logging.error(str(err))
        raise
