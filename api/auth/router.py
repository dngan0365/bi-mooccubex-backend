from fastapi import APIRouter, HTTPException,  Header, Depends
from api.models.user import UserCreate, UserLogin, UserInDB
from api.auth.utils import hash_password, verify_password, create_access_token, decode_token
from api.db.dynamodb import create_user, get_user_by_email

router = APIRouter()

@router.post("/signup")
async def signup(user: UserCreate):
    try:
        # Check if user already exists
        existing = get_user_by_email(user.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password
        hashed = hash_password(user.password)
        
        # Create user in DB
        user_in_db = UserInDB(username=user.username, email=user.email, hashed_password=hashed)
        create_user(user_in_db)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.email})
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/signin")
async def signin(user_data: UserLogin):
    try:
        user = get_user_by_email(user_data.email)
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        # Log error to console (will appear in CloudWatch logs)
        print("Error during /signin:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/token")
def get_user_info(authorization: str = Header(...)):
    token = authorization.split(" ")[1] if " " in authorization else authorization
    try:
        token_data = decode_token(token)
        user = get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": str(user.id), "username": user.username, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))