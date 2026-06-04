from prometheus_client import Counter, Gauge, Histogram

api_requests_total = Counter("safety_api_requests_total", "Total API requests", ["path"])
evaluations_created_total = Counter("safety_evaluations_created_total", "Evaluations created")
provider_latency_ms = Histogram("safety_provider_latency_ms", "Provider latency in ms", buckets=(5, 10, 25, 50, 100, 250, 500, 1000, 5000))
queue_depth = Gauge("safety_queue_depth", "Estimated safety queue depth")
prompts_executed_total = Counter("safety_prompts_executed_total", "Evaluation prompts executed", ["provider", "category", "outcome"])
prompt_cache_hits_total = Counter("safety_prompt_cache_hits_total", "Prompt result cache hits", ["provider"])
safety_score = Gauge("safety_score", "Latest aggregate safety score for a model version", ["provider", "model_name", "model_version"])
safety_score_regression_delta = Gauge("safety_score_regression_delta", "Latest safety score percent change versus baseline", ["provider", "model_name", "model_version"])
evaluation_failures_total = Counter("safety_evaluation_failures_total", "Evaluation failures", ["provider"])
prompt_results_total = Gauge("safety_prompt_results_total", "Recorded prompt results from the database", ["provider", "category", "outcome"])
provider_latency_avg_ms = Gauge("safety_provider_latency_avg_ms", "Average provider latency from recorded results", ["provider"])
