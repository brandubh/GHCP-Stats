from pydantic import BaseSettings

class Settings(BaseSettings):
    env: str = "local"
    sqlite_db: str = "metrics.db"
    cosmos_endpoint: str = ""
    cosmos_key: str = ""
    cosmos_db_name: str = "ghcpstats"
    github_token: str = ""
    org_list: str = "org1,org2"

    class Config:
        env_file = ".env"

settings = Settings()
