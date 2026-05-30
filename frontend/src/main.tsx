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
  Trash2,
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
  created_at: string;
};

type Report = {
  id: string;
  run_id: string;
  json_payload: {
    aggregate_score?: number;
    result_count?: number;
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
  const [selectedProvider, setSelectedProvider] = React.useState("mock");
  const [modelVersion, setModelVersion] = React.useState("v1");
  const [mutationDepth, setMutationDepth] = React.useState(2);
  const [notice, setNotice] = React.useState<string | null>(null);

  const headers = React.useMemo(() => ({ "X-Role": "admin", "X-Actor-Id": "dashboard" }), []);

  const loadRunDetails = React.useCallback(async (runId: string | null) => {
    if (!runId) {
      setResults([]);
      setReports([]);
      return;
    }
    const resultResponse = await fetch(`${API_URL}/api/v1/evaluations/${runId}/results`, { headers });
    setResults(await resultResponse.json());
    const reportResponse = await fetch(`${API_URL}/api/v1/reports?run_id=${runId}`, { headers });
    setReports(await reportResponse.json());
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
        categories: ["jailbreak", "injection", "toxicity", "hallucination", "bias"],
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

  const deleteRun = async (runId: string) => {
    if (!confirm("Are you sure you want to delete this evaluation run? This action cannot be undone.")) {
      return;
    }
    await fetch(`${API_URL}/api/v1/evaluations/${runId}`, {
      method: "DELETE",
      headers,
    });
    setSelectedRun(null);
    await refresh();
  };

  const deleteAuditLog = async (logId: string) => {
    if (!confirm("Are you sure you want to delete this audit log?")) {
      return;
    }
    await fetch(`${API_URL}/api/v1/audit-logs/${logId}`, {
      method: "DELETE",
      headers,
    });
    await refresh();
  };

  const selected = runs.find((run) => run.id === selectedRun) ?? runs[0];
  const aggregate = selected?.aggregate_score ?? 0;
  const scoreRows = buildScoreRows(results);
  const severityRows = Object.entries(
    results.reduce<Record<string, number>>((acc, result) => {
      acc[result.attack_category] = (acc[result.attack_category] ?? 0) + 1;
      return acc;
    }, {})
  ).map(([category, count]) => ({ category, count }));
  const trend = runs.slice().reverse().map((run) => ({ name: run.model_version, score: run.aggregate_score ?? 0 }));
  const selectedProviderInfo = providers.find((provider) => provider.name === selectedProvider);
  const providerUnavailable = Boolean(selectedProviderInfo && !selectedProviderInfo.ready);

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
  const auditSuccessAll = sortedAudits.filter((a) => !/failed|failure|error/i.test(a.action));
  const auditFailedAll = sortedAudits.filter((a) => /failed|failure|error/i.test(a.action));
  const latestAuditSuccess = auditSuccessAll.slice(0, latestCount);
  const latestAuditFailed = auditFailedAll.slice(0, latestCount);
  const moreAuditSuccess = auditSuccessAll.slice(latestCount);
  const moreAuditFailed = auditFailedAll.slice(latestCount);

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <ShieldAlert size={24} />
          <span>Safety Eval</span>
        </div>
        <nav>
          <a href="#overview"><Gauge size={18} /> Overview</a>
          <a href="#configure"><KeyRound size={18} /> Providers</a>
          <a href="#scores"><Sparkles size={18} /> Scores</a>
          <a href="#runs"><ClipboardList size={18} /> Runs</a>
          <a href="#attacks"><ShieldAlert size={18} /> Attacks</a>
          <a href="#regression"><GitCompare size={18} /> Regression</a>
          <a href="#audit"><History size={18} /> Audit</a>
          <a href="#reports"><FileText size={18} /> Reports</a>
        </nav>
      </aside>

      <section className="content">
        <header className="hero">
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

        <section id="configure" className="control-panel">
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
        </section>

        <section id="overview" className="metrics-grid">
          <Metric title="Aggregate Safety Score" value={`${aggregate.toFixed(1)}`} tone={aggregate >= 70 ? "good" : "risk"} />
          <Metric title="Active Runs" value={`${runs.filter((run) => ["queued", "running"].includes(run.status)).length}`} />
          <Metric title="Attack Results" value={`${results.length}`} />
          <Metric title="Audit Events" value={`${audits.length}`} />
        </section>

        <section id="scores" className="panel score-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title"><Sparkles size={18} /> Individual Safety Scores</div>
              <p>Each card shows risk for one safety dimension. Lower risk is better; the aggregate safety score converts those risks into an overall safety number.</p>
            </div>
            <button className="secondary-action" onClick={() => refresh()}><RefreshCw size={16} /> Refresh</button>
          </div>
          <div className="score-grid">
            {scoreRows.map((score) => (
              <ScoreCard key={score.key} score={score} />
            ))}
          </div>
        </section>

        <section className="split">
          <div id="runs" className="panel">
            <div className="panel-title"><Activity size={18} /> Evaluation Run Tracking</div>
            <div className="run-columns">
              <div className="run-column">
                <div className="column-header">Success ({successfulRunsAll.length})</div>
                <div className="run-list">
                  {latestSuccessfulRuns.map((run) => (
                    <div className={run.id === selected?.id ? "run selected" : "run"} key={run.id} role="button" tabIndex={0} onClick={() => setSelectedRun(run.id)}>
                      <span>{run.name}</span>
                      <div className="run-meta"><strong>{run.status}</strong><small>{run.provider} / {run.model_version}</small></div>
                      <progress value={run.progress} max="1" />
                      <button className="delete-btn" onClick={(e) => { e.stopPropagation(); deleteRun(run.id); }} title="Delete run"><Trash2 size={14} /></button>
                    </div>
                  ))}
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
                          <button className="delete-btn" onClick={(e) => { e.stopPropagation(); deleteRun(run.id); }} title="Delete run"><Trash2 size={14} /></button>
                        </div>
                      ))}
                    </div>
                  </details>
                ) : null}
              </div>
              <div className="run-column">
                <div className="column-header">Failed ({failedRunsAll.length})</div>
                <div className="run-list">
                  {latestFailedRuns.map((run) => (
                    <div className={run.id === selected?.id ? "run selected" : "run"} key={run.id} role="button" tabIndex={0} onClick={() => setSelectedRun(run.id)}>
                      <span>{run.name}</span>
                      <div className="run-meta"><strong>{run.status}</strong><small>{run.provider} / {run.model_version}</small></div>
                      <progress value={run.progress} max="1" />
                      <button className="delete-btn" onClick={(e) => { e.stopPropagation(); deleteRun(run.id); }} title="Delete run"><Trash2 size={14} /></button>
                    </div>
                  ))}
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
                          <button className="delete-btn" onClick={(e) => { e.stopPropagation(); deleteRun(run.id); }} title="Delete run"><Trash2 size={14} /></button>
                        </div>
                      ))}
                    </div>
                  </details>
                ) : null}
              </div>
            </div>
          </div>
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
                  <strong>{trend.length > 1 && trend[trend.length - 1].score > trend[0].score ? "📈 Improving" : trend.length > 1 ? "📉 Declining" : "—"}</strong>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="split">
          <div id="attacks" className="panel">
            <div className="panel-title"><ShieldAlert size={18} /> Attack Analysis</div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={severityRows}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count">
                  {severityRows.map((row) => (
                    <Cell key={row.category} fill={categoryColor(row.category)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div id="audit" className="panel">
            <div className="panel-title"><History size={18} /> Audit Log Timeline</div>
            <div className="audit-columns">
              <div className="audit-column">
                <div className="column-header">Success Events ({auditSuccessAll.length})</div>
                <div className="timeline">
                  {latestAuditSuccess.map((audit) => (
                    <div className="event" key={audit.id}>
                      <div className="event-header">
                        <div>
                          <strong>{audit.action}</strong>
                          <span>{audit.resource_type} {audit.resource_id?.slice(0, 8)}</span>
                        </div>
                        <button className="delete-btn-small" onClick={() => deleteAuditLog(audit.id)} title="Delete audit log"><Trash2 size={12} /></button>
                      </div>
                    </div>
                  ))}
                </div>
                {moreAuditSuccess.length > 0 ? (
                  <details className="history-dropdown">
                    <summary>History</summary>
                    <div className="timeline history-list">
                      {moreAuditSuccess.map((audit) => (
                        <div className="event" key={audit.id}>
                          <div className="event-header">
                            <div>
                              <strong>{audit.action}</strong>
                              <span>{audit.resource_type} {audit.resource_id?.slice(0, 8)}</span>
                            </div>
                            <button className="delete-btn-small" onClick={() => deleteAuditLog(audit.id)} title="Delete audit log"><Trash2 size={12} /></button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                ) : null}
              </div>
              <div className="audit-column">
                <div className="column-header">Failed Events ({auditFailedAll.length})</div>
                <div className="timeline">
                  {latestAuditFailed.map((audit) => (
                    <div className="event failed" key={audit.id}>
                      <div className="event-header">
                        <div>
                          <strong>{audit.action}</strong>
                          <span>{audit.resource_type} {audit.resource_id?.slice(0, 8)}</span>
                        </div>
                        <button className="delete-btn-small" onClick={() => deleteAuditLog(audit.id)} title="Delete audit log"><Trash2 size={12} /></button>
                      </div>
                    </div>
                  ))}
                </div>
                {moreAuditFailed.length > 0 ? (
                  <details className="history-dropdown">
                    <summary>History</summary>
                    <div className="timeline history-list">
                      {moreAuditFailed.map((audit) => (
                        <div className="event failed" key={audit.id}>
                          <div className="event-header">
                            <div>
                              <strong>{audit.action}</strong>
                              <span>{audit.resource_type} {audit.resource_id?.slice(0, 8)}</span>
                            </div>
                            <button className="delete-btn-small" onClick={() => deleteAuditLog(audit.id)} title="Delete audit log"><Trash2 size={12} /></button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                ) : null}
              </div>
            </div>
          </div>
        </section>

        <section id="reports" className="panel">
          <div className="panel-title"><FileText size={18} /> Report Generation</div>
          <div className="report-grid">
            {reports.map((report) => (
              <a className="report" key={report.id} href={`${API_URL}/api/v1/reports/${report.id}/pdf`} target="_blank" rel="noreferrer">
                <strong>Report {report.id.slice(0, 8)}</strong>
                <span>{report.json_payload.result_count ?? 0} results</span>
                <span>Score {report.json_payload.aggregate_score ?? "pending"}</span>
              </a>
            ))}
          </div>
        </section>
      </section>
    </main>
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

function buildScoreRows(results: Result[]) {
  return SCORE_DEFINITIONS.map((definition) => {
    const values = results
      .map((result) => result.scores[definition.key])
      .filter((value): value is number => typeof value === "number");
    const value = values.length ? values.reduce((sum, next) => sum + next, 0) / values.length : 0;
    return { ...definition, value };
  });
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
  }[category] ?? "#475569";
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
