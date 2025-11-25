from types import SimpleNamespace

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.address import AddressService
from dependencies.security import require_all_permissions, get_current_user
from config import Permissions
from tests.factories.token_session_user_factories import UserFactory


@pytest.fixture
def address_urls(get_app):
    class URLs:
        def __init__(self, app):
            self.app = app

        def me(self):
            return self.app.url_path_for("get_my_address")

        def upsert(self):
            return self.app.url_path_for("update_address")

        def admin_get(self, user_uuid: str):
            return self.app.url_path_for("get_address_by_user_uuid", user_uuid=user_uuid)

    return URLs(get_app)


@pytest.fixture(autouse=True)
def override_permissions_and_user(get_app):
    current_user = SimpleNamespace(id="test-user-uuid")

    async def _override_get_current_user():
        return current_user

    def _override_require_all_permissions(*_, **__):
        return lambda: current_user

    get_app.dependency_overrides[require_all_permissions] = _override_require_all_permissions
    get_app.dependency_overrides[require_all_permissions(Permissions.USERS_WRITE_OWN)] = _override_require_all_permissions
    get_app.dependency_overrides[require_all_permissions(Permissions.USERS_READ_OWN)] = _override_require_all_permissions
    get_app.dependency_overrides[require_all_permissions(Permissions.USERS_READ_ALL)] = _override_require_all_permissions
    get_app.dependency_overrides[get_current_user] = _override_get_current_user

    return current_user


@pytest.mark.asyncio
class TestAddressEndpoints:
    async def test_upsert_creates_when_missing(self, client: AsyncClient, db: AsyncSession, address_urls):
        user = UserFactory.build(uuid_key="test-user-uuid")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        payload = {
            "country": "USA",
            "state": "CA",
            "zip_code": 90210,
            "city": "Beverly Hills",
            "address": "123 Palm Dr",
        }

        response = await client.put(address_urls.upsert(), json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["country"] == payload["country"]
        assert data["user_id"] == user.id

        address_service = AddressService(db)
        stored = await address_service.get_by_user_id(user.id)
        assert stored is not None
        assert stored.country == payload["country"]

    async def test_get_me_creates_if_missing(self, client: AsyncClient, db: AsyncSession, address_urls):
        user = UserFactory.build(uuid_key="test-user-uuid")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        response = await client.get(address_urls.me())
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id

        address_service = AddressService(db)
        stored = await address_service.get_by_user_id(user.id)
        assert stored is not None

    async def test_admin_get_creates_if_missing(self, client: AsyncClient, db: AsyncSession, address_urls):
        user = UserFactory.build(uuid_key="admin-target-uuid")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        response = await client.get(address_urls.admin_get(user.uuid_key))
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id

        address_service = AddressService(db)
        stored = await address_service.get_by_user_id(user.id)
        assert stored is not None
