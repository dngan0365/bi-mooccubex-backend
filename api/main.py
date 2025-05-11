from fastapi import FastAPI, Depends
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="bi-mooccubex-backend",
    description="Backend for MOOC-Cubex",
    version="0.1.0",
)
# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers
# app.include_router(auth_router, prefix="/auth", tags=["auth"])
# app.include_router(bi_overview, prefix="/overview", tags=["overview"])
# app.include_router(bi_data_quality, prefix="/quality", tags=["quality"])
# app.include_router(bi_data_mining, prefix="/mining", tags=["mining"])
# app.include_router(bi_course, prefix="/course", tags=["course"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

handler = Mangum(app=app)