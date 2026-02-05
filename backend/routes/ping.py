"""
Ping/Health check route
Migrated from photoapp.py get_ping function
"""

from fastapi import APIRouter
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from models import PingResponse
from database import get_dbConn
from aws_services import get_bucket

router = APIRouter()


@router.get("/ping", response_model=PingResponse)
async def get_ping():
    """
    Pings the S3 bucket and database server to check if they are accessible.
    
    Returns a response with:
    - bucket_items: Number of items in the S3 bucket (or error message)
    - database_users: Number of users in the database (or error message)
    
    This endpoint preserves the exact logic from photoapp.py get_ping()
    
    Returns:
        PingResponse: Status of S3 bucket and database
    """
    
    def get_M():
        """Get number of items in S3 bucket"""
        bucket = None
        try:
            bucket = get_bucket()
            assets = bucket.objects.all()
            M = len(list(assets))
            return M
        except Exception as err:
            logging.error("get_ping.get_M():")
            logging.error(str(err))
            raise
        finally:
            if bucket:
                try:
                    bucket.meta.client.close()
                except:
                    pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def get_N():
        """Get number of users in database"""
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            sql = "SELECT count(userid) FROM users;"
            
            dbCursor.execute(sql)
            row = dbCursor.fetchone()
            
            N = row[0]
            return N
        
        except Exception as err:
            logging.error("get_ping.get_N():")
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
    
    # Compute M and N separately for independent exception handling
    try:
        M = get_M()
    except Exception as err:
        M = str(err)
    
    try:
        N = get_N()
    except Exception as err:
        N = str(err)
    
    return PingResponse(bucket_items=M, database_users=N)
