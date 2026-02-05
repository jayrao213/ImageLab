"""
User routes
Migrated from photoapp.py get_users function
"""

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from models import User
from database import get_dbConn

router = APIRouter()


class CreateUserRequest(BaseModel):
    """Request model for creating a new user"""
    username: str
    givenname: str
    familyname: str
    password: str


@router.get("/", response_model=List[User])
async def get_users():
    """
    Returns a list of all users in the database.
    
    Each user contains userid, username, givenname, and familyname.
    The list is ordered by userid, ascending.
    
    This endpoint preserves the exact logic from photoapp.py get_users()
    
    Returns:
        List[User]: List of all users ordered by userid
    
    Raises:
        HTTPException: If database error occurs
    """
    dbConn = None
    dbCursor = None
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        
        sql = """
            SELECT userid, username, givenname, familyname, is_admin 
            FROM users 
            ORDER BY userid ASC
        """
        
        dbCursor.execute(sql)
        rows = dbCursor.fetchall()
        
        users = [
            User(
                userid=row[0],
                username=row[1],
                givenname=row[2],
                familyname=row[3],
                is_admin=bool(row[4])
            )
            for row in rows
        ]
        
        return users
    
    except Exception as err:
        logging.error("get_users():")
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


@router.post("/", response_model=User, status_code=201)
async def create_user(user_request: CreateUserRequest):
    """
    Creates a new user in the database.
    
    Args:
        user_request: User data (username, givenname, familyname)
    
    Returns:
        User: The created user with userid
    
    Raises:
        HTTPException: If username already exists or database error occurs
    """
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def create_user_inner():
        dbConn = None
        dbCursor = None
        try:
            dbConn = get_dbConn()
            dbCursor = dbConn.cursor()
            
            # Check if username already exists
            sql = "SELECT userid FROM users WHERE username = %s"
            dbCursor.execute(sql, [user_request.username])
            existing = dbCursor.fetchone()
            
            if existing:
                raise ValueError(f"Username '{user_request.username}' already exists")
            
            # Hash the password (same as auth.py)
            import hashlib
            salt = "imagelab-salt"
            password_hash = hashlib.sha256(f"{salt}{user_request.password}".encode()).hexdigest()

            # Insert new user with password_hash
            sql = """
                INSERT INTO users (username, givenname, familyname, password_hash)
                VALUES (%s, %s, %s, %s)
            """
            dbCursor.execute(sql, [
                user_request.username,
                user_request.givenname,
                user_request.familyname,
                password_hash
            ])
            
            # Get the new user ID
            sql = "SELECT LAST_INSERT_ID()"
            dbCursor.execute(sql)
            row = dbCursor.fetchone()
            new_userid = row[0]
            
            dbConn.commit()
            
            return User(
                userid=new_userid,
                username=user_request.username,
                givenname=user_request.givenname,
                familyname=user_request.familyname
            )
        
        except ValueError as err:
            if dbConn:
                dbConn.rollback()
            raise
        except Exception as err:
            if dbConn:
                dbConn.rollback()
            logging.error("create_user():")
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
        return create_user_inner()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

@router.delete("/{userid}", status_code=200)
async def delete_user(userid: int):
    """
    Deletes a user and all their associated images and labels.
    
    Args:
        userid: The ID of the user to delete
    
    Returns:
        dict: Success message
    
    Raises:
        HTTPException: If user not found or database error occurs
    """
    dbConn = None
    dbCursor = None
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        
        # Check if user exists
        sql = "SELECT userid FROM users WHERE userid = %s"
        dbCursor.execute(sql, [userid])
        user = dbCursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {userid} not found")
        
        # Delete image labels for user's images
        sql = """
            DELETE FROM image_labels 
            WHERE assetid IN (SELECT assetid FROM assets WHERE userid = %s)
        """
        dbCursor.execute(sql, [userid])
        
        # Delete user's images
        sql = "DELETE FROM assets WHERE userid = %s"
        dbCursor.execute(sql, [userid])
        
        # Delete the user
        sql = "DELETE FROM users WHERE userid = %s"
        dbCursor.execute(sql, [userid])
        
        dbConn.commit()
        
        return {"message": f"User {userid} and all associated data deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as err:
        if dbConn:
            dbConn.rollback()
        logging.error("delete_user():")
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