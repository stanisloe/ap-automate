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
    profiles: str = "./profiles.csv"
    rounds: int = 1
    threads: int = 2
    extension: Extensions

    metamask_id: str = "fbkaeljfgkiknokhhdiomplofllnoele"
    phantom_id: str = "bfnaelmomeimhlpmgjnjophhpkkoljpa"

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "use_enum_values": True,
        "alias_generator": pydantic.alias_generators.to_camel
    }