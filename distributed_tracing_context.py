# Distributed Systems Observability & APM: Implementing W3C Trace Context parsing, propagation, and nested span telemetry

import time
import secrets
import json

class Span:
    """Represents a single timed unit of work within a distributed trace."""
    def __init__(self, name, trace_id, parent_span_id=None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = secrets.token_hex(8)  # 64-bit random hex identifier
        self.parent_span_id = parent_span_id
        self.start_time = 0.0
        self.end_time = 0.0
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)

    def to_dict(self):
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "duration_ms": self.duration_ms
        }


class W3CTraceContextEngine:
    """
    Parses and serializes W3C Traceparent headers:
    Format: {version:2hex}-{trace_id:32hex}-{parent_id:16hex}-{trace_flags:2hex}
    """
    VERSION = "00"
    DEFAULT_FLAGS = "01"  # Sampled

    @classmethod
    def generate_trace_id(cls):
        """Generates a globally unique 128-bit trace ID (32 hex characters)."""
        return secrets.token_hex(16)

    @classmethod
    def inject_traceparent(cls, span):
        """Encodes an active span into a W3C traceparent header string."""
        return f"{cls.VERSION}-{span.trace_id}-{span.span_id}-{cls.DEFAULT_FLAGS}"

    @classmethod
    def extract_traceparent(cls, traceparent_str):
        """Parses an incoming W3C traceparent header to extract trace_id and parent span_id."""
        if not traceparent_str:
            return None, None

        parts = traceparent_str.strip().split("-")
        if len(parts) != 4:
            raise ValueError(f"Invalid W3C traceparent format: '{traceparent_str}'")

        version, trace_id, parent_id, flags = parts
        if version != "00" or len(trace_id) != 32 or len(parent_id) != 16:
            raise ValueError(f"Malformed traceparent components: '{traceparent_str}'")

        return trace_id, parent_id


class DistributedTracer:
    """Simulates distributed tracing collector across service hops."""
    def __init__(self):
        self.recorded_spans = []

    def start_span(self, name, traceparent=None):
        """Starts a span from scratch or as a child of an incoming traceparent header."""
        if traceparent:
            trace_id, parent_id = W3CTraceContextEngine.extract_traceparent(traceparent)
        else:
            trace_id = W3CTraceContextEngine.generate_trace_id()
            parent_id = None

        span = Span(name, trace_id, parent_id)
        return span

    def record_span(self, span):
        self.recorded_spans.append(span.to_dict())


if __name__ == "__main__":
    print("--- Observability: W3C Distributed Tracing Engine ---\n")

    tracer = DistributedTracer()

    # Step 1: Request enters the API Gateway (Root Span)
    print("Hop 1: Ingress at [APIGateway]")
    with tracer.start_span("APIGateway::HandleCheckout") as root_span:
        time.sleep(0.04)  # Simulate gateway auth/routing overhead
        tracer.record_span(root_span)

        # Ingress gateway injects W3C header into HTTP request for downstream service
        carrier_header = W3CTraceContextEngine.inject_traceparent(root_span)
        print(f" Injected W3C Header -> traceparent: {carrier_header}\n")

    # Step 2: Request arrives at Order Service
    print("Hop 2: Request received at [OrderService]")
    with tracer.start_span("OrderService::ProcessOrder", traceparent=carrier_header) as order_span:
        time.sleep(0.06)
        tracer.record_span(order_span)

        carrier_header_2 = W3CTraceContextEngine.inject_traceparent(order_span)
        print(f"Injected W3C Header -> traceparent: {carrier_header_2}\n")

    # Step 3: Request arrives at Payment Service
    print("Hop 3: Request received at [PaymentService]")
    with tracer.start_span("PaymentService::ChargeCard", traceparent=carrier_header_2) as payment_span:
        time.sleep(0.08)
        tracer.record_span(payment_span)

    # Output hierarchical trace telemetry
    print("=" * 65)
    print("Aggregated Distributed Trace Spans:")
    print(json.dumps(tracer.recorded_spans, indent=2))