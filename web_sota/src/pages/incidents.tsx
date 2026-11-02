import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, HeartPulse, Search } from "lucide-react";

export function Incidents() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [description, setDescription] = useState("fleet targets flapping, errors in logs");
  const [service, setService] = useState("");
  const [metricQuery, setMetricQuery] = useState("up == 0");
  const [logQuery, setLogQuery] = useState('{job=~".+"} |= "error"');
  const [incident, setIncident] = useState<any>(null);
  const [correlating, setCorrelating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/correlation/health`).then((x) => x.json());
      if (res?.error) throw new Error(res.error);
      setHealth(res);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backend unreachable");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const iv = setInterval(load, 60000);
    return () => clearInterval(iv);
  }, [load]);

  const correlate = async () => {
    if (!description.trim()) return;
    setCorrelating(true);
    try {
      const res = await fetch(`${API_BASE}/api/correlation/incident`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_description: description,
          service_name: service || undefined,
          metric_query: metricQuery,
          log_query: logQuery,
        }),
      }).then((x) => x.json());
      setIncident(res);
    } finally {
      setCorrelating(false);
    }
  };

  const components = health?.health?.components ?? {};
  const issues = health?.health?.issues ?? [];
  const overall = health?.health?.overall_status ?? "unknown";

  return (
    <div className="space-y-6" data-testid="incidents-page">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Incidents — Correlation</h2>
          <p className="text-slate-400">
            {loading ? "Loading…" : `Overall: ${overall} · ${issues.length} open issues`}
          </p>
        </div>
        <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800" onClick={load}>
          Refresh
        </Button>
      </div>

      {error && <p className="text-sm text-red-400">Correlation error: {error}</p>}

      <div className="grid gap-4 md:grid-cols-3">
        {["grafana", "prometheus", "loki"].map((name) => {
          const c = components[name];
          const ok = c?.status === "healthy";
          return (
            <Card key={name} className="border-slate-800 bg-slate-950/50">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm text-slate-200 capitalize">{name}</CardTitle>
                <HeartPulse className={`h-4 w-4 ${ok ? "text-emerald-500" : "text-red-500"}`} />
              </CardHeader>
              <CardContent>
                <p className={`text-lg font-bold ${ok ? "text-emerald-400" : "text-red-400"}`}>{c?.status ?? "unknown"}</p>
                <p className="text-xs text-slate-500">{c?.details ?? c?.error ?? "—"}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {issues.length > 0 && (
        <Card className="border-red-900/40 bg-red-950/10">
          <CardHeader>
            <CardTitle className="text-sm text-red-300 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" /> Open issues ({issues.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1.5 text-xs">
            {issues.map((iss: any, i: number) => (
              <div key={i} className="rounded border border-red-900/30 px-2 py-1 text-slate-300">
                <span className="font-mono text-red-400">[{iss.component}/{iss.severity}]</span> {iss.description}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-sm text-white flex items-center gap-2">
            <Search className="h-4 w-4 text-yellow-500" /> Correlate incident (metrics + logs)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            placeholder="What is happening? e.g. plex-mcp down, 5xx spike on gateway"
            className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-yellow-500"
          />
          <div className="grid gap-2 md:grid-cols-3">
            <input value={service} onChange={(e) => setService(e.target.value)} placeholder="service filter (optional)" className="bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white font-mono" />
            <input value={metricQuery} onChange={(e) => setMetricQuery(e.target.value)} placeholder="metric query" className="bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white font-mono" />
            <input value={logQuery} onChange={(e) => setLogQuery(e.target.value)} placeholder="log query" className="bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white font-mono" />
          </div>
          <Button className="bg-yellow-600 hover:bg-yellow-700 text-white" onClick={correlate} disabled={correlating || !description.trim()}>
            {correlating ? "Correlating…" : "Run correlation"}
          </Button>
          {incident && (
            <div className="rounded border border-slate-800 bg-slate-950 p-3 text-xs">
              {incident?.error && <p className="text-red-400">Error: {incident.error}</p>}
              {incident?.conversational_summary && <p className="text-slate-200 pb-2">{incident.conversational_summary}</p>}
              <pre className="max-h-96 overflow-auto text-slate-400 whitespace-pre-wrap">{JSON.stringify(incident?.data ?? incident?.correlation ?? incident, null, 2).slice(0, 8000)}</pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
