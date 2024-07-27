#Libraries Required
from fastapi import FastAPI
from routes.cars import router as cars_router
from routes.bikes import router as bikes_router
from routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


# FastAPI instance
app = FastAPI()


# CORS settings
origins = ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Vehicle Store API"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(bikes_router, prefix="/bikes", tags=["bikes"])
app.include_router(cars_router, prefix="/cars", tags=["cars"])



