"""Pytest test configuration and fixtures."""
import sys
from pathlib import Path
import pytest

# Ensure src is in python path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.models.schemas import ForecastGenerateRequest, RegionEnum


@pytest.fixture
def sample_emea_request() -> ForecastGenerateRequest:
    return ForecastGenerateRequest(
        region=RegionEnum.EMEA,
        fiscal_period="Q3_2026",
        prompt_override="Generate a forecast analysis for the EMEA region.",
        auto_approve_simulation=True,
        user_id="director_fpa@corp.internal",
    )


@pytest.fixture
def sample_latam_request() -> ForecastGenerateRequest:
    return ForecastGenerateRequest(
        region=RegionEnum.LATAM,
        fiscal_period="Q3_2026",
        prompt_override="Can you check the forecast and risk analysis for LATAM?",
        auto_approve_simulation=True,
        user_id="director_fpa@corp.internal",
    )


@pytest.fixture
def sample_na_request() -> ForecastGenerateRequest:
    return ForecastGenerateRequest(
        region=RegionEnum.NA,
        fiscal_period="Q3_2026",
        prompt_override="Please analyze the NA region forecast.",
        auto_approve_simulation=True,
        user_id="director_fpa@corp.internal",
    )
