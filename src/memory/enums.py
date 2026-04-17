from enum import Enum


class Scope(str, Enum):
    GLOBAL = "global"
    AGENT = "agent"


class Layer(str, Enum):
    HOT = "hot"
    COLD = "cold"
