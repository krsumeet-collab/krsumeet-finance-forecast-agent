"""Application configuration loader."""
import os
from pathlib import Path
from typing import Dict, Any
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    environment: str = Field(default="prod", alias="ENVIRONMENT")
    gcp_project_id: str = Field(default="corp-finance-gcp", alias="GCP_PROJECT_ID")
    gcp_region: str = Field(default="europe-west1", alias="GCP_REGION")
    bigquery_dataset: str = Field(default="finance_analytics", alias="BIGQUERY_DATASET")
    otel_service_name: str = Field(default="finance-forecast-agent", alias="OTEL_SERVICE_NAME")
    port: int = Field(default=8080, alias="PORT")

    # Path to YAML configs
    config_dir: Path = Path(__file__).resolve().parent.parent / "configs"

    def load_yaml(self, filename: str) -> Dict[str, Any]:
        filepath = self.config_dir / filename
        if not filepath.exists():
            return {}
        with open(filepath, "r") as f:
            return yaml.safe_load(f) or {}

    @property
    def agent_config(self) -> Dict[str, Any]:
        return self.load_yaml("agent_config.yaml")

    @property
    def prompts(self) -> Dict[str, Any]:
        return self.load_yaml("prompts.yaml")


settings = Settings()
