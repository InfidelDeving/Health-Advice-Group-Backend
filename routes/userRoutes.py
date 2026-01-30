from fastapi import APIRouter, HTTPException
from models.userModels import AddUser, UserPublic, User
from db import db, to_object_id, serialize_doc

user_router = APIRouter()
users = db["users"]


@user_router.post("/login" , response_model=UserPublic)
def login():
    return {"ok" : "goober"}


@user_router.post("/signup", response_model=UserPublic)
def add_user(user: AddUser):
    if users.find_one({"email" == user.email}):
        raise HTTPException(status_code=500, detail="Recourse already exists")
    user_dict = user.model_dump()
    if user_dict["password"] == user_dict["confirm_password"]:
        raise HTTPException(status_code=401, detail="Password and password confirmation differ. Please try to use our front-end for making HTTP requests for more convinient usage.")
    