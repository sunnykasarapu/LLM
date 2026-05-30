CREATE TYPE role AS ENUM ('admin', 'evaluator', 'viewer');
CREATE TYPE evaluationstatus AS ENUM ('queued', 'running', 'completed', 'failed');
CREATE TYPE attackcategory AS ENUM ('jailbreak', 'injection', 'toxicity', 'hallucination', 'bias');

CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  role role NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evaluation_runs (
  id TEXT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  provider VARCHAR(64) NOT NULL,
  model_name VARCHAR(255) NOT NULL,
  model_version VARCHAR(128) NOT NULL,
  status evaluationstatus NOT NULL,
  progress DOUBLE PRECISION NOT NULL DEFAULT 0,
  aggregate_score DOUBLE PRECISION,
  config JSONB NOT NULL,
  created_by TEXT REFERENCES users(id),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evaluation_results (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES evaluation_runs(id) ON DELETE CASCADE,
  attack_category attackcategory NOT NULL,
  original_prompt TEXT NOT NULL,
  mutated_prompt TEXT NOT NULL,
  response_text TEXT NOT NULL,
  provider_latency_ms INTEGER NOT NULL,
  scores JSONB NOT NULL,
  severity VARCHAR(32) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE regression_snapshots (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES evaluation_runs(id) ON DELETE CASCADE,
  baseline_run_id TEXT REFERENCES evaluation_runs(id),
  delta JSONB NOT NULL,
  degradation_detected BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE reports (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES evaluation_runs(id) ON DELETE CASCADE,
  json_payload JSONB NOT NULL,
  markdown TEXT NOT NULL,
  pdf_path VARCHAR(512),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
  id TEXT PRIMARY KEY,
  actor_id TEXT REFERENCES users(id),
  action VARCHAR(128) NOT NULL,
  resource_type VARCHAR(128) NOT NULL,
  resource_id VARCHAR(128),
  metadata JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
