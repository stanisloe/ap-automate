from pydantic import BaseModel, field_validator


class Profile(BaseModel):
    id: str
    profile: str
    seed: str
    password: str

class LaunchArgs(BaseModel):
    profiles_path: str
    rounds_count: int
    threads_count: int
    metamask_id: str