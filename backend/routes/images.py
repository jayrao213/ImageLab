"""
Image routes
Migrated from photoapp.py: get_images, post_image, get_image, delete_images functions
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
import logging
import uuid
import os
import io
import hashlib
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
from PIL import Image as PILImage

from models import Image, ImageUploadResponse, DeleteResponse
from database import get_dbConn
from aws_services import get_bucket, get_rekognition

router = APIRouter()

# Simple in-memory cache for thumbnails (max 100 items)
_thumbnail_cache = {}
_THUMBNAIL_CACHE_MAX_SIZE = 100


@router.get("/", response_model=List[Image])
async def get_images(userid: Optional[int] = None):
    """
    Returns a list of all images in the database, optionally filtered by userid.
    
    Each image contains assetid, userid, localname, and bucketkey.
    The list is ordered by assetid, ascending.
    
    This endpoint preserves the exact logic from photoapp.py get_images()
    
    Args:
        userid: Optional filter to return images for specific user only
    
    Returns:
        List[Image]: List of images ordered by assetid
    
    Raises:
        HTTPException: If database error occurs
    """
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def get_images_inner():
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            if userid:
                sql = """
                    SELECT assets.assetid, users.userid, localname, bucketkey
                    FROM users
                    INNER JOIN assets ON users.userid = assets.userid
                    WHERE users.userid = %s
                    ORDER BY assets.assetid ASC
                """
                dbCursor.execute(sql, [userid])
            else:
                sql = """
                    SELECT assets.assetid, users.userid, localname, bucketkey
                    FROM users
                    INNER JOIN assets ON users.userid = assets.userid
                    ORDER BY assets.assetid ASC
                """
                dbCursor.execute(sql)
            
            rows = dbCursor.fetchall()
            return list(rows)
        
        except Exception as err:
            logging.error("get_images():")
            logging.error(str(err))
            raise
        
        finally:
            if dbCursor:
                try:
                    dbCursor.close()
                except:
                    pass
            if dbConn:
                try:
                    dbConn.close()
                except:
                    pass
    
    try:
        rows = get_images_inner()
        images = [
            Image(
                assetid=row[0],
                userid=row[1],
                localname=row[2],
                bucketkey=row[3]
            )
            for row in rows
        ]
        return images
    
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/", response_model=ImageUploadResponse)
async def post_image(
    userid: int = Form(...),
    file: UploadFile = File(...)
):
    """
    Uploads an image to S3 and creates a database record.
    
    The image is analyzed by AWS Rekognition to detect labels,
    which are stored in the database for later retrieval.
    
    This endpoint preserves the exact logic from photoapp.py post_image()
    
    Args:
        userid: User ID who owns this image
        file: Image file to upload
    
    Returns:
        ImageUploadResponse: Contains the new assetid
    
    Raises:
        HTTPException: If user doesn't exist or upload fails
    """
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def post_image_inner1():
        """Verify user exists and get username"""
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            sql = "SELECT username FROM users WHERE userid = %s"
            dbCursor.execute(sql, [userid])
            row = dbCursor.fetchone()
            
            if row:
                return row[0]
            else:
                raise ValueError("no such userid")
        
        except Exception as err:
            logging.error("post_image():")
            logging.error(str(err))
            raise
        
        finally:
            if dbCursor:
                try:
                    dbCursor.close()
                except:
                    pass
            if dbConn:
                try:
                    dbConn.close()
                except:
                    pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def post_image_inner2(bucketkey):
        """Insert asset record and return asset_id"""
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            sql = """
                INSERT INTO assets (userid, localname, bucketkey)
                VALUES (%s, %s, %s);
            """
            dbCursor.execute(sql, [userid, file.filename, bucketkey])
            
            sql = "SELECT LAST_INSERT_ID();"
            dbCursor.execute(sql)
            row = dbCursor.fetchone()
            asset_id = row[0]
            
            dbConn.commit()
            return asset_id
        
        except Exception as err:
            dbConn.rollback()
            logging.error("post_image():")
            logging.error(str(err))
            raise
        
        finally:
            if dbCursor:
                try:
                    dbCursor.close()
                except:
                    pass
            if dbConn:
                try:
                    dbConn.close()
                except:
                    pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def post_image_inner3(asset_id, label_name, label_confidence):
        """Insert image label"""
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            sql = """
                INSERT INTO image_labels (assetid, label, confidence)
                VALUES(%s, %s, %s)
            """
            dbCursor.execute(sql, [asset_id, label_name, label_confidence])
            dbConn.commit()
        
        except Exception as err:
            dbConn.rollback()
            logging.error("post_image():")
            logging.error(str(err))
            raise
        
        finally:
            if dbCursor:
                try:
                    dbCursor.close()
                except:
                    pass
            if dbConn:
                try:
                    dbConn.close()
                except:
                    pass
    
    try:
        # Step 1: Verify user exists
        username = post_image_inner1()
        
        # Step 2: Upload to S3
        bucket = get_bucket()
        unique_part = str(uuid.uuid4())
        bucketkey = f"{username}/{unique_part}-{file.filename}"
        
        # Save file temporarily to upload to S3
        temp_filename = f"temp_{unique_part}_{file.filename}"
        with open(temp_filename, "wb") as f:
            content = await file.read()
            f.write(content)
        
        try:
            bucket.upload_file(temp_filename, bucketkey)
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        
        # Step 3: Insert database record
        asset_id = post_image_inner2(bucketkey)
        
        # Step 4: Analyze with Rekognition
        rekognition = get_rekognition()
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket.name,
                    'Name': bucketkey,
                },
            },
            MaxLabels=100,
            MinConfidence=80,
        )
        labels = response['Labels']
        
        # Step 5: Store labels
        for label in labels:
            name = label['Name']
            confidence = int(label['Confidence'])
            post_image_inner3(asset_id, name, confidence)
        
        return ImageUploadResponse(
            assetid=asset_id,
            message=f"Image uploaded successfully with {len(labels)} labels detected"
        )
    
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        logging.error("post_image():")
        logging.error(str(err))
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/{assetid}")
async def get_image(assetid: int, thumbnail: bool = False, download: bool = False):
    """
    Downloads an image from S3 by assetid.
    
    Returns the image file as a streaming response.
    Optionally returns a thumbnail (max 400px width) for gallery view.
    
    This endpoint preserves the exact logic from photoapp.py get_image()
    
    Args:
        assetid: Asset ID of the image to download
        thumbnail: If True, returns a resized thumbnail for faster loading
    
    Returns:
        StreamingResponse: The image file (or thumbnail)
    
    Raises:
        HTTPException: If assetid doesn't exist or download fails
    """
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def get_image_inner():
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            sql = """
                SELECT localname, bucketkey
                FROM assets
                WHERE assetid = %s;
            """
            dbCursor.execute(sql, [assetid])
            row = dbCursor.fetchone()
            
            if row is None:
                raise ValueError("no such assetid")
            
            localname = row[0]
            bucketkey = row[1]
            
            return localname, bucketkey
        
        except Exception as err:
            logging.error("get_image():")
            logging.error(str(err))
            raise
        
        finally:
            if dbCursor:
                try:
                    dbCursor.close()
                except:
                    pass
            if dbConn:
                try:
                    dbConn.close()
                except:
                    pass
    
    try:
        localname, bucketkey = get_image_inner()
        
        # If thumbnail requested, check cache first
        if thumbnail:
            cache_key = f"thumb_{assetid}"
            if cache_key in _thumbnail_cache:
                # Serve from cache
                cached_data = _thumbnail_cache[cache_key]
                buffer = io.BytesIO(cached_data)
                content_type = "image/jpeg"
            else:
                # Download from S3 and create thumbnail
                bucket = get_bucket()
                buffer = io.BytesIO()
                bucket.download_fileobj(bucketkey, buffer)
                buffer.seek(0)
                
                try:
                    img = PILImage.open(buffer)
                    # Resize to max 300px width while maintaining aspect ratio
                    max_width = 300
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)
                    
                    # Save resized image to new buffer with aggressive compression
                    thumb_buffer = io.BytesIO()
                    img = img.convert('RGB')  # Convert to RGB for JPEG
                    img.save(thumb_buffer, format='JPEG', quality=70, optimize=True)
                    thumb_data = thumb_buffer.getvalue()
                    
                    # Store in cache (with size limit)
                    if len(_thumbnail_cache) >= _THUMBNAIL_CACHE_MAX_SIZE:
                        # Remove oldest entry
                        oldest_key = next(iter(_thumbnail_cache))
                        del _thumbnail_cache[oldest_key]
                    _thumbnail_cache[cache_key] = thumb_data
                    
                    buffer = io.BytesIO(thumb_data)
                    content_type = "image/jpeg"
                except Exception as e:
                    logging.warning(f"Failed to create thumbnail for {assetid}: {e}, serving original")
                    buffer.seek(0)
                    content_type = "application/octet-stream"
                    if localname.lower().endswith(('.jpg', '.jpeg')):
                        content_type = "image/jpeg"
                    elif localname.lower().endswith('.png'):
                        content_type = "image/png"
        else:
            # Download full image from S3
            bucket = get_bucket()
            buffer = io.BytesIO()
            bucket.download_fileobj(bucketkey, buffer)
            buffer.seek(0)
            
            # Determine content type from filename for full images
            content_type = "application/octet-stream"
            if localname.lower().endswith(('.jpg', '.jpeg')):
                content_type = "image/jpeg"
            elif localname.lower().endswith('.png'):
                content_type = "image/png"
        
        # Set cache headers for better performance
        cache_max_age = 3600 if thumbnail else 86400  # 1 hour for thumbnails, 24 hours for full images
        disposition = "inline" if thumbnail or not download else "attachment"
        
        return StreamingResponse(
            buffer,
            media_type=content_type,
            headers={
                "Content-Disposition": f"{disposition}; filename={localname}",
                "Cache-Control": f"public, max-age={cache_max_age}",
                "X-Content-Type-Options": "nosniff",
            }
        )
    
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        logging.error("get_image():")
        logging.error(str(err))
        raise HTTPException(status_code=500, detail=str(err))


@router.delete("/", response_model=DeleteResponse)
async def delete_images(userid: int | None = None):
    """
    Deletes all images and associated labels from the database and S3.
    
    Args:
        userid: Optional user ID to delete images for a specific user only.
                If None, deletes all images (admin-only).
    
    The images are not deleted from S3 unless the database is successfully cleared.
    
    This endpoint preserves the exact logic from photoapp.py delete_images()
    
    Returns:
        DeleteResponse: Success status
    
    Raises:
        HTTPException: If deletion fails
    """
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def delete_images_inner1():
        """Get all bucketkeys to delete"""
        dbConn = None
        dbCursor = None
        objects_to_delete = []
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            if userid is not None:
                # Delete only images for specific user
                sql = "SELECT bucketkey FROM assets WHERE userid = %s;"
                dbCursor.execute(sql, (userid,))
            else:
                # Delete all images
                sql = "SELECT bucketkey FROM assets;"
                dbCursor.execute(sql)
            
            rows = dbCursor.fetchall()
            
            for row in rows:
                objects_to_delete.append({'Key': str(row[0])})
            
            return objects_to_delete
        
        except Exception as err:
            logging.error("delete_images():")
            logging.error(str(err))
            raise
        
        finally:
            if dbCursor:
                try:
                    dbCursor.close()
                except:
                    pass
            if dbConn:
                try:
                    dbConn.close()
                except:
                    pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def delete_images_inner2():
        """Clear database tables"""
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            if userid is not None:
                # Delete only for specific user
                # First delete labels for this user's images
                sql = "DELETE il FROM image_labels il INNER JOIN assets a ON il.assetid = a.assetid WHERE a.userid = %s;"
                dbCursor.execute(sql, (userid,))
                
                # Then delete the images
                sql = "DELETE FROM assets WHERE userid = %s;"
                dbCursor.execute(sql, (userid,))
            else:
                # Delete all images and labels
                sql = "SET foreign_key_checks = 0;"
                dbCursor.execute(sql)
                
                sql = "TRUNCATE TABLE assets;"
                dbCursor.execute(sql)
                
                sql = "TRUNCATE TABLE image_labels;"
                dbCursor.execute(sql)
                
                sql = "SET foreign_key_checks = 1;"
                dbCursor.execute(sql)
                
                sql = "ALTER TABLE assets AUTO_INCREMENT = 1001;"
                dbCursor.execute(sql)
            
            dbConn.commit()
        
        except Exception as err:
            logging.error("delete_images():")
            logging.error(str(err))
            raise
        
        finally:
            if dbCursor:
                try:
                    dbCursor.close()
                except:
                    pass
            if dbConn:
                try:
                    dbConn.close()
                except:
                    pass
    
    try:
        # Get list of objects to delete
        objects_to_delete = delete_images_inner1()
        
        # Clear database
        delete_images_inner2()
        
        # Delete from S3
        if len(objects_to_delete) > 0:
            bucket = get_bucket()
            bucket.delete_objects(Delete={'Objects': objects_to_delete})
        
        return DeleteResponse(
            success=True,
            message=f"Deleted {len(objects_to_delete)} images successfully"
        )
    
    except Exception as err:
        logging.error("delete_images():")
        logging.error(str(err))
        raise HTTPException(status_code=500, detail=str(err))


@router.delete("/{assetid}", response_model=DeleteResponse)
async def delete_single_image(assetid: int):
    """
    Deletes a single image and its associated labels from the database and S3.
    
    Args:
        assetid: The ID of the image to delete
    
    Returns:
        DeleteResponse: Success status
    
    Raises:
        HTTPException: If image not found or deletion fails
    """
    dbConn = None
    dbCursor = None
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        
        # Get image info
        sql = "SELECT bucketkey FROM assets WHERE assetid = %s"
        dbCursor.execute(sql, [assetid])
        row = dbCursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Image with ID {assetid} not found")
        
        bucketkey = row[0]
        
        # Delete image labels
        sql = "DELETE FROM image_labels WHERE assetid = %s"
        dbCursor.execute(sql, [assetid])
        
        # Delete from assets table
        sql = "DELETE FROM assets WHERE assetid = %s"
        dbCursor.execute(sql, [assetid])
        
        dbConn.commit()
        
        # Delete from S3
        bucket = get_bucket()
        bucket.delete_objects(Delete={'Objects': [{'Key': bucketkey}]})
        
        # Clear from thumbnail cache
        cache_key = f"thumb_{assetid}"
        if cache_key in _thumbnail_cache:
            del _thumbnail_cache[cache_key]
        
        return DeleteResponse(
            success=True,
            message=f"Image {assetid} deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as err:
        if dbConn:
            dbConn.rollback()
        logging.error("delete_single_image():")
        logging.error(str(err))
        raise HTTPException(status_code=500, detail=str(err))
    
    finally:
        if dbCursor:
            try:
                dbCursor.close()
            except:
                pass
        if dbConn:
            try:
                dbConn.close()
            except:
                pass
