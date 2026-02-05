from fastapi import APIRouter, HTTPException
from models.userModels import AddUser, UserPublic, User, AddUserResponse
from db import db, to_object_id, serialize_doc

user_router = APIRouter()
users = db["users"]


@user_router.post("/login" , response_model=UserPublic)
def login():
    return {"ok" : "goober"}


@user_router.post("/signup", response_model=AddUserResponse)
def add_user(user: AddUser):

    user_dict = user.model_dump()
 
    if users.find_one({"email" : user.email}):
        raise HTTPException(status_code=500, detail="Email already exists")
    
    elif user_dict["password"] != user_dict["confirm_password"]:
        raise HTTPException(status_code=401, detail="Password and password confirmation differ. Please try to use our front-end for making HTTP requests for more convinient usage.")
    users.insert_one(user_dict)
    return AddUserResponse(password= user_dict["password"], display= user_dict["display"], email= user_dict["email"], msg="Account successfully created", code=200)

@user_router.put("/update", response_model=UserPublic)
def update_user(user: User):
    pass
    

