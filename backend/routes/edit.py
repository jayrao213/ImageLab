"""
Image editing routes
Integrates ImageLab functionality with PhotoApp's storage system
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
from PIL import Image as PILImage
from io import BytesIO
import logging

from image_processing import Image, Pixel
from aws_services import get_bucket, get_rekognition
from database import get_dbConn

router = APIRouter()


def pil_to_internal(pil_img: PILImage.Image) -> Image:
    """Convert PIL Image to internal Image format"""
    pil_img = pil_img.convert("RGB")
    width, height = pil_img.size
    data = []
    for r in range(height):
        y = height - 1 - r
        row = []
        for x in range(width):
            r8, g8, b8 = pil_img.getpixel((x, y))
            row.append(Pixel(r8, g8, b8))
        data.append(row)
    return Image(data, [3779, 3779])


def internal_to_pil(img: Image) -> PILImage.Image:
    """Convert internal Image format to PIL Image"""
    h = len(img._data)
    w = len(img._data[0])
    pil = PILImage.new("RGB", (w, h))
    for r, row in enumerate(img._data):
        y = h - 1 - r
        for x, p in enumerate(row):
            pil.putpixel((x, y), (p._red, p._green, p._blue))
    return pil


@router.post("/apply")
async def apply_transformation(
    file: Optional[UploadFile] = File(None),
    assetid: Optional[int] = Form(None),
    action: str = Form(...),
    amount: Optional[float] = Form(None),
    factor: Optional[float] = Form(None),
    size: Optional[int] = Form(None),
    r: Optional[int] = Form(None),
    g: Optional[int] = Form(None),
    b: Optional[int] = Form(None),
    degrees: Optional[int] = Form(None),
    block: Optional[int] = Form(None),
    prompt: Optional[str] = Form(None),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    resize_width: Optional[int] = Form(None),
    resize_height: Optional[int] = Form(None),
):
    """
    Apply an image transformation
    
    Can load image from either:
    - Uploaded file (file parameter)
    - Database by assetid (assetid parameter)
    
    Returns the transformed image as PNG
    """
    
    # Load image from either upload or database
    if assetid:
        # Load from S3 via database
        try:
            bucket = get_bucket()
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            sql = "SELECT bucketkey FROM assets WHERE assetid = %s"
            dbCursor.execute(sql, [assetid])
            row = dbCursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Asset {assetid} not found")
            
            bucketkey = row[0]
            
            # Download from S3
            response = bucket.Object(bucketkey).get()
            raw = response['Body'].read()
            pil_in = PILImage.open(BytesIO(raw))
            
            dbCursor.close()
            dbConn.close()
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error loading image from database: {e}")
            raise HTTPException(status_code=500, detail="Failed to load image from database")
    else:
        # Load from uploaded file
        if not file:
            raise HTTPException(status_code=400, detail="Image file or assetid required")
        try:
            raw = await file.read()
            pil_in = PILImage.open(BytesIO(raw))
        except Exception:
            raise HTTPException(status_code=400, detail="Could not read image")

    # Convert to internal format
    img = pil_to_internal(pil_in)

    # Apply transformation
    try:
        if action == "resize":
            if not resize_width or not resize_height:
                raise HTTPException(status_code=400, detail="Width and height required for resize")
            img.resize(int(resize_width), int(resize_height))
        elif action == "add_color":
            img.add_color(Pixel(int(r or 0), int(g or 0), int(b or 0)))
        elif action == "red_shift":
            img.red_shift(float(amount or 0))
        elif action == "green_shift":
            img.green_shift(float(amount or 0))
        elif action == "blue_shift":
            img.blue_shift(float(amount or 0))
        elif action == "shift_brightness":
            img.shift_brightness(float(factor or 1.0))
        elif action == "make_monochrome":
            img.make_monochrome()
        elif action == "mirror_horizontal":
            img.mirror_horizontal()
        elif action == "mirror_vertical":
            img.mirror_vertical()
        elif action == "tile":
            img.tile(int(size or 1))
        elif action == "blur":
            img.blur()
        elif action == "negative":
            img.negative()
        elif action == "sepia":
            img.sepia()
        elif action == "rotate":
            img.rotate(int(degrees or 90))
        elif action == "pixelate":
            img.pixelate(int(block or 8))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action '{action}'")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error applying transformation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # Convert back to PIL and return
    pil_out = internal_to_pil(img)
    buf = BytesIO()
    pil_out.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.post("/save")
async def save_edited_image(
    file: UploadFile = File(...),
    userid: int = Form(...),
    replace_assetid: Optional[int] = Form(None),
):
    """
    Save an edited image to the database
    
    If replace_assetid is provided, updates that existing asset with new image
    Otherwise, creates a new asset
    
    Returns the assetid
    """
    import uuid
    import os
    
    if replace_assetid:
        # Replace mode: Update existing asset
        try:
            bucket = get_bucket()
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            # Verify asset exists and belongs to user
            sql = "SELECT bucketkey, localname FROM assets WHERE assetid = %s AND userid = %s"
            dbCursor.execute(sql, [replace_assetid, userid])
            row = dbCursor.fetchone()
            
            if not row:
                dbCursor.close()
                dbConn.close()
                raise HTTPException(status_code=404, detail="Asset not found or access denied")
            
            old_bucketkey = row[0]
            
            # Get username for new bucketkey path
            sql = "SELECT username FROM users WHERE userid = %s"
            dbCursor.execute(sql, [userid])
            user_row = dbCursor.fetchone()
            if not user_row:
                dbCursor.close()
                dbConn.close()
                raise HTTPException(status_code=404, detail="User not found")
            
            username = user_row[0]
            
            # Upload new image to S3
            unique_part = str(uuid.uuid4())
            new_bucketkey = f"{username}/{unique_part}-{file.filename}"
            
            # Save file temporarily
            temp_filename = f"temp_{unique_part}_{file.filename}"
            with open(temp_filename, "wb") as f:
                content = await file.read()
                f.write(content)
            
            try:
                # Upload new image
                bucket.upload_file(temp_filename, new_bucketkey)
                
                # Delete old image from S3
                bucket.Object(old_bucketkey).delete()
                
                # Update database record
                sql = "UPDATE assets SET bucketkey = %s, localname = %s WHERE assetid = %s"
                dbCursor.execute(sql, [new_bucketkey, file.filename, replace_assetid])
                dbConn.commit()
                
                # Delete old labels
                sql = "DELETE FROM image_labels WHERE assetid = %s"
                dbCursor.execute(sql, [replace_assetid])
                dbConn.commit()
                
                # Run Rekognition on new image
                rekognition = get_rekognition()
                response = rekognition.detect_labels(
                    Image={
                        'S3Object': {
                            'Bucket': bucket.name,
                            'Name': new_bucketkey,
                        },
                    },
                    MaxLabels=100,
                    MinConfidence=80,
                )
                labels = response['Labels']
                
                # Store new labels
                for label in labels:
                    name = label['Name']
                    confidence = int(label['Confidence'])
                    sql = "INSERT INTO image_labels (assetid, label, confidence) VALUES (%s, %s, %s)"
                    dbCursor.execute(sql, [replace_assetid, name, confidence])
                
                dbConn.commit()
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            
            dbCursor.close()
            dbConn.close()
            
            return {"assetid": replace_assetid, "message": "Image replaced successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error replacing image: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to replace image: {str(e)}")
    
    else:
        # New image mode: Use existing upload logic
        try:
            from routes.images import post_image
            result = await post_image(userid=userid, file=file)
            return result
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error saving edited image: {e}")
            raise HTTPException(status_code=500, detail="Failed to save edited image")
