from pydantic import BaseModel

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
    encryption_key: bytes | None = None