from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from models.userModels import AccessToken
from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException
from typing import Optional
from db import refresh_tokens

auth_header = APIKeyHeader(name="Authorization")

SECRET_KEY="Qjm_q9HhLmR96FvHgWKHPahHMiYUQXdazTqemhB1sOXYPoqAiza6EAM9Em8xXN2diyoXeGzu-bEn2GS-OgATuA"

REFRESH_SECRET_KEY="ET5jhbR6ILQctavTdeE4cKKvJcco-Z9uxfNqCRnYohGYLkBTrot9Y-SDgs4TKsfV0YNrbrsZAm1CTMmleZNqFA"

def create_access_token(user_id: str):

    now = datetime.now(timezone.utc)
    issued = int(now.timestamp())
    expires = int((now + timedelta(minutes=5)).timestamp())

    #standard key names that library expects
    payload = {
        "iat": issued,
        "exp": expires,
        "sub": user_id 
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return AccessToken(token=token)


def create_refresh_token(user_id: str):

    now = datetime.now(timezone.utc)
    issued = int(now.timestamp())
    expires = int((now + timedelta(days=7)).timestamp())


    payload = {
        "type": "refresh",
        "exp": expires,
        "sub": user_id 
    }

    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm="HS256")



def get_current_user_id(token: str = Depends(auth_header)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})




def refresh_access_token(refresh_token: str):

    session = refresh_tokens.find_one({
        "refresh_token": refresh_token,
        "revoked": False
    })

    if not session:
        raise HTTPException(status_code=401, detail="Session revoked or expired")

    try:
        payload = jwt.decode(
            refresh_token,
            REFRESH_SECRET_KEY,
            algorithms=["HS256"]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")

        new_access_token = create_access_token(user_id)

        return new_access_token

    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid or expired refresh token")