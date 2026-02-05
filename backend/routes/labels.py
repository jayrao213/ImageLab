"""
Label routes
Migrated from photoapp.py: get_image_labels and get_images_with_label functions
"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from models import ImageLabel, ImageWithLabel
from database import get_dbConn

router = APIRouter()


@router.get("/count")
async def get_labels_count():
    """
    Returns the total count of all AI-detected labels in the database.
    
    Returns:
        dict: Total count of labels
    
    Raises:
        HTTPException: If database error occurs
    """
    dbConn = None
    dbCursor = None
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        
        sql = "SELECT COUNT(*) FROM image_labels"
        dbCursor.execute(sql)
        count = dbCursor.fetchone()[0]
        
        return {"count": count}
    
    except Exception as err:
        logging.error("get_labels_count():")
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


@router.get("/image/{assetid}", response_model=List[ImageLabel])
async def get_image_labels(assetid: int):
    """
    Retrieves AI-generated labels for a specific image.
    
    When an image is uploaded, AWS Rekognition automatically labels objects
    in the image. This endpoint retrieves those labels.
    
    This endpoint preserves the exact logic from photoapp.py get_image_labels()
    
    Args:
        assetid: Image asset ID to retrieve labels for
    
    Returns:
        List[ImageLabel]: List of labels with confidence scores, ordered by label
    
    Raises:
        HTTPException: If assetid doesn't exist or database error occurs
    """
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def get_image_labels_inner():
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            # First verify assetid exists
            sql = """
                SELECT assetid 
                FROM assets
                WHERE assetid = %s;
            """
            dbCursor.execute(sql, [assetid])
            row = dbCursor.fetchone()
            
            if row is None:
                raise ValueError("no such assetid")
            
            # Get labels for this image
            sql = """
                SELECT label, confidence
                FROM image_labels
                WHERE assetid = %s
                ORDER BY label ASC;
            """
            dbCursor.execute(sql, [assetid])
            rows = dbCursor.fetchall()
            
            image_labels = []
            for row in rows:
                image_labels.append((str(row[0]), int(row[1])))
            
            return image_labels
        
        except Exception as err:
            logging.error("get_image_labels():")
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
        labels_data = get_image_labels_inner()
        labels = [
            ImageLabel(label=label, confidence=confidence)
            for label, confidence in labels_data
        ]
        return labels
    
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/search", response_model=List[ImageWithLabel])
async def get_images_with_label(label: str, userid: int = None):
    """
    Searches for all images that contain a specific label (partial match).
    
    Performs a case-insensitive search for images with labels matching
    the search term. Partial matches are supported (e.g., 'boat' matches 'sailboat').
    Optionally filter by userid to only search that user's images.
    
    This endpoint preserves the exact logic from photoapp.py get_images_with_label()
    
    Args:
        label: Label to search for (can be partial)
        userid: Optional user ID to filter results
    
    Returns:
        List[ImageWithLabel]: Images with matching labels, ordered by assetid then label
    
    Raises:
        HTTPException: If database error occurs
    """
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def get_images_with_label_inner():
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            search_pattern = "%" + str(label) + "%"
            
            if userid is not None:
                sql = """
                    SELECT il.assetid, a.localname, il.label, il.confidence
                    FROM image_labels il
                    INNER JOIN assets a ON il.assetid = a.assetid
                    WHERE il.label LIKE %s AND a.userid = %s
                    ORDER BY il.assetid ASC, il.label ASC;
                """
                dbCursor.execute(sql, [search_pattern, userid])
            else:
                sql = """
                    SELECT il.assetid, a.localname, il.label, il.confidence
                    FROM image_labels il
                    INNER JOIN assets a ON il.assetid = a.assetid
                    WHERE il.label LIKE %s
                    ORDER BY il.assetid ASC, il.label ASC;
                """
                dbCursor.execute(sql, [search_pattern])
            
            rows = dbCursor.fetchall()
            
            images = []
            for row in rows:
                images.append({
                    "assetid": int(row[0]),
                    "localname": str(row[1]),
                    "label": str(row[2]),
                    "confidence": int(row[3])
                })
            
            return images
        
        except Exception as err:
            logging.error("get_images_with_label():")
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
        images_data = get_images_with_label_inner()
        images = [
            ImageWithLabel(
                assetid=item["assetid"],
                localname=item["localname"],
                label=item["label"],
                confidence=item["confidence"]
            )
            for item in images_data
        ]
        return images
    
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
