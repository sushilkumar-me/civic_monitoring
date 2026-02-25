from pydantic import BaseModel

class IssueCreate(BaseModel):
    latitude: float
    longitude: float
