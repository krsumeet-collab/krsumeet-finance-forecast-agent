"""OpenTelemetry Tracing and Observability Module."""
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, AsyncGenerator


class TelemetryTracer:
    """Manages OpenTelemetry tracing, distributed span contexts,

    and latency metrics exporting to Google Cloud Trace.
    """

    def __init__(self, service_name: str = "finance-forecast-agent"):
        self.service_name = service_name

    @asynccontextmanager
    async def start_span(self, name: str, attributes: Dict[str, Any] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Context manager simulating an OpenTelemetry span with latency tracking."""
        start_time = time.perf_counter()
        span_data = {
            "name": name,
            "attributes": attributes or {},
            "status": "OK",
            "start_time": start_time,
        }
        try:
            yield span_data
        except Exception as e:
            span_data["status"] = "ERROR"
            span_data["error"] = str(e)
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            span_data["latency_ms"] = round(elapsed_ms, 2)
            # In live GCP, span is exported to Cloud Trace:
            # trace_client.create_span(...)


telemetry = TelemetryTracer()
