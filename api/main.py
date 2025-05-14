from fastapi import FastAPI, Depends
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
from api.auth.router import router as auth_router

app = FastAPI(
    title="bi-mooccubex-backend",
    description="Backend for MOOC-Cubex",
    version="0.1.0",
)
# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://bi-moocubex-frontend.vercel.app/"],  # exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

handler = Mangum(app=app)