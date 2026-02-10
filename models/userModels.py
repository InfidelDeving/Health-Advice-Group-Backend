from pydantic import BaseModel, Field
from typing import Optional

class BaseResponseModel(BaseModel):
    msg: str

class UserHealth(BaseModel):
    height: str
    weight: str
    birthdate: str
    medical_conditions: list
 
class SubmitTrackingData(BaseModel):
    email: str
    date: str
    input: str 


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
    id: str
    email: str
    display: str

class AccessToken(BaseModel): 
    token: str 
    token_type: str = "bearer"

class LoginUser(BaseModel):
    email: str
    password: str

class LoginUserResponse(BaseModel):
    id: str
    email: str
    access_token: AccessToken
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str

