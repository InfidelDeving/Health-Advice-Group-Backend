from fastapi import APIRouter, HTTPException
from models.userModels import AddUser, UserPublic, AddUserResponse, BaseResponseModel, UpdateUser
from db import db, to_object_id, serialize_doc
from security import hash_password, verify_password

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


@user_router.post("/login" , response_model=UserPublic)
def login():
    return {"ok" : "goober"}


@user_router.post("/signup", response_model=AddUserResponse)
def add_user(user: AddUser):

    user_dict = user.model_dump()
 
    if users.find_one({"email" : user.email}):
        raise HTTPException(status_code=500, detail="Email already exists")
    
    validate_password(user_dict["password"])

    if user_dict["password"] != user_dict["confirm_password"]:
        raise HTTPException(status_code=401, detail="Password and password confirmation differ. Please try to use our front-end for making HTTP requests for more convinient usage.")
    
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
def update_user(id: str, updates: UpdateUser):
    object_id = to_object_id(id)
    print("id: ", object_id)
    if not users.find_one({"_id": object_id}):
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = updates.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=406, detail="No data to update")
    
    if update_data["password"]:
        validate_password(update_data["password"])
        update_data["password"] = hash_password(update_data["password"])

    result = users.update_one({"_id": object_id}, {"$set": update_data})

    updated_doc = users.find_one({"_id": object_id})
    print(updated_doc)
    return {
        "msg": "Account updated successfully",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "item": serialize_doc(updated_doc)
    }


@user_router.get("/login")
def login_user(email: str ,password: str):
    if not users.find_one({"email" : email}):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    user = users.find_one({"email": email})
    if user.password == password:
        return user

    