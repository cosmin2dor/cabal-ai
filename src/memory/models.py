from sqlmodel import Field
from .enums import Scope, Layer
from typing import Optional

from core.models import Base


class Memory(Base, table=True):
    agent: Optional[str] = Field(default=None, index=True, nullable=True)
    scope: Scope = Field(index=True, nullable=False)
    layer: Layer = Field(index=True, nullable=False)
    content: str = Field(nullable=False)
