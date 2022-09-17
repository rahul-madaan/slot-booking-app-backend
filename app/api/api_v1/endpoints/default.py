from fastapi import APIRouter

router = APIRouter()


# localhost:8000/api/v1 = default
@router.get("/")
async def say_hello():
    return {"message": "Hello World",
            "availableSlots": [12, 13, 14, 0, 16, 17, 18, 19]}
