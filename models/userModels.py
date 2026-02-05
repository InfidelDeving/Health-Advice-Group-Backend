from pydantic import BaseModel, Field
from typing import Optional

class BaseResponseModel(BaseModel):
    msg: str
    code: int

class UserHealth(BaseModel):
    height: str
    weight: str
    birthdate: str
    medical_conditions: list
 
class SubmitTrackingData(BaseModel):
    email: str
    date: str
    input: str 


class User(BaseModel):
    display: str
    email: str
    password: str
    health: UserHealth
    tracking_data: dict # object/dictionary key:value == date:input

class UserPublic(BaseModel):
    display: str
    email: str
    health: UserHealth
    tracking_data: dict # object/dictionary key:value == date:input

class AddUser(BaseModel):
    email: str
    display: str
    password: str
    confirm_password: str
    

class UpdateUser(BaseModel):
    display: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    health: Optional[UserHealth] = None
    tracking_data: Optional[dict] = None # object/dictionary key:value == date:input

class AddUserResponse(BaseResponseModel):
    email: str
    display: str
    password: str