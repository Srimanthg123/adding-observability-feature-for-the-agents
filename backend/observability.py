"""
Observability setup using Langfuse @observe decorator and OpenTelemetry.
"""
from langfuse import observe, get_client
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# -------------------------------
# OpenTelemetry setup
# -------------------------------
trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()

# Console exporter (for debugging spans in terminal)
tracer_provider.add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

# -------------------------------
# Langfuse client
# -------------------------------
langfuse_client = get_client()

def flush_langfuse():
    """
    Flush Langfuse traces safely on shutdown.
    """
    try:
        langfuse_client.flush()
    except Exception:
        pass




