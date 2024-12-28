from enum import Enum

import pydantic.alias_generators
from pydantic import BaseModel


class Profile(BaseModel):
    id: str
    profile: str
    seed: str
    password: str

class Extensions(Enum):
    metamask = "metamask"
    phantom = "phantom"


class LaunchArgs(BaseModel):
    file: str
    extension: Extensions
    ext_id: str
    rounds: int = 1
    threads: int = 1

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "use_enum_values": True,
        "alias_generator": pydantic.alias_generators.to_camel
    }