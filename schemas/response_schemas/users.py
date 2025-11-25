from pydantic import BaseModel

from database.schemas.address import AddressRead
from database.schemas.role import RoleReadWithPermissions
from database.schemas.user import UserRead


class FullUserOut(UserRead):
    roles: list[RoleReadWithPermissions] = []


class UserWithRolePermission(UserRead):
    roles: list[str] = []
    permissions: list[str] = []


class Plan(BaseModel):
    max_bid_one_time: int
    name: str
    description: str
    bid_power: int
    price: int


class UserAccount(BaseModel):
    balance: int | None = None
    plan: Plan | None = None


class DetailedUser(UserWithRolePermission):
    account: UserAccount | None = None
    address: AddressRead | None = None
