from utils import verify_password,Depends,get_user,HTTPException,create_access_token,create_user,User,List,get_current_active_admin
from fastapi import APIRouter
from Database.connection import cars_collection
from config.config import ACCESS_TOKEN_EXPIRE_MINUTES
from models.models import Car,Order
from fastapi import APIRouter, Depends, HTTPException
from models.models import User
from Database.connection import cars_collection,orders_collection
from typing import List
from utils import get_current_active_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()

# Regular user endpoints
@router.get("/cars/", response_model=List[dict])  # Use `dict` as response model
async def get_cars():
    try:
        cars = await cars_collection.find().to_list(length=100)
        return [{"make": car["make"], "model": car["model"], "year": car["year"], "price": car["price"]} for car in cars]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@router.post("/cars/", response_model=Car)
async def create_car(car: Car, current_user: User = Depends(get_current_active_admin)):
    new_car = dict(car)
    result = await cars_collection.insert_one(new_car)
    return {**car.dict(), "id": str(result.inserted_id)}



@router.put("/cars/{car_id}", response_model=Car)
async def update_car(car_id: str, car: Car, current_user: User = Depends(get_current_active_admin)):
    try:
        result = await cars_collection.update_one({"_id": ObjectId(car_id)}, {"$set": dict(car)})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Car not found")
        return {**car.dict(), "id": car_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    


@router.delete("/cars/{car_id}", response_model=dict)
async def delete_car(car_id: str, current_user: User = Depends(get_current_active_admin)):
    try:
        result = await cars_collection.delete_one({"_id": ObjectId(car_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Car not found")
        return {"message": "Car deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    


# Admin endpoints (protected with authentication)
@router.get("/admin/cars/", response_model=List[Car])
async def get_admin_cars(current_user: User = Depends(get_current_active_admin)):
    try:
        cars = await cars_collection.find().to_list(length=100)
        return [{"id": str(car["_id"]), "make": car["make"], "model": car["model"], "year": car["year"], "price": car["price"]} for car in cars]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

# Buy a car
@router.post("/{bike_id}/buy", response_model=Order)
async def buy_bike(bike_id: str):
    # Convert the bike_id to ObjectId
    try:
        bike_obj_id = ObjectId(bike_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid bike_id: {e}")

    # Find the bike by its ObjectId
    bike = await cars_collection.find_one({"_id": bike_obj_id})
    if bike is None:
        raise HTTPException(status_code=404, detail="Bike not found")

    # Create the order
    order = Order(
        id=str(ObjectId()),  # Generate a new unique ObjectId
        bike_id=bike_id,
        timestamp=datetime.utcnow()
    )

    result = await orders_collection.insert_one(order.dict(by_alias=True))
    new_order = await orders_collection.find_one({"_id": result.inserted_id})

    # Delete the bike from the inventory
    await cars_collection.delete_one({"_id": bike_obj_id})

    return new_order