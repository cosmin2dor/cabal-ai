from sqlmodel import Field

from core.models import Base

from .enums import Layer, Scope


class Memory(Base, table=True):
    agent: str | None = Field(default=None, index=True, nullable=True)
    scope: Scope = Field(index=True, nullable=False)
    layer: Layer = Field(index=True, nullable=False)
    content: str = Field(nullable=False)
