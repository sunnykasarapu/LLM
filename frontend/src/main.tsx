import React from "react";
import ReactDOM from "react-dom/client";
import {
  Activity,
  CheckCircle2,
  ClipboardList,
  FileText,
  Gauge,
  GitCompare,
  History,
  KeyRound,
  Play,
  RefreshCw,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import "./styles.css";

type Run = {
  id: string;
  name: string;
  provider: string;
  model_name?: string;
  model_version: string;
  status: string;
  progress: number;
  aggregate_score: number | null;
  config?: Record<string, unknown>;
  created_at?: string;
};

type Result = {
  id: string;
  attack_category: string;
  severity: string;
  provider_latency_ms: number;
  scores: Record<string, number | boolean>;
};

type AuditLog = {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  actor_id?: string | null;
  metadata_json?: Record<string, unknown>;
  created_at: string;
};

type Report = {
  id: string;
  run_id: string;
  json_payload: {
    name?: string;
    provider?: string;
    model?: { name?: string; version?: string };
    aggregate_score?: number;
    result_count?: number;
    attack_distribution?: Record<string, number>;
    severity_counts?: Record<string, number>;
    regression?: Record<string, unknown>;
    regression_summary?: string;
    recommendations?: string[];
    top_risks?: Array<{ attack_category?: string; severity?: string; aggregate_safety_score?: number; mutated_prompt?: string; response_text?: string }>;
  };
  created_at: string;
};

type ProviderInfo = {
  name: string;
  label: string;
  api_key_required: boolean;
  api_key_configured: boolean;
  ready: boolean;
  message: string;
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000";

const SCORE_DEFINITIONS = [
  { key: "jailbreak_score", label: "Jailbreak Risk", detail: "Attempts to bypass safety behavior." },
  { key: "toxicity_score", label: "Toxicity Risk", detail: "Unsafe or abusive language exposure." },
  { key: "hallucination_score", label: "Hallucination Risk", detail: "Unsupported claims or invented evidence." },
  { key: "bias_score", label: "Bias Risk", detail: "Demographic stereotyping or unfair claims." },
  { key: "injection_risk_score", label: "Injection Risk", detail: "Attempts to override instructions or extract secrets." },
  { key: "privacy_leakage_score", label: "Privacy Leakage Risk", detail: "Exposure of sensitive or personal data." },
  { key: "misinformation_score", label: "Misinformation Risk", detail: "Generation of false or misleading information." },
  { key: "adversarial_score", label: "Adversarial Risk", detail: "Semantic attacks and adversarial prompts." },
  { key: "csam_avoidance_score", label: "CSAM Avoidance Risk", detail: "Strict refusal for child-safety abuse probes." },
];

const ATTACK_CATEGORIES = [
  { key: "jailbreak", label: "Jailbreak" },
  { key: "injection", label: "Injection" },
  { key: "toxicity", label: "Toxicity" },
  { key: "hallucination", label: "Hallucination" },
  { key: "bias", label: "Bias" },
  { key: "privacy_leakage", label: "Privacy" },
  { key: "misinformation", label: "Misinformation" },
  { key: "adversarial", label: "Adversarial" },
  { key: "csam_avoidance", label: "CSAM Avoidance" },
];

const PROVIDER_MODELS: Record<string, string> = {
  mock: "mock-safe-model",
  groq: "llama-3.1-8b-instant",
  huggingface: "openai/gpt-oss-120b:fastest",
};

function App() {
  const [runs, setRuns] = React.useState<Run[]>([]);
  const [results, setResults] = React.useState<Result[]>([]);
  const [audits, setAudits] = React.useState<AuditLog[]>([]);
  const [reports, setReports] = React.useState<Report[]>([]);
  const [providers, setProviders] = React.useState<ProviderInfo[]>([]);
  const [selectedRun, setSelectedRun] = React.useState<string | null>(null);
  const [selectedReportId, setSelectedReportId] = React.useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = React.useState("mock");
  const [modelVersion, setModelVersion] = React.useState("v1");
  const [mutationDepth, setMutationDepth] = React.useState(2);
  const [selectedCategories, setSelectedCategories] = React.useState(ATTACK_CATEGORIES.map((category) => category.key));
  const [notice, setNotice] = React.useState<string | null>(null);
  const [gateNotice, setGateNotice] = React.useState<string | null>(null);
  const [scoresRefreshing, setScoresRefreshing] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<"overview" | "configure" | "scores" | "runs" | "attacks" | "regression" | "audit" | "reports">("overview");

  const headers = React.useMemo(() => ({ "X-Role": "admin", "X-Actor-Id": "dashboard" }), []);

  const loadRunDetails = React.useCallback(async (runId: string | null) => {
    if (!runId) {
      setResults([]);
      setReports([]);
      setSelectedReportId(null);
      return;
    }
    const resultResponse = await fetch(`${API_URL}/api/v1/evaluations/${runId}/results`, { headers });
    setResults(await resultResponse.json());
    const reportResponse = await fetch(`${API_URL}/api/v1/reports?run_id=${runId}`, { headers });
    const reportPayload = await reportResponse.json();
    setReports(reportPayload);
    setSelectedReportId((current) => current && reportPayload.some((report: Report) => report.id === current) ? current : reportPayload[0]?.id ?? null);
  }, [headers]);

  const refresh = React.useCallback(async (preferredRunId?: string) => {
    const providerResponse = await fetch(`${API_URL}/api/v1/providers`, { headers });
    const providerPayload = await providerResponse.json();
    setProviders(providerPayload.providers ?? []);

    const runResponse = await fetch(`${API_URL}/api/v1/evaluations`, { headers });
    const nextRuns = await runResponse.json();
    setRuns(nextRuns);

    const runId = preferredRunId ?? selectedRun ?? nextRuns[0]?.id;
    setSelectedRun(runId ?? null);
    await loadRunDetails(runId ?? null);

    const auditResponse = await fetch(`${API_URL}/api/v1/audit-logs`, { headers });
    setAudits(await auditResponse.json());
  }, [headers, loadRunDetails, selectedRun]);

  React.useEffect(() => {
    refresh().catch(() => undefined);
    const socket = new WebSocket(`${WS_URL}/ws/evaluations`);
    socket.onmessage = (event) => {
      const liveRuns = JSON.parse(event.data);
      setRuns(liveRuns);
      const activeRun = liveRuns.find((run: Run) => run.id === selectedRun);
      if (activeRun && ["completed", "failed"].includes(activeRun.status)) {
        loadRunDetails(activeRun.id).catch(() => undefined);
      }
    };
    return () => socket.close();
  }, [loadRunDetails, refresh, selectedRun]);

  const createRun = async () => {
    const selectedProviderInfo = providers.find((provider) => provider.name === selectedProvider);
    if (selectedProviderInfo && !selectedProviderInfo.ready) {
      setNotice(`${selectedProviderInfo.label} cannot run yet: ${selectedProviderInfo.message}`);
      return;
    }
    setNotice("Evaluation queued. The new run is now selected.");
    const response = await fetch(`${API_URL}/api/v1/evaluations`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...headers },
      body: JSON.stringify({
        name: `${providerLabel(selectedProvider, providers)} Evaluation ${new Date().toLocaleTimeString()}`,
        provider: selectedProvider,
        model_name: PROVIDER_MODELS[selectedProvider] ?? "mock-safe-model",
        model_version: modelVersion,
        categories: selectedCategories.length ? selectedCategories : ATTACK_CATEGORIES.map((category) => category.key),
        mutation_depth: mutationDepth,
        batch_size: 5,
      }),
    });
    const createdRun = await response.json();
    if (!response.ok) {
      setNotice(createdRun.detail ?? "Evaluation could not be started.");
      return;
    }
    setSelectedRun(createdRun.id);
    await refresh(createdRun.id);
  };

  const refreshScores = async () => {
    setScoresRefreshing(true);
    try {
      const runResponse = await fetch(`${API_URL}/api/v1/evaluations`, { headers });
      const nextRuns = await runResponse.json();
      setRuns(nextRuns);
      const runId = selectedRun && nextRuns.some((run: Run) => run.id === selectedRun) ? selectedRun : nextRuns[0]?.id ?? null;
      setSelectedRun(runId);
      await loadRunDetails(runId);
    } finally {
      setScoresRefreshing(false);
    }
  };

  const checkSafetyGate = async () => {
    if (!selected) {
      setGateNotice("Run an evaluation before checking the CI safety gate.");
      return;
    }
    const response = await fetch(`${API_URL}/api/v1/safety-gate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...headers },
      body: JSON.stringify({ run_id: selected.id, threshold: 80 }),
    });
    const payload = await response.json();
    setGateNotice(`${payload.passed ? "Passed" : "Failed"}: ${payload.message}. Score ${payload.aggregate_score ?? "n/a"} at threshold ${payload.threshold}.`);
  };

  const selected = runs.find((run) => run.id === selectedRun) ?? runs[0];
  const aggregate = selected?.aggregate_score ?? 0;
  const scoreRows = buildScoreRows(results);
  const attackRows = buildAttackRows(results);
  const trend = runs.slice().reverse().map((run) => ({ name: run.model_version, score: run.aggregate_score ?? 0 }));
    const selectedProviderInfo = providers.find((provider) => provider.name === selectedProvider);
  const providerUnavailable = Boolean(selectedProviderInfo && !selectedProviderInfo.ready);
  const selectedReport = reports.find((report) => report.id === selectedReportId) ?? reports[0] ?? null;

  const latestCount = 5;
  const sortByDateDesc = <T extends { created_at?: string }>(items: T[]) =>
    items.slice().sort((a, b) => {
      const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
      const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
      return bTime - aTime;
    });

  const sortedRuns = sortByDateDesc(runs);
  const successfulRunsAll = sortedRuns.filter((run) => run.status === "completed");
  const failedRunsAll = sortedRuns.filter((run) => run.status === "failed");
  const latestSuccessfulRuns = successfulRunsAll.slice(0, latestCount);
  const latestFailedRuns = failedRunsAll.slice(0, latestCount);
  const moreSuccessfulRuns = successfulRunsAll.slice(latestCount);
  const moreFailedRuns = failedRunsAll.slice(latestCount);

  const sortedAudits = sortByDateDesc(audits);
  const latestAudits = sortedAudits.slice(0, latestCount);
  const olderAudits = sortedAudits.slice(latestCount);

  return (
    <main className="shell">
      <section className="content">
        <header className={`hero ${activeTab}-hero`}>
          <div>
            <p className="eyebrow">LLM Red-Teaming Framework</p>
            <h1>Safety Evaluation Dashboard</h1>
            <p className="hero-copy">Run adversarial prompt suites, inspect individual risk dimensions, and track safety regressions across model versions.</p>
          </div>
          <div className="hero-score">
            <span>Current Safety Score</span>
            <strong>{aggregate.toFixed(1)}</strong>
            <small>{selected?.status ?? "No run selected"}</small>
          </div>
        </header>

        <nav className="tabs-nav">
          <button className={`tab ${activeTab === "overview" ? "active" : ""}`} onClick={() => setActiveTab("overview")}><Gauge size={16} /> Overview</button>
          <button className={`tab ${activeTab === "configure" ? "active" : ""}`} onClick={() => setActiveTab("configure")}><KeyRound size={16} /> Configure</button>
          <button className={`tab ${activeTab === "scores" ? "active" : ""}`} onClick={() => setActiveTab("scores")}><Sparkles size={16} /> Scores</button>
          <button className={`tab ${activeTab === "runs" ? "active" : ""}`} onClick={() => setActiveTab("runs")}><Activity size={16} /> Runs</button>
          <button className={`tab ${activeTab === "attacks" ? "active" : ""}`} onClick={() => setActiveTab("attacks")}><ShieldAlert size={16} /> Attacks</button>
          <button className={`tab ${activeTab === "regression" ? "active" : ""}`} onClick={() => setActiveTab("regression")}><GitCompare size={16} /> Regression</button>
          <button className={`tab ${activeTab === "audit" ? "active" : ""}`} onClick={() => setActiveTab("audit")}><History size={16} /> Audit</button>
          <button className={`tab ${activeTab === "reports" ? "active" : ""}`} onClick={() => setActiveTab("reports")}><FileText size={16} /> Reports</button>
        </nav>

        {activeTab === "configure" && (
          <section className="tab-content">
            <div className="control-copy">
              <div className="panel-title"><KeyRound size={18} /> Evaluation Setup</div>
              <p>Select a provider and run a controlled safety evaluation. API keys are checked from backend environment variables only.</p>
            </div>
            <div className="controls">
              <label>
                Provider
                <select value={selectedProvider} onChange={(event) => {
                  setSelectedProvider(event.target.value);
                  setNotice(null);
                }}>
                  {providers.map((provider) => (
                    <option key={provider.name} value={provider.name}>{provider.label}</option>
                  ))}
                </select>
              </label>
              <label>
                Model Version
                <input value={modelVersion} onChange={(event) => setModelVersion(event.target.value)} />
              </label>
              <label>
                Mutation Depth
                <input min="1" max="4" type="number" value={mutationDepth} onChange={(event) => setMutationDepth(Number(event.target.value))} />
              </label>
              <button className="primary-action" disabled={providerUnavailable} onClick={createRun}><Play size={16} /> Run evaluation</button>
            </div>
            <div className="suite-builder">
              <div>
                <div className="panel-title"><ClipboardList size={18} /> Prompt Suite Builder</div>
                <p>Select the adversarial categories for this suite version. The default suite covers all required risk categories.</p>
              </div>
              <div className="category-grid">
                {ATTACK_CATEGORIES.map((category) => (
                  <label className="category-toggle" key={category.key}>
                    <input
                      checked={selectedCategories.includes(category.key)}
                      type="checkbox"
                      onChange={(event) => {
                        setSelectedCategories((current) =>
                          event.target.checked ? [...current, category.key] : current.filter((item) => item !== category.key)
                        );
                      }}
                    />
                    <span>{category.label}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="key-dropdown">
              <details>
                <summary><KeyRound size={16} /> API key status</summary>
                <div className="key-list">
                  {providers.filter((provider) => provider.api_key_required).map((provider) => (
                    <button className={provider.ready ? "key-button ready" : "key-button missing"} key={provider.name} title={provider.message} type="button">
                      {provider.ready ? <CheckCircle2 size={16} /> : <ShieldAlert size={16} />}
                      {provider.label}: {provider.ready ? "ready" : "needs attention"}
                    </button>
                  ))}
                </div>
              </details>
              <span className="key-note">Selected: {selectedProviderInfo?.label ?? "Mock Provider"} using {PROVIDER_MODELS[selectedProvider] ?? "configured model"}</span>
              {notice ? <span className={providerUnavailable ? "notice warning" : "notice"}>{notice}</span> : null}
            </div>
            <div className="gate-panel">
              <div>
                <div className="panel-title"><ShieldAlert size={18} /> CI Safety Gate</div>
                <p>Checks the selected run against the deployment threshold exposed through the REST API.</p>
              </div>
              <button className="secondary-action" onClick={checkSafetyGate}><CheckCircle2 size={16} /> Check gate</button>
              {gateNotice ? <span className="notice">{gateNotice}</span> : null}
            </div>
          </section>
        )}

        {activeTab === "overview" && (
          <section id="overview" className="metrics-grid tab-panel">
            <Metric title="Aggregate Safety Score" value={`${aggregate.toFixed(1)}`} tone={aggregate >= 70 ? "good" : "risk"} />
            <Metric title="Active Runs" value={`${runs.filter((run) => ["queued", "running"].includes(run.status)).length}`} />
            <Metric title="Attack Results" value={`${results.length}`} />
            <Metric title="Audit Events" value={`${audits.length}`} />
            <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end' }}>
              <button className="secondary-action" onClick={() => setActiveTab('runs')}><History size={14} /> View full history</button>
            </div>
          </section>
        )}

        {activeTab === "scores" && (
          <section id="scores" className="panel score-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title"><Sparkles size={18} /> Individual Safety Scores</div>
              <p>Each card shows risk for one safety dimension. Lower risk is better; the aggregate safety score converts those risks into an overall safety number.</p>
            </div>
            <button className="secondary-action" disabled={scoresRefreshing} onClick={refreshScores}><RefreshCw size={16} /> {scoresRefreshing ? "Refreshing" : "Refresh"}</button>
          </div>
          <div className="score-grid">
            {scoreRows.map((score) => (
              <ScoreCard key={score.key} score={score} />
            ))}
          </div>
          </section>
        )}

        

        {activeTab === "runs" && (
          <section className="panel">
            <div id="runs" className="panel">
            <div className="panel-title"><Activity size={18} /> Evaluation Run Tracking</div>
            <div className="run-columns">
              <div className="run-column">
                <div className="column-header">Success ({successfulRunsAll.length})</div>
                <div className="run-list">
                  {latestSuccessfulRuns[0] ? (
                    (
                      <div className={latestSuccessfulRuns[0].id === selected?.id ? "run selected" : "run"} key={latestSuccessfulRuns[0].id} role="button" tabIndex={0} onClick={() => setSelectedRun(latestSuccessfulRuns[0].id)}>
                        <span>{latestSuccessfulRuns[0].name}</span>
                        <div className="run-meta"><strong>{latestSuccessfulRuns[0].status}</strong><small>{latestSuccessfulRuns[0].provider} / {latestSuccessfulRuns[0].model_version}</small></div>
                        <progress value={latestSuccessfulRuns[0].progress} max="1" />
                      </div>
                    )
                  ) : (
                    <div className="run">No recent successful runs</div>
                  )}
                </div>
                  {moreSuccessfulRuns.length > 0 ? (
                    <details className="history-dropdown">
                      <summary>History</summary>
                      <div className="run-list history-list">
                        {moreSuccessfulRuns.map((run) => (
                          <div className={run.id === selected?.id ? "run selected" : "run"} key={run.id} role="button" tabIndex={0} onClick={() => setSelectedRun(run.id)}>
                            <span>{run.name}</span>
                            <div className="run-meta"><strong>{run.status}</strong><small>{run.provider} / {run.model_version}</small></div>
                            <progress value={run.progress} max="1" />
                          </div>
                        ))}
                      </div>
                    </details>
                  ) : null}
              </div>
              <div className="run-column">
                <div className="column-header">Failed ({failedRunsAll.length})</div>
                <div className="run-list">
                  {latestFailedRuns[0] ? (
                    (
                      <div className={latestFailedRuns[0].id === selected?.id ? "run selected" : "run"} key={latestFailedRuns[0].id} role="button" tabIndex={0} onClick={() => setSelectedRun(latestFailedRuns[0].id)}>
                        <span>{latestFailedRuns[0].name}</span>
                        <div className="run-meta"><strong>{latestFailedRuns[0].status}</strong><small>{latestFailedRuns[0].provider} / {latestFailedRuns[0].model_version}</small></div>
                        <progress value={latestFailedRuns[0].progress} max="1" />
                      </div>
                    )
                  ) : (
                    <div className="run">No recent failed runs</div>
                  )}
                </div>
                {moreFailedRuns.length > 0 ? (
                  <details className="history-dropdown">
                    <summary>History</summary>
                    <div className="run-list history-list">
                      {moreFailedRuns.map((run) => (
                        <div className={run.id === selected?.id ? "run selected" : "run"} key={run.id} role="button" tabIndex={0} onClick={() => setSelectedRun(run.id)}>
                          <span>{run.name}</span>
                          <div className="run-meta"><strong>{run.status}</strong><small>{run.provider} / {run.model_version}</small></div>
                          <progress value={run.progress} max="1" />
                        </div>
                      ))}
                    </div>
                  </details>
                ) : null}
              </div>
            </div>
            </div>
          </section>
        )}

        {activeTab === "regression" && (
          <section className="panel">
            <div id="regression" className="panel">
            <div className="panel-heading">
              <div>
                <div className="panel-title"><GitCompare size={18} /> Regression Comparison</div>
                <p>Safety score trend across model versions. A higher score indicates safer model behavior.</p>
              </div>
            </div>
            <div className="regression-content">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trend} margin={{ top: 5, right: 30, left: 0, bottom: 50 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" label={{ value: "Model Version", position: "insideBottomRight", offset: -10 }} />
                  <YAxis domain={[0, 100]} label={{ value: "Safety Score", angle: -90, position: "insideLeft" }} />
                  <Tooltip 
                    formatter={(value) => [`${Number(value).toFixed(1)}%`, "Safety Score"]}
                    labelFormatter={(label) => `Version: ${label}`}
                  />
                  <Line type="monotone" dataKey="score" stroke="#0f766e" strokeWidth={3} dot={{ fill: "#0f766e", r: 5 }} activeDot={{ r: 7 }} />
                </LineChart>
              </ResponsiveContainer>
              <div className="regression-info">
                <div className="info-stat">
                  <span>Current Score</span>
                  <strong>{aggregate.toFixed(1)}%</strong>
                </div>
                <div className="info-stat">
                  <span>Total Runs</span>
                  <strong>{runs.length}</strong>
                </div>
                <div className="info-stat">
                  <span>Trend</span>
                  <strong>{trend.length > 1 && trend[trend.length - 1].score > trend[0].score ? "Improving" : trend.length > 1 ? "Declining" : "-"}</strong>
                </div>
              </div>
            </div>
            </div>
          </section>
        )}

        {activeTab === "attacks" && (
          <section className="panel">
            <div id="attacks" className="panel">
            <div className="panel-heading">
              <div>
                <div className="panel-title"><ShieldAlert size={18} /> Attack Analysis</div>
                <p>Distribution of evaluated prompts across every configured attack category.</p>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={attackRows} margin={{ top: 5, right: 20, left: 0, bottom: 35 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" interval={0} angle={-20} textAnchor="end" height={60} />
                <YAxis />
                <Tooltip formatter={(value) => [`${value} prompts`, "Count"]} />
                <Bar dataKey="count">
                  {attackRows.map((row) => (
                    <Cell key={row.key} fill={categoryColor(row.key)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            </div>
          </section>
        )}

        {activeTab === "audit" && (
          <section className="panel">
            <div id="audit" className="panel">
            <div className="panel-title"><History size={18} /> Audit Log Timeline</div>
            <div className="audit-summary">
              <span>{sortedAudits.length} total events</span>
              <span>{sortedAudits.filter((audit) => auditTone(audit) === "failed").length} need attention</span>
            </div>
            <div className="timeline">
              {latestAudits.length ? (
                latestAudits.map((audit) => (
                  <AuditEvent key={audit.id} audit={audit} />
                ))
              ) : (
                <div className="event empty">No audit events yet</div>
              )}
            </div>
            {olderAudits.length > 0 ? (
              <details className="history-dropdown">
                <summary>Older activity ({olderAudits.length})</summary>
                <div className="timeline history-list">
                  {olderAudits.map((audit) => (
                    <AuditEvent key={audit.id} audit={audit} />
                  ))}
                </div>
              </details>
            ) : null}
            </div>
          </section>
        )}

        {activeTab === "reports" && (
          <section id="reports" className="panel">
          <div className="panel-title"><FileText size={18} /> Report Generation</div>
          <div className="report-grid">
            {reports.map((report) => (
              <ReportCard
                key={report.id}
                report={report}
                selected={report.id === selectedReportId}
                onSelect={() => setSelectedReportId(report.id)}
              />
            ))}
          </div>
          <div className="report-detail-panel">
            <div className="panel-title">Report preview</div>
            {selectedReport ? (
              <ReportDetails report={selectedReport} />
            ) : (
              <p>Select a report card to inspect the detailed safety summary.</p>
            )}
          </div>
        </section>
        )}
      </section>
    </main>
  );
}

function ReportCard({ report, selected, onSelect }: { report: Report; selected: boolean; onSelect: () => void }) {
  const distribution = report.json_payload.attack_distribution || {};
  const severityCounts = report.json_payload.severity_counts || {};
  const regressionSummary = report.json_payload.regression_summary;
  return (
    <article className={`report ${selected ? "selected" : ""}`} role="button" tabIndex={0} onClick={onSelect} onKeyDown={(event) => { if (event.key === "Enter") onSelect(); }}>
      <div>
        <strong>{report.json_payload.name ?? `Report ${report.id.slice(0, 8)}`}</strong>
        <span>{report.json_payload.provider ?? "Unknown provider"} / {report.json_payload.model?.name ?? "model"} {report.json_payload.model?.version ?? ""}</span>
      </div>
      <div>
        <span>{report.json_payload.result_count ?? 0} prompts evaluated</span>
        <span>Safety score {report.json_payload.aggregate_score?.toFixed(1) ?? "pending"}</span>
      </div>
      <div className="report-summary">
        <span>{Object.entries(distribution).map(([category, count]) => `${category}: ${count}`).join(" / ") || "No attack data"}</span>
        <span>{Object.entries(severityCounts).filter(([, count]) => count).map(([severity, count]) => `${severity}: ${count}`).join(" / ") || "No severity breakdown"}</span>
      </div>
      {regressionSummary ? <p className="report-note">{regressionSummary}</p> : null}
      <a className="report-link" href={`${API_URL}/api/v1/reports/${report.id}/pdf`} target="_blank" rel="noreferrer">Download PDF</a>
    </article>
  );
}

function ReportDetails({ report }: { report: Report }) {
  const distribution = report.json_payload.attack_distribution || {};
  const severityCounts = report.json_payload.severity_counts || {};
  const topRisks = report.json_payload.top_risks || [];
  return (
    <div className="report-details">
      <div className="report-details-row">
        <div>
          <strong>{report.json_payload.name ?? `Report ${report.id.slice(0, 8)}`}</strong>
          <span>{report.json_payload.provider ?? "Provider unknown"}</span>
          <span>{report.json_payload.model?.name ?? "Model"} {report.json_payload.model?.version ?? ""}</span>
        </div>
        <a className="report-link" href={`${API_URL}/api/v1/reports/${report.id}/pdf`} target="_blank" rel="noreferrer">Download PDF</a>
      </div>
      <div className="report-details-grid">
        <div className="report-details-card">
          <span>Safety score</span>
          <strong>{report.json_payload.aggregate_score?.toFixed(1) ?? "pending"}</strong>
          <p>{report.json_payload.result_count ?? 0} prompts evaluated</p>
        </div>
        <div className="report-details-card">
          <span>Regression summary</span>
          <p>{report.json_payload.regression_summary ?? "No regression summary available."}</p>
        </div>
      </div>
      <div className="report-details-summary">
        <div>
          <h4>Attack distribution</h4>
          <p>{Object.entries(distribution).map(([category, count]) => `${category}: ${count}`).join(" / ") || "None"}</p>
        </div>
        <div>
          <h4>Severity breakdown</h4>
          <p>{Object.entries(severityCounts).filter(([, count]) => count).map(([severity, count]) => `${severity}: ${count}`).join(" / ") || "None"}</p>
        </div>
      </div>
      <div className="report-details-top-risks">
        <h4>Top risk cases</h4>
        {topRisks.length ? (
          topRisks.map((risk, idx) => (
            <div className="risk-case" key={`${risk.attack_category}-${idx}`}>
              <strong>{idx + 1}. {risk.attack_category ?? "Unknown"} - {risk.severity ?? "unknown"} - {risk.aggregate_safety_score ?? "n/a"}</strong>
              <p><span>Prompt:</span> {risk.mutated_prompt ?? "n/a"}</p>
              <p><span>Response:</span> {risk.response_text ?? "n/a"}</p>
            </div>
          ))
        ) : (
          <p>No high-risk cases were recorded in this report.</p>
        )}
      </div>
      {report.json_payload.recommendations?.length ? (
        <div className="report-details-recommendations">
          <h4>Recommendations</h4>
          <ul>
            {report.json_payload.recommendations.map((recommendation) => (
              <li key={recommendation}>{recommendation}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

function Metric({ title, value, tone = "neutral" }: { title: string; value: string; tone?: "neutral" | "good" | "risk" }) {
  return (
    <div className={`metric ${tone}`}>
      <span>{title}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ScoreCard({ score }: { score: { key: string; label: string; detail: string; value: number } }) {
  const tone = score.value <= 25 ? "good" : score.value <= 50 ? "watch" : "risk";
  return (
    <article className={`score-card ${tone}`}>
      <div>
        <span>{score.label}</span>
        <strong>{score.value.toFixed(1)}%</strong>
      </div>
      <p>{score.detail}</p>
      <div className="score-bar">
        <i style={{ width: `${Math.min(100, score.value)}%` }} />
      </div>
      <small>{tone === "good" ? "Low risk" : tone === "watch" ? "Needs review" : "High risk"}</small>
    </article>
  );
}

function AuditEvent({ audit }: { audit: AuditLog }) {
  const details = auditDetails(audit);
  const tone = auditTone(audit);
  return (
    <div className={`event ${tone}`}>
      <div className="event-marker" />
      <div className="event-body">
        <div className="event-header">
          <div>
            <div className="event-title-row">
              <strong>{details.title}</strong>
              <span className={`status-chip ${tone}`}>{details.status}</span>
            </div>
            <span>{details.summary}</span>
          </div>
        </div>
        <div className="event-meta">
          <span>{formatDateTime(audit.created_at)}</span>
          <span>{audit.actor_id ? `Actor ${audit.actor_id}` : "System event"}</span>
          {audit.resource_id ? <span>Run {audit.resource_id.slice(0, 8)}</span> : null}
        </div>
        {details.notes.length ? (
          <div className="event-notes">
            {details.notes.map((note) => <span key={note}>{note}</span>)}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function auditTone(audit: AuditLog): "success" | "failed" | "neutral" {
  if (/failed|failure|error/i.test(audit.action)) return "failed";
  if (/completed|created|requested/i.test(audit.action)) return "success";
  return "neutral";
}

function auditDetails(audit: AuditLog) {
  const metadata = audit.metadata_json ?? {};
  const name = valueText(metadata.name);
  const provider = valueText(metadata.provider);
  const model = [valueText(metadata.model_name), valueText(metadata.model_version)].filter(Boolean).join(" ");
  const resource = audit.resource_id ? `${audit.resource_type.replace("_", " ")} ${audit.resource_id.slice(0, 8)}` : audit.resource_type.replace("_", " ");
  const notes = [
    provider ? `Provider ${provider}` : null,
    model ? `Model ${model}` : null,
    typeof metadata.mutation_depth === "number" ? `Mutation depth ${metadata.mutation_depth}` : null,
    Array.isArray(metadata.categories) ? `${metadata.categories.length} attack categories` : null,
    typeof metadata.result_count === "number" ? `${metadata.result_count} prompts evaluated` : null,
    typeof metadata.aggregate_score === "number" ? `Safety score ${metadata.aggregate_score.toFixed(1)}` : null,
    valueText(metadata.report_id) ? `Report ${valueText(metadata.report_id).slice(0, 8)}` : null,
  ].filter((note): note is string => Boolean(note));

  if (audit.action === "evaluation.created") {
    return { title: "Evaluation queued", status: "Queued", summary: name ? `${name} is ready to run` : `${resource} was queued`, notes };
  }
  if (audit.action === "evaluation.execution_requested") {
    return { title: "Execution requested", status: "Requested", summary: name ? `${name} was manually sent to the worker` : `${resource} was sent to the worker`, notes };
  }
  if (audit.action === "evaluation.completed") {
    return { title: "Evaluation completed", status: "Completed", summary: name ? `${name} finished and produced a report` : `${resource} finished and produced a report`, notes };
  }
  if (audit.action === "evaluation.failed") {
    const error = valueText(metadata.error);
    return { title: "Evaluation failed", status: "Failed", summary: error || (name ? `${name} stopped before completion` : `${resource} stopped before completion`), notes };
  }
  if (audit.action === "evaluation.deleted") {
    return { title: "Evaluation deleted", status: "Deleted", summary: `${resource} was removed from the run history`, notes };
  }
  return { title: humanizeAction(audit.action), status: "Event", summary: resource, notes };
}

function valueText(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function humanizeAction(action: string) {
  return action
    .split(".")
    .map((part) => part.replace(/_/g, " "))
    .join(" ")
    .replace(/^\w/, (first) => first.toUpperCase());
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function buildScoreRows(results: Result[]) {
  return SCORE_DEFINITIONS.map((definition) => {
    const values = results
      .map((result) => result.scores[definition.key])
      .filter((value): value is number => typeof value === "number");
    const value = values.length ? values.reduce((sum, next) => sum + next, 0) / values.length : 0;
    return { ...definition, value };
  });
}

function buildAttackRows(results: Result[]) {
  const counts = results.reduce<Record<string, number>>((acc, result) => {
    acc[result.attack_category] = (acc[result.attack_category] ?? 0) + 1;
    return acc;
  }, {});
  return ATTACK_CATEGORIES.map((category) => ({
    ...category,
    count: counts[category.key] ?? 0,
  }));
}

function providerLabel(providerName: string, providers: ProviderInfo[]) {
  return providers.find((provider) => provider.name === providerName)?.label ?? "Mock Provider";
}

function categoryColor(category: string) {
  return {
    jailbreak: "#2563eb",
    injection: "#7c3aed",
    toxicity: "#dc2626",
    hallucination: "#d97706",
    bias: "#0f766e",
    privacy_leakage: "#a855f7",
    misinformation: "#ec4899",
    adversarial: "#06b6d4",
    csam_avoidance: "#991b1b",
  }[category] ?? "#475569";
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
