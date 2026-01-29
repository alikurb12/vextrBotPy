from pydantic_settings import BaseSettings
from pydantic import model_validator

TARIFFS = {
    '1month': {'days': 30, 'price': 500, 'name': '1 месяц', 'currency': 'RUB'},
    '3months': {'days': 90, 'price': 1200, 'name': '3 месяца', 'currency': 'RUB'},
}

class Settings(BaseSettings):
    
    YOOMONEY_ACCESS_TOKEN : str
    YOOMONEY_RECEIVER : int

    BOT_TOKEN : str
    CRYPTO_BOT_TOKEN : str
    GROUP_ID : str
    MODERATOR_GROUP_ID : str
    SUPPORT_CONTACT : str

    DB_HOST : str
    DB_NAME : str
    DB_USER : str
    DB_PASS : str
    DB_PORT : str
    
    DATABASE_URL : str | None = None

    @model_validator(mode="after")
    def get_database_url(self):
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return self

    class Config:
        env_file = '.env'

settings = Settings()