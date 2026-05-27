from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.schemas.user import RegisterRequest, LoginRequest, AuthResponse
from src.services.user_service import create_user, authenticate_user, get_user_by_token, get_user_by_username

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    if get_user_by_username(db, data.username) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = create_user(db, data.username, data.password)
    return AuthResponse(username=user.username, token=user.auth_token)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return AuthResponse(username=user.username, token=user.auth_token)


@router.get("/me", response_model=AuthResponse)
def me(authorization: str = Header(None, alias="Authorization"), db: Session = Depends(get_db)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid")
    token = authorization.split(" ", 1)[1].strip()
    user = get_user_by_token(db, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return AuthResponse(username=user.username, token=user.auth_token)
