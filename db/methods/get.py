from db.models import *
from sqlalchemy import select, exc


async def get_user(user_id: BigInteger) -> tuple | None:
    """
    Получает данные пользователя и значение админ или нет
    :param user_id:
    :return:
    """
    async with async_session() as session:
        try:
            result = await session.execute(select(User, Role.is_admin).join(User.roles).where(User.tg_id == user_id))
            return result.one()
        except exc.NoResultFound:
            return None


async def get_user_role(user_id: BigInteger) -> List | None:
    """
    Получает список ролей пользователя
    :param user_id:
    :return:
    """
    async with async_session() as session:
        try:
            result = await session.execute(select(Role).join(Role.users).where(User.tg_id == user_id))
            return result.scalars().all()
        except exc.NoResultFound:
            return None
