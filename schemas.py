from enum import Enum

import pydantic.alias_generators
from pydantic import BaseModel, field_validator


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
    id_filter: set[str] | None = None

    @field_validator("id_filter", mode="before")
    @classmethod
    def validate_id_filter(cls, value):
        if value is None:
            return None

        if isinstance(value, set):
            tokens = [str(item).strip() for item in value]
        elif isinstance(value, (list, tuple)):
            tokens = [str(item).strip() for item in value]
        elif isinstance(value, str):
            tokens = [token.strip() for token in value.split(",")]
        else:
            raise ValueError("idFilter must be a comma-separated string")

        if not tokens or any(token == "" for token in tokens):
            raise ValueError("idFilter contains empty tokens")

        result = set()
        for token in tokens:
            if "-" in token:
                range_parts = token.split("-")
                if len(range_parts) != 2 or not range_parts[0].isdigit() or not range_parts[1].isdigit():
                    raise ValueError(
                        f"Invalid idFilter token '{token}'. Dashed tokens must be numeric ranges like 10-20."
                    )
                start = int(range_parts[0])
                end = int(range_parts[1])
                if start > end:
                    raise ValueError(
                        f"Invalid idFilter range '{token}'. Range start must be less than or equal to end."
                    )
                for item in range(start, end + 1):
                    result.add(str(item))
            else:
                result.add(token)

        return result

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "use_enum_values": True,
        "alias_generator": pydantic.alias_generators.to_camel
    }