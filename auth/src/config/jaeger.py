from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)

from src.config.config import settings


def configure_tracer(app: Flask) -> None:
    if settings.enable_tracer:
        trace.set_tracer_provider(
            TracerProvider(resource=Resource.create(
                {
                    SERVICE_NAME: "Auth-service"
                 }
            )
            )
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(
                JaegerExporter(
                    agent_host_name=app.config.get("JAEGER_HOST", "localhost"),
                    agent_port=app.config.get("JAEGER_PORT", 6831),
                )
            )
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )


def init_jaeger(app: Flask):
    configure_tracer(app)
    FlaskInstrumentor().instrument_app(app)