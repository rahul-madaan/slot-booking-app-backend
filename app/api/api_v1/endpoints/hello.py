from fastapi import APIRouter

router = APIRouter()


# localhost:8000/hello = default
@router.get("/")
async def say_hello():
    return {"message": "Hello Rahul"}
