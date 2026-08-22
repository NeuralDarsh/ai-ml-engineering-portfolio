# Distributed Systems & Observability: Generating, extracting, and propagating distributed trace correlation IDs across services

import uuid
import time
import json

class RequestContextTracker:
    """
    Manages distributed request tracing by extracting or generating unique Correlation IDs
    and injecting tracing context into outbound request headers and log records.
    """
    HEADER_KEY = "X-Correlation-ID"

    def _init_(self, service_name="ApiGateway"):
        self.service_name = service_name

    def process_inbound_request(self, inbound_headers=None):
        """
        Extracts existing correlation ID from inbound headers or generates a new trace UUID.
        """
        inbound_headers = inbound_headers or {}
        
        # Case-insensitive header extraction
        normalized_headers = {k.lower(): v for k, v in inbound_headers.items()}
        correlation_id = normalized_headers.get(self.HEADER_KEY.lower())

        is_new = False
        if not correlation_id:
            correlation_id = f"trace_{uuid.uuid4().hex[:12]}"
            is_new = True

        context = {
            "correlation_id": correlation_id,
            "origin_service": self.service_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_new_trace": is_new
        }

        print(f"--- Observability: [{self.service_name}] Inbound Request ---")
        print(f" Trace Status  : {'Generated New Trace' if is_new else 'Propagated Existing Trace'}")
        print(f" Correlation ID: {correlation_id}\n")
        return context

    def prepare_outbound_headers(self, context, downstream_service):
        """
        Injects the active correlation ID and caller metadata into outbound headers for downstream calls.
        """
        outbound_headers = {
            self.HEADER_KEY: context["correlation_id"],
            "X-Originating-Service": self.service_name,
            "X-Forwarded-For-Service": downstream_service
        }
        print(f"Forwarding call from [{self.service_name}] to [{downstream_service}]")
        print(f"Injected Headers: {json.dumps(outbound_headers, indent=2)}\n")
        return outbound_headers

if __name__ == "_main_":
    # 1. API Gateway receives fresh request without trace headers
    gateway = RequestContextTracker(service_name="APIGateway")
    gateway_context = gateway.process_inbound_request(inbound_headers={})

    # Gateway forwards request to Order Service
    outbound_to_orders = gateway.prepare_outbound_headers(gateway_context, "OrderMicroservice")

    print("=" * 60 + "\n")

    # 2. Order Service receives the forwarded request with existing trace header
    order_service = RequestContextTracker(service_name="OrderMicroservice")
    order_context = order_service.process_inbound_request(inbound_headers=outbound_to_orders)

    # Order Service forwards to Payment Gateway
    outbound_to_payment = order_service.prepare_outbound_headers(order_context, "PaymentService")