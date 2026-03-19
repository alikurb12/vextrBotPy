from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
import secrets
from config.config import settings
import logging

logger = logging.getLogger(__name__)

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request):
        try:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")

            if (username and password and
                secrets.compare_digest(username, settings.ADMIN_USERNAME) and
                secrets.compare_digest(password, settings.ADMIN_PASSWORD)):

                request.session.update({"token" : username})
                logger.info(f"Успешный вход в админку: {username}")
                return True
            else:
                logger.warning(f"Неудачная попытка входа в админку: {username}")
                return False
        
        except Exception as e:
            logger.error(f"Ошибка при попытке входа в админку: {e}")
            return False
    
    async def logout(self, request: Request):
        request.session.clear()
        logger.info("Пользователь вышел из админки")
        return True
    
    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        
        if not token:
            logger.debug("No token in session")
            return False
        if token == settings.ADMIN_USERNAME:
            logger.debug(f"User authenticated: {token}")
            return True
        else:
            logger.warning(f"Invalid token: {token}")
            return False