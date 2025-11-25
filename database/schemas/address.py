from typing import Optional

from pydantic import BaseModel, ConfigDict


class AddressCreate(BaseModel):
    user_id: Optional[int] = None
    country: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[int] = None
    city: Optional[str] = None
    address: Optional[str] = None


class AddressUpdate(BaseModel):
    user_id: Optional[int] = None
    country: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[int] = None
    city: Optional[str] = None
    address: Optional[str] = None


class AddressRead(AddressCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
