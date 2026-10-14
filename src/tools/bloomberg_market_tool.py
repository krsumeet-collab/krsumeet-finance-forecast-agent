"""Bloomberg Market Intelligence News Integration Tool."""
from datetime import datetime, timedelta, timezone
from typing import List
from src.models.schemas import MarketIntelligenceFinding, MarketNewsItem, RegionEnum


class BloombergMarketTool:
    """Simulates Bloomberg Enterprise Market Data API for real-time news scans

    and competitor intelligence extraction.
    """

    async def scan_market_news_feeds(
        self, region: RegionEnum, prompt_context: str = ""
    ) -> MarketIntelligenceFinding:
        """Scans macroeconomic news feeds and competitor press releases for the target region."""
        pub_date = (datetime.now(timezone.utc) - timedelta(days=28)).strftime("%Y-%m-%d")
        ctx = (prompt_context or "").lower()

        has_comp_trigger = any(w in ctx for w in [
            "competitor", "predatory", "rival", "discount", "cloud vendor",
            "leadership", "attrition", "resigned"
        ]) or (region == RegionEnum.EMEA and "stable" not in ctx and "stabili" not in ctx and "upside" not in ctx and "macro" not in ctx and "fx" not in ctx and "currency" not in ctx)
        if has_comp_trigger:
            comp_name = "Competitor X"
            if "neocloud" in ctx:
                comp_name = "NeoCloud"
            elif "alpha" in ctx:
                comp_name = "Competitor Alpha"
            elif "rival" in ctx:
                comp_name = "Rival Cloud Titan"

            news = [
                MarketNewsItem(
                    headline=f"{comp_name} Disrupts {region.value} Market with Aggressive 'Cloud-Native' Product Launch",
                    source="Bloomberg Enterprise Tech Wire",
                    published_date=pub_date,
                    relevance_score=0.98,
                    key_competitor=comp_name,
                    sentiment="NEGATIVE",
                ),
            ]
            return MarketIntelligenceFinding(
                key_competitors_active=[comp_name],
                news_items=news,
                macro_headwinds=[f"Competitive Pricing Disruption from {comp_name}"],
                finding_summary=(
                    f"External market analysis discovered press releases confirming that '{comp_name}' "
                    f"launched an aggressive cloud product four weeks ago targeting primary market segments in {region.value}."
                ),
            )
        elif (
            "fx" in ctx
            or "currency" in ctx
            or "volatili" in ctx
            or "inflation" in ctx
            or "interest" in ctx
            or "headwind" in ctx
            or "macro" in ctx
            or "indicator" in ctx
            or (region == RegionEnum.LATAM and "leadership" not in ctx and "attrition" not in ctx and "competitor" not in ctx)
        ) and "stable" not in ctx and "stabili" not in ctx and "upside" not in ctx:
            news = [
                MarketNewsItem(
                    headline=f"{region.value} Regional Currencies & Macro Indices Face Headwinds",
                    source="Bloomberg Emerging Markets",
                    published_date=pub_date,
                    relevance_score=0.92,
                    key_competitor=None,
                    sentiment="NEGATIVE",
                )
            ]
            return MarketIntelligenceFinding(
                key_competitors_active=[],
                news_items=news,
                macro_headwinds=["Regional FX Volatility", "Macroeconomic Headwinds"],
                finding_summary=f"Bloomberg headlines register currency headwinds and macroeconomic volatility in {region.value}.",
            )
        elif "upside" in ctx or "launch" in ctx or "accel" in ctx or "breakthrough" in ctx:
            news = [
                MarketNewsItem(
                    headline=f"Industry Analysts Cite Breakthrough Adoption for Next-Gen Enterprise AI Suite",
                    source="Bloomberg Tech Insights",
                    published_date=pub_date,
                    relevance_score=0.95,
                    key_competitor=None,
                    sentiment="POSITIVE",
                )
            ]
            return MarketIntelligenceFinding(
                key_competitors_active=[],
                news_items=news,
                macro_headwinds=[],
                finding_summary=f"Market wires celebrate product acceleration and strong market reception in {region.value}.",
            )
        else:
            news = [
                MarketNewsItem(
                    headline=f"{region.value} Enterprise Tech Valuations Hold Steady",
                    source="Bloomberg Markets",
                    published_date=pub_date,
                    relevance_score=0.75,
                    key_competitor=None,
                    sentiment="POSITIVE",
                )
            ]
            return MarketIntelligenceFinding(
                key_competitors_active=[],
                news_items=news,
                macro_headwinds=[],
                finding_summary=f"Steady tech valuations and routine market conditions across {region.value}.",
            )


bloomberg_tool = BloombergMarketTool()
