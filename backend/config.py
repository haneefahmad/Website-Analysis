import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PAGESPEED_API_KEY: str = os.getenv("PAGESPEED_API_KEY", "")
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./audits.db")
    SCREENSHOTS_DIR: str = os.path.join(os.path.dirname(__file__), "screenshots")

    class Config:
        env_file = ".env"

settings = Settings()
