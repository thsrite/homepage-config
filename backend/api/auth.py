from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from backend.core.auth import authenticate_user, create_access_token, get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInfo(BaseModel):
    username: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": request.username})
    return LoginResponse(access_token=access_token)

@router.get("/verify", response_model=UserInfo)
async def verify(current_user: dict = Depends(get_current_user)):
    """Verify token and get current user info"""
    return UserInfo(username=current_user["username"])

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout endpoint (client should remove token)"""
    return {"message": "Logged out successfully"}
