from pydantic import BaseModel

class Profile(BaseModel):
    id: str
    profile: str
    seed: str
    password: str
