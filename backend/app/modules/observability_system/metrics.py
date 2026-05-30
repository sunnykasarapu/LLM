from prometheus_client import Counter, Gauge, Histogram

api_requests_total = Counter("safety_api_requests_total", "Total API requests", ["path"])
evaluations_created_total = Counter("safety_evaluations_created_total", "Evaluations created")
provider_latency_ms = Histogram("safety_provider_latency_ms", "Provider latency in ms", buckets=(5, 10, 25, 50, 100, 250, 500, 1000, 5000))
queue_depth = Gauge("safety_queue_depth", "Estimated safety queue depth")

