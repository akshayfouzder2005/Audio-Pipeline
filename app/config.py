from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    GROQ_API_KEY: str = ""
    SECRET_KEY: str = "1766e76d647a90ebe7e54f72154967aed27cd6fd2ae1427619c20921f3920337"
    API_BASE_URL: str = "https://audio-pipeline.onrender.com"
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50

    class Config:
        env_file = ".env"

settings = Settings()