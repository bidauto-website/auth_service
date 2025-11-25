from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.base import BaseService
from database.models import Address
from database.schemas.address import AddressCreate, AddressUpdate


class AddressService(BaseService[Address, AddressCreate, AddressUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Address, session)

    async def get_by_user_id(self, user_id: int) -> Optional[Address]:
        stmt = select(Address).where(Address.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
