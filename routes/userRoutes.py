from fastapi import APIRouter, HTTPException, Depends
from models.userModels import AddUser, AddUserResponse, BaseResponseModel, UpdateUser, LoginUserResponse, LoginUser, RefreshTokenRequest
from db import db, to_object_id, serialize_doc, refresh_tokens
from security import hash_password, verify_password
from auth import create_access_token, get_current_user_id, create_refresh_token, refresh_access_token
from datetime import datetime, timedelta, timezone


user_router = APIRouter()
users = db["users"]

def validate_password(password):
    SPECIAL_CHAR= ["!", "£", "$", "%", "^", "&", "*", "@"]
    special_present=0
    for i in SPECIAL_CHAR:
        if i in password:
            special_present=1
            break
        
    if len(password) >= 8 and special_present == 1:
        pass
    else: raise HTTPException(status_code=406, detail="Password does not meet requirements")

@user_router.post("/signup", response_model=AddUserResponse)
def add_user(user: AddUser):

    user_dict = user.model_dump()
 
    if users.find_one({"email" : user.email}):
        raise HTTPException(status_code=500, detail="Email already exists")
    
    validate_password(user_dict["password"])

    if user_dict["password"] != user_dict["confirm_password"]:
        raise HTTPException(status_code=401, detail="Password and password confirmation differ. Please try to use our front-end for making HTTP requests for more convinient usage.")
    else: user_dict.pop("confirm_password", None)
    
    user_dict["password"] = hash_password(user_dict["password"])

    user_result  = users.insert_one(user_dict)
    id = str(user_result.inserted_id)
    return AddUserResponse(id=id, display= user_dict["display"], email= user_dict["email"], msg="Account successfully created")


@user_router.delete("/delete/{id}", response_model=BaseResponseModel)
def delete_user(id: str):
    object_id = to_object_id(id)
    result = users.delete_one({"_id" : object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return BaseResponseModel(msg="Account successfully deleted")


@user_router.patch("/update/{id}")
def update_user(updates: UpdateUser, id: str = Depends(get_current_user_id)):
    object_id = to_object_id(id)
    if not users.find_one({"_id": object_id}):
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = updates.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=406, detail="No data to update")
    
    if update_data.get("password"):
        validate_password(update_data["password"])
        update_data["password"] = hash_password(update_data["password"])

    result = users.update_one({"_id": object_id}, {"$set": update_data})

    updated_doc = users.find_one({"_id": object_id})
    return {
        "msg": "Account updated successfully",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "item": serialize_doc(updated_doc)
    }


@user_router.post("/login", response_model=LoginUserResponse)
def login_user(login: LoginUser):
    user = users.find_one({"email": login.email})
    if not user or not verify_password(login.password ,user["password"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    
    access_token = create_access_token(str(user["_id"]))
    refresh_token = create_refresh_token(str(user["_id"]))

    refresh_tokens.insert_one({
        "user_id:": user["_id"],
        "refresh_token": refresh_token,
        "issued_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "revoked": False
        })

    return LoginUserResponse(
        id=str(user["_id"]),
        email=user["email"],
        access_token=access_token,
        refresh_token=refresh_token
        )


@user_router.post("/refresh")
def refresh_token_route(data: RefreshTokenRequest):
    return refresh_access_token(data.refresh_token)


@user_router.post("/logout")
def logout(data: RefreshTokenRequest):
    refresh_tokens.update_one(
        {"refresh_token": data.refresh_token},
        {"$set": {"revoked": True}}
    )
    return BaseResponseModel(msg="Logged out")