from sqlalchemy import String, BigInteger, Boolean, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from typing import List

from os import environ

db_url = environ.get('DB_URL')
db_admin = environ.get('DB_ADMIN')
db_password = environ.get('DB_PASSWORD')
db_name = environ.get('DB_NAME')

engine = create_async_engine(
    url=f'postgresql+asyncpg://{db_admin}:{db_password}@{db_url}:5432/{db_name}',
    echo=True
)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


association_table = Table(
    "user_in_role",
    Base.metadata,
    Column("role_id", ForeignKey("role.id"), primary_key=True),
    Column("user_id", ForeignKey("user.tg_id"), primary_key=True),
)


class Role(Base):
    __tablename__ = 'role'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(12))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    users: Mapped[List["User"]] = relationship(secondary=association_table, back_populates="roles")


class User(Base):
    __tablename__ = 'user'

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(15))
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    roles: Mapped[List["Role"]] = relationship(secondary=association_table, back_populates="users")


async def run_db_conn():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
