from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import Base

if TYPE_CHECKING:
    from database.models.user import User


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    country: Mapped[str | None] = mapped_column(String(150), nullable=True)
    state: Mapped[str | None] = mapped_column(String(150), nullable=True)
    zip_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    city: Mapped[str | None] = mapped_column(String(150), nullable=True)
    address: Mapped[str | None] = mapped_column(String(150), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="address", uselist=False)
