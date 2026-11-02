import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, AlertTriangle, Play, Server } from "lucide-react";

type Target = {
  labels?: Record<string, string>;
  scrapeUrl?: string;
  globalUrl?: string;
  health?: string;
  lastError?: string;
  lastScrape?: string;
  lastScrapeDuration?: number;
};

type QueryValue = [number, string];
type QuerySeries = { metric: Record<string, string>; value?: QueryValue; values?: QueryValue[] };

function Sparkline({ values }: { values: number[] }) {
  if (values.length < 2) return <span className="text-xs text-slate-600">not enough points</span>;
  const w = 320;
  const h = 64;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const pts = values.map((v, i) => `${(i / (values.length - 1)) * w},${h - ((v - min) / span) * (h - 8) - 4}`).join(" ");
  return (
    <svg width={w} height={h} className="w-full rounded bg-slate-900/60 border border-slate-800">
      <polyline points={pts} fill="none" stroke="#34d399" strokeWidth={1.5} />
    </svg>
  );
}

export function Prometheus() {
  const [targets, setTargets] = useState<Target[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [build, setBuild] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [query, setQuery] = useState("up");
  const [qResult, setQResult] = useState<QuerySeries[]>([]);
  const [qRunning, setQRunning] = useState(false);
  const [range, setRange] = useState({ start: "now-1h", end: "now", step: "5m" });
  const [rValues, setRValues] = useState<number[]>([]);
  const [rRunning, setRRunning] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [t, a, r, b] = await Promise.all([
        fetch(`${API_BASE}/api/prometheus/targets`).then((x) => x.json()),
        fetch(`${API_BASE}/api/prometheus/alerts`).then((x) => x.json()),
        fetch(`${API_BASE}/api/prometheus/rules`).then((x) => x.json()),
        fetch(`${API_BASE}/api/prometheus/build`).then((x) => (x.ok ? x.json() : null)),
      ]);
      setTargets(t?.data?.activeTargets ?? []);
      setAlerts(a?.data?.alerts ?? []);
      setRules(r?.data?.groups ?? []);
      setBuild(b?.data ?? b ?? null);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backend unreachable");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const iv = setInterval(load, 30000);
    return () => clearInterval(iv);
  }, [load]);

  const runQuery = async () => {
    setQRunning(true);
    try {
      const res = await fetch(`${API_BASE}/api/prometheus/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      }).then((x) => x.json());
      setQResult(res?.data?.result ?? []);
    } finally {
      setQRunning(false);
    }
  };

  const runRange = async () => {
    setRRunning(true);
    try {
      const res = await fetch(`${API_BASE}/api/prometheus/query_range`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, ...range }),
      }).then((x) => x.json());
      const first: QuerySeries | undefined = res?.data?.result?.[0];
      setRValues((first?.values ?? []).map((v) => parseFloat(v[1])).filter((n) => !Number.isNaN(n)));
    } finally {
      setRRunning(false);
    }
  };

  const up = targets.filter((t) => t.health === "up").length;
  const firing = alerts.filter((a) => a?.state === "firing").length;

  return (
    <div className="space-y-6" data-testid="prometheus-page">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Prometheus — Metrics</h2>
          <p className="text-slate-400">
            {loading ? "Loading…" : `${up}/${targets.length} targets up · ${firing} firing alerts`}
            {build?.version ? ` · v${build.version}` : ""}
          </p>
        </div>
        <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800" onClick={load}>
          Refresh
        </Button>
      </div>

      {error && <p className="text-sm text-red-400">Backend error: {error}</p>}

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-sm text-white flex items-center gap-2">
            <Play className="h-4 w-4 text-emerald-500" /> PromQL — instant + range
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2 flex-wrap">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && runQuery()}
              placeholder='e.g. up, 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
              className="flex-1 min-w-[280px] bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white font-mono focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
            <Button className="bg-emerald-600 hover:bg-emerald-700 text-white" onClick={runQuery} disabled={qRunning}>
              {qRunning ? "Running…" : "Query"}
            </Button>
            <Button variant="outline" className="border-slate-700" onClick={runRange} disabled={rRunning}>
              {rRunning ? "Loading…" : "Range chart"}
            </Button>
          </div>
          <div className="flex gap-2 text-xs flex-wrap">
            {(["up", "up == 0", "node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes"] as string[]).map((q) => (
              <button key={q} onClick={() => setQuery(q)} className="px-2 py-1 rounded border border-slate-700 text-slate-400 font-mono hover:bg-slate-800">
                {q}
              </button>
            ))}
            <span className="ml-auto flex gap-1 items-center text-slate-500">
              <input value={range.start} onChange={(e) => setRange({ ...range, start: e.target.value })} className="w-20 bg-slate-950 border border-slate-800 rounded px-1 py-0.5 font-mono" />
              →
              <input value={range.end} onChange={(e) => setRange({ ...range, end: e.target.value })} className="w-20 bg-slate-950 border border-slate-800 rounded px-1 py-0.5 font-mono" />
              @
              <input value={range.step} onChange={(e) => setRange({ ...range, step: e.target.value })} className="w-14 bg-slate-950 border border-slate-800 rounded px-1 py-0.5 font-mono" />
            </span>
          </div>
          {rValues.length > 0 && <Sparkline values={rValues} />}
          {qResult.length > 0 && (
            <div className="max-h-64 overflow-auto rounded border border-slate-800 font-mono text-xs">
              <table className="w-full text-left">
                <thead className="bg-slate-900 text-slate-400 sticky top-0">
                  <tr><th className="px-2 py-1">metric</th><th className="px-2 py-1">value</th></tr>
                </thead>
                <tbody>
                  {qResult.slice(0, 100).map((s, i) => (
                    <tr key={i} className="border-t border-slate-800/50 text-slate-300">
                      <td className="px-2 py-1 break-all">{JSON.stringify(s.metric)}</td>
                      <td className="px-2 py-1 text-emerald-400">{s.value?.[1] ?? `${s.values?.length ?? 0} pts`}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-sm text-white flex items-center gap-2">
              <Server className="h-4 w-4 text-blue-500" /> Scrape targets ({targets.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="max-h-80 overflow-auto rounded border border-slate-800 text-xs font-mono">
              <table className="w-full text-left">
                <thead className="bg-slate-900 text-slate-400 sticky top-0">
                  <tr><th className="px-2 py-1">job</th><th className="px-2 py-1">instance</th><th className="px-2 py-1">health</th></tr>
                </thead>
                <tbody>
                  {targets.map((t, i) => (
                    <tr key={i} className="border-t border-slate-800/50" title={t.lastError || t.scrapeUrl}>
                      <td className="px-2 py-1 text-slate-300">{t.labels?.job ?? "?"}</td>
                      <td className="px-2 py-1 text-slate-500 break-all">{t.labels?.instance ?? t.scrapeUrl}</td>
                      <td className={`px-2 py-1 font-bold ${t.health === "up" ? "text-emerald-400" : "text-red-400"}`}>{t.health}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-sm text-white flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-yellow-500" /> Alerts ({alerts.length}) · Rules ({rules.length} groups)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            {alerts.length === 0 && <p className="text-slate-500">No active alerts — quiet.</p>}
            {alerts.slice(0, 20).map((a, i) => (
              <div key={i} className="flex items-center gap-2 rounded border border-slate-800 px-2 py-1">
                <span className={`font-bold ${a.state === "firing" ? "text-red-400" : "text-yellow-400"}`}>{a.state}</span>
                <span className="text-slate-300 font-mono">{a?.labels?.alertname ?? "?"}</span>
                <span className="text-slate-600 ml-auto">{a?.activeAt ?? ""}</span>
              </div>
            ))}
            {rules.length > 0 && (
              <div className="pt-2 text-slate-500">
                <span className="flex items-center gap-1"><Activity className="h-3 w-3" /> Rule groups:</span>
                <div className="flex flex-wrap gap-1 pt-1">
                  {rules.slice(0, 12).map((g, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 font-mono">{g.name} ({g.rules?.length ?? 0})</span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
