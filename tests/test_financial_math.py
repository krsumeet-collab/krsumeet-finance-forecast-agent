"""Unit tests for deterministic financial math and variance waterfall engine."""
import pytest
from src.tools.financial_math_engine import financial_math_engine
from src.models.schemas import RiskClassEnum


def test_high_risk_waterfall_math():
    baseline = 90.90
    bridge = financial_math_engine.compute_variance_waterfall(
        baseline_usd=baseline,
        risk_class=RiskClassEnum.HIGH_RISK,
    )
    assert bridge.tie_out_verified is True
    # 15% penalty on 90.90 is 13.635
    assert bridge.total_variance_penalty_usd == 13.635
    assert bridge.simulated_revenue_usd == 77.265
    assert bridge.variance_percentage == 15.0
    assert bridge.slippage_haircut_usd > 0
    assert bridge.competitor_or_macro_impact_usd > 0
    assert bridge.adjusted_ebitda_usd < bridge.baseline_ebitda_usd
    assert bridge.ebitda_margin_compression_bps > 0


def test_medium_risk_waterfall_math():
    baseline = 52.00
    bridge = financial_math_engine.compute_variance_waterfall(
        baseline_usd=baseline,
        risk_class=RiskClassEnum.MEDIUM_RISK,
    )
    assert bridge.tie_out_verified is True
    # 8% penalty on 52.00 is 4.16
    assert bridge.total_variance_penalty_usd == 4.160
    assert bridge.simulated_revenue_usd == 47.840
    assert bridge.variance_percentage == 8.0


def test_low_risk_waterfall_math():
    baseline = 145.00
    bridge = financial_math_engine.compute_variance_waterfall(
        baseline_usd=baseline,
        risk_class=RiskClassEnum.LOW_RISK,
    )
    assert bridge.tie_out_verified is True
    # 2% variance on 145.00 is 2.90
    assert bridge.total_variance_penalty_usd == 2.900
    assert bridge.simulated_revenue_usd == 142.100


def test_custom_slippage_and_cogs_inflation():
    baseline = 100.00
    bridge = financial_math_engine.compute_variance_waterfall(
        baseline_usd=baseline,
        custom_slippage_pct=0.20,
        cost_inflation_pct=0.05,
    )
    assert bridge.total_variance_penalty_usd == 20.00
    assert bridge.simulated_revenue_usd == 80.00
    assert bridge.tie_out_verified is True


def test_verify_narrative_tie_out():
    baseline = 90.90
    bridge = financial_math_engine.compute_variance_waterfall(
        baseline_usd=baseline,
        risk_class=RiskClassEnum.HIGH_RISK,
    )
    narrative = f"Simulated revenue is $77.3M with projected miss of -$13.6M."
    verified, msg = financial_math_engine.verify_narrative_tie_out(narrative, bridge)
    assert verified is True
