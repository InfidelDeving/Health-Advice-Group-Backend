from bson import ObjectId
from fastapi import HTTPException
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["users"]

def to_object_id(id_str: str) -> ObjectId:

    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


# This is also useful so we wont have to manually convert the id every time when we want the entire document
def serialize_doc(doc: dict) -> dict:
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    return doc
