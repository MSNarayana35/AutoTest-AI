from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import base64
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# ==================== TOKEN ENCRYPTION ====================

def _get_encryption_key() -> bytes:
    """Get or generate encryption key from settings"""
    # Use SECRET_KEY as basis for Fernet key
    # Fernet requires a 32-byte base64-encoded key
    key_material = settings.SECRET_KEY.encode()
    # Pad or truncate to 32 bytes
    key_material = key_material[:32].ljust(32, b'0')
    return base64.urlsafe_b64encode(key_material)


def encrypt_token(token: str) -> str:
    """
    Encrypt a sensitive token (like GitHub token) for storage
    
    Args:
        token: Plain text token
        
    Returns:
        Encrypted token as string
    """
    try:
        fernet = Fernet(_get_encryption_key())
        encrypted = fernet.encrypt(token.encode())
        return encrypted.decode()
    except Exception as e:
        raise ValueError(f"Failed to encrypt token: {str(e)}")


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt a token from storage
    
    Args:
        encrypted_token: Encrypted token string
        
    Returns:
        Decrypted plain text token
    """
    try:
        fernet = Fernet(_get_encryption_key())
        decrypted = fernet.decrypt(encrypted_token.encode())
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt token: {str(e)}")
