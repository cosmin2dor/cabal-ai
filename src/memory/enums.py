from enum import StrEnum


class Scope(StrEnum):
    GLOBAL = "global"
    AGENT = "agent"


class Layer(StrEnum):
    HOT = "hot"
    COLD = "cold"
