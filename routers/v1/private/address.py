from fastapi import APIRouter, Depends, Body, Path
from rfc9457 import NotFoundProblem, BadRequestProblem
from sqlalchemy.ext.asyncio import AsyncSession

from config import Permissions
from database.crud.address import AddressService
from database.crud.user import UserService
from database.db.session import get_async_db
from database.models import Address, User
from database.schemas.address import AddressCreate, AddressUpdate, AddressRead
from dependencies.security import JWTUser, require_all_permissions


address_router = APIRouter(prefix="/address")


async def _get_user_by_uuid(user_service: UserService, user_uuid: str)-> User:
    user = await user_service.get_user_by_uuid(user_uuid)
    if not user:
        raise NotFoundProblem(detail="User not found")
    return user


async def _get_or_create_address(address_service: AddressService, user_id: int)-> Address:
    address = await address_service.get_by_user_id(user_id)
    if address:
        return address
    return await address_service.create(AddressCreate(user_id=user_id))


@address_router.put(
    "",
    response_model=AddressRead,
    description="Create or update address for current user",
)
async def update_address(
    address_update: AddressUpdate = Body(...),
    current_user: JWTUser = Depends(require_all_permissions(Permissions.USERS_WRITE_OWN)),
    db: AsyncSession = Depends(get_async_db),
):
    user_service = UserService(db)
    db_user = await _get_user_by_uuid(user_service, current_user.id)

    address_service = AddressService(db)
    if address_update.user_id is not None and address_update.user_id != db_user.id:
        raise BadRequestProblem(detail="Cannot move address to a different user")

    existing_address = await address_service.get_by_user_id(db_user.id)

    payload = address_update.model_dump(exclude_unset=True, exclude={"user_id"})
    payload["user_id"] = db_user.id

    if existing_address:
        updated = await address_service.update(existing_address.id, AddressUpdate(**payload))
        return updated

    created = await address_service.create(AddressCreate(**payload))
    return created


@address_router.get(
    "/me",
    response_model=AddressRead,
    description="Get address for current user",
)
async def get_my_address(
    current_user: JWTUser = Depends(require_all_permissions(Permissions.USERS_READ_OWN)),
    db: AsyncSession = Depends(get_async_db),
):
    user_service = UserService(db)
    db_user = await _get_user_by_uuid(user_service, current_user.id)

    address_service = AddressService(db)
    return await _get_or_create_address(address_service, db_user.id)


@address_router.get(
    "/user/{user_uuid}",
    response_model=AddressRead,
    description="Get address by user UUID (admin)",
    dependencies=[Depends(require_all_permissions(Permissions.USERS_READ_ALL))],
)
async def get_address_by_user_uuid(
    user_uuid: str = Path(..., description="User UUID"),
    db: AsyncSession = Depends(get_async_db),
):
    user_service = UserService(db)
    user = await _get_user_by_uuid(user_service, user_uuid)

    address_service = AddressService(db)
    return await _get_or_create_address(address_service, user.id)
