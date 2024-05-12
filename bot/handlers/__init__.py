from aiogram import Router

from .admin import admin
from .common import common
from .user import user

router = Router()
router.include_routers(admin.router, common.router, user.router)
