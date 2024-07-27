import motor.motor_asyncio

# MongoDB connection details
MONGO_DETAILS = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.vehicle_store

users_collection = database.get_collection("users")
cars_collection = database.get_collection("cars")
bikes_collection = database.get_collection("bikes")
orders_collection = database.get_collection("orders") 
