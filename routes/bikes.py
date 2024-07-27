from utils import verify_password,Depends,get_user,HTTPException,status,create_access_token,timedelta,create_user,User,List,get_current_active_admin,get_current_user
from fastapi import APIRouter
from Database.connection import bikes_collection,orders_collection
from config.config import ACCESS_TOKEN_EXPIRE_MINUTES
from models.models import Bike,Order
from datetime import datetime
from bson import ObjectId

router = APIRouter()

#get the list of bikes for user
@router.get("/bikes/", response_model=List[dict])  
async def get_bikes():
    try:
        bikes = await bikes_collection.find().to_list(length=100)
        return [{"make": bike["make"], "model": bike["model"], "year": bike["year"], "price": bike["price"]} for bike in bikes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



# Creates bike only valid for admin
@router.post("/bikes/", response_model=Bike)
async def create_bike(bike: Bike, current_user: User = Depends(get_current_active_admin)):
    new_bike = dict(bike)
    result = await bikes_collection.insert_one(new_bike)
    return {**bike.dict(), "id": str(result.inserted_id)}



#Update information of bikes only valid for admin
@router.put("/bikes/{bike_id}", response_model=Bike)
async def update_bike(bike_id: str, bike: Bike, current_user: User = Depends(get_current_active_admin)):
    try:
        result = await bikes_collection.update_one({"_id": ObjectId(bike_id)}, {"$set": dict(bike)})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Bike not found")
        return {**bike.dict(), "id": bike_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



#Deletes the bike using the bike id only for admin
@router.delete("/bikes/{bike_id}", response_model=dict)
async def delete_bike(bike_id: str, current_user: User = Depends(get_current_active_admin)):
    try:
        result = await bikes_collection.delete_one({"_id": ObjectId(bike_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Bike not found")
        return {"message": "Bike deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    


#Gets the list of bikes for admin(alsop displays id)
@router.get("/admin/bikes/", response_model=List[Bike])
async def get_admin_bikes(current_user: User = Depends(get_current_active_admin)):
    try:
        bikes = await bikes_collection.find().to_list(length=100)
        return [{"id": str(bike["_id"]), "make": bike["make"], "model": bike["model"], "year": bike["year"], "price": bike["price"]} for bike in bikes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    


# Buy a bike
@router.post("/{bike_id}/buy", response_model=Order)
async def buy_bike(bike_id: str):
    # Convert the bike_id to ObjectId
    try:
        bike_obj_id = ObjectId(bike_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid bike_id: {e}")

    # Find the bike by its ObjectId
    bike = await bikes_collection.find_one({"_id": bike_obj_id})
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
    await bikes_collection.delete_one({"_id": bike_obj_id})

    return new_order