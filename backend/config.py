from pydantic_settings import BaseSettings, SettingsConfigDict


class settings(BaseSettings):
    DB_URL: str
    model_config = SettingsConfigDict(
        env_file= ".env",
        extra= "ignore"
    )
    
    
config = settings()