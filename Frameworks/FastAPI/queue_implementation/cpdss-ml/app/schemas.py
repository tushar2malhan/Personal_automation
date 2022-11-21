from typing import List, Optional

from pydantic import BaseModel


class PumpInfo(BaseModel):
    Port: str
    Vessel: str
    MaxRate: float

    class Config:
        orm_mode = True


class CargoInfo(BaseModel):
    Port: str
    Cargo: str
    Year: int
    Month: int
    Date: int

    class Config:
        orm_mode = True


class InstructionsInfo(BaseModel):
    Port: str
    Cargoes: List[str]
    Berth: str
    Connection: str
    Operation: str

    class Config:
        orm_mode = True


class NominationInfo(BaseModel):
    Vessel: str
    Vol: List[float]
    API: List[float]
    LoadingPortsCount: int

    class Config:
        orm_mode = True


class BallastInfo(BaseModel):
    PrevPort: List[dict]
    CurrPort: List[dict]
    NextPort: List[dict]

    # Vol: List[float]
    # API: List[float]
    # MaxTol: List[float]
    # MinTol: List[float]
    # Onhand: float

    class Config:
        orm_mode = True
