from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    bot_token: str
    public_base_url: str = "http://localhost:8000"
    admin_telegram_ids: str = ""
    api_internal_url: str = "http://api:8000"

    @property
    def admin_ids(self) -> List[int]:
        ids=[]
        for p in (self.admin_telegram_ids or "").split(","):
            p=p.strip()
            if p.isdigit():
                ids.append(int(p))
        return ids

settings = Settings()
