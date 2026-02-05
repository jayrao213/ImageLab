"""
Authentication routes
Handles user registration, login, and token management
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import logging
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta

from database import get_dbConn

router = APIRouter()
security = HTTPBearer()

# Secret key for JWT - in production, use environment variable
JWT_SECRET = "imagelab-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


# Request/Response Models
class RegisterRequest(BaseModel):
    username: str
    password: str
    givenname: str
    familyname: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    userid: int
    username: str
    givenname: str
    familyname: str
    is_admin: bool = False


class UserInfo(BaseModel):
    userid: int
    username: str
    givenname: str
    familyname: str
    is_admin: bool = False


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt"""
    salt = "imagelab-salt"  # In production, use unique salt per user
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def create_token(userid: int, username: str, is_admin: bool = False) -> str:
    """Create a JWT token"""
    payload = {
        "userid": userid,
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInfo:
    """Dependency to get the current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    return UserInfo(
        userid=payload["userid"],
        username=payload["username"],
        givenname="",  # We could fetch from DB if needed
        familyname="",
        is_admin=payload.get("is_admin", False)
    )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Register a new user with password
    """
    dbConn = None
    dbCursor = None
    
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        
        # Check if username already exists
        sql = "SELECT userid FROM users WHERE username = %s"
        dbCursor.execute(sql, [request.username])
        existing = dbCursor.fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Hash the password
        password_hash = hash_password(request.password)
        
        # Insert new user with password
        sql = """
            INSERT INTO users (username, givenname, familyname, password_hash)
            VALUES (%s, %s, %s, %s)
        """
        dbCursor.execute(sql, [
            request.username,
            request.givenname,
            request.familyname,
            password_hash
        ])
        dbConn.commit()
        
        # Get the new user's ID
        sql = "SELECT LAST_INSERT_ID()"
        dbCursor.execute(sql)
        userid = dbCursor.fetchone()[0]
        
        # Create token (new users are never admin)
        token = create_token(userid, request.username, is_admin=False)
        
        return AuthResponse(
            token=token,
            userid=userid,
            username=request.username,
            givenname=request.givenname,
            familyname=request.familyname,
            is_admin=False
        )
        
    except HTTPException:
        raise
    except Exception as err:
        logging.error(f"register(): {err}")
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


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with username and password
    """
    dbConn = None
    dbCursor = None
    
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        
        # Get user by username
        sql = """
            SELECT userid, username, givenname, familyname, password_hash, is_admin
            FROM users
            WHERE username = %s
        """
        dbCursor.execute(sql, [request.username])
        row = dbCursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        userid, username, givenname, familyname, stored_hash, is_admin = row
        
        # Check if user has a password set
        if not stored_hash:
            raise HTTPException(
                status_code=401, 
                detail="This account was created before authentication was enabled. Please contact admin to set a password."
            )
        
        # Verify password
        if hash_password(request.password) != stored_hash:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create token with admin status
        token = create_token(userid, username, is_admin=bool(is_admin))
        
        return AuthResponse(
            token=token,
            userid=userid,
            username=username,
            givenname=givenname,
            familyname=familyname,
            is_admin=bool(is_admin)
        )
        
    except HTTPException:
        raise
    except Exception as err:
        logging.error(f"login(): {err}")
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


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    """
    Get the current authenticated user's info
    """
    dbConn = None
    dbCursor = None
    
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        
        sql = """
            SELECT userid, username, givenname, familyname, is_admin
            FROM users
            WHERE userid = %s
        """
        dbCursor.execute(sql, [current_user.userid])
        row = dbCursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserInfo(
            userid=row[0],
            username=row[1],
            givenname=row[2],
            familyname=row[3],
            is_admin=bool(row[4])
        )
        
    except HTTPException:
        raise
    except Exception as err:
        logging.error(f"get_me(): {err}")
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


@router.post("/set-password")
async def set_password_for_existing_user(username: str, password: str):
    """
    Set password for existing users who don't have one
    This is an admin utility endpoint
    """
    dbConn = None
    dbCursor = None
    
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        
        password_hash = hash_password(password)
        
        sql = "UPDATE users SET password_hash = %s WHERE username = %s"
        dbCursor.execute(sql, [password_hash, username])
        dbConn.commit()
        
        if dbCursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": f"Password set for user {username}"}
        
    except HTTPException:
        raise
    except Exception as err:
        logging.error(f"set_password(): {err}")
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
