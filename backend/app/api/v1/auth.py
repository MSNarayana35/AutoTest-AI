from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import secrets
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.models.platform import ApiKey, Notification
from app.models.user import User, UserRole

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ProfileUpdate(BaseModel):
    full_name: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class ApiKeyCreate(BaseModel):
    name: str

class ApiKeyCreated(BaseModel):
    id: int
    name: str
    key_prefix: str
    api_key: str

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str

    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=UserRole.QA_ENGINEER
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(
    profile: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.full_name = profile.full_name
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/forgot-password")
def forgot_password(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        notification = Notification(
            user_id=user.id,
            channel="email",
            title="Password reset requested",
            message="Password reset flow was requested for this account.",
        )
        db.add(notification)
        db.commit()
    return {"status": "accepted"}

@router.post("/verify-email")
def verify_email(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.is_verified = True
    db.commit()
    return {"status": "verified"}

@router.get("/oauth/{provider}")
def oauth_provider(provider: str):
    if provider not in {"google", "github"}:
        raise HTTPException(status_code=404, detail="OAuth provider not supported")
    return {
        "provider": provider,
        "status": "configuration_required",
        "message": "Set provider client ID, secret, and callback URL before enabling OAuth login.",
    }

@router.post("/api-keys", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_key = f"atai_{secrets.token_urlsafe(32)}"
    key = ApiKey(
        user_id=current_user.id,
        name=payload.name,
        key_prefix=raw_key[:12],
        hashed_key=get_password_hash(raw_key),
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return {
        "id": key.id,
        "name": key.name,
        "key_prefix": key.key_prefix,
        "api_key": raw_key,
    }

@router.get("/api-keys", response_model=list[ApiKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
