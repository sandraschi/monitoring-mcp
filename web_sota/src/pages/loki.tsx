import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Play, Tags } from "lucide-react";

type LokiStream = { stream: Record<string, string>; values: [string, string][] };

export function Loki() {
  const [labels, setLabels] = useState<string[]>([]);
  const [labelValues, setLabelValues] = useState<Record<string, string[]>>({});
  const [query, setQuery] = useState('{job=~".+"} |= "error"');
  const [limit, setLimit] = useState(100);
  const [streams, setStreams] = useState<LokiStream[]>([]);
  const [totalEntries, setTotalEntries] = useState(0);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLabels = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/loki/labels`).then((x) => x.json());
      setLabels(res?.data ?? []);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Loki unreachable");
    }
  }, []);

  useEffect(() => {
    loadLabels();
  }, [loadLabels]);

  const loadValues = async (name: string) => {
    if (labelValues[name]) return;
    const res = await fetch(`${API_BASE}/api/loki/label/${encodeURIComponent(name)}/values`).then((x) => x.json());
    setLabelValues((prev) => ({ ...prev, [name]: res?.data ?? [] }));
  };

  const runQuery = async (range = false) => {
    setRunning(true);
    try {
      const endpoint = range ? "/api/loki/query_range" : "/api/loki/query";
      const body = range
        ? { query, start: "now-1h", end: "now", limit }
        : { query, limit };
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then((x) => x.json());
      const result: LokiStream[] = res?.data?.result ?? [];
      setStreams(result);
      setTotalEntries(result.reduce((n, s) => n + s.values.length, 0));
      setError(res?.error ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Query failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="loki-page">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Loki — Logs</h2>
          <p className="text-slate-400">LogQL search across the unified-loki stack</p>
        </div>
        <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800" onClick={loadLabels}>
          Reload labels
        </Button>
      </div>

      {error && <p className="text-sm text-red-400">Loki error: {error}</p>}

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-sm text-white flex items-center gap-2">
            <Play className="h-4 w-4 text-blue-500" /> LogQL
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2 flex-wrap">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && runQuery(false)}
              placeholder='{job="promtail"} |= "error"'
              className="flex-1 min-w-[280px] bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white font-mono focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <select value={limit} onChange={(e) => setLimit(Number(e.target.value))} className="bg-slate-950 border border-slate-800 rounded-md px-2 py-2 text-sm text-slate-300">
              {[25, 50, 100, 250, 500].map((n) => (
                <option key={n} value={n}>{n} lines</option>
              ))}
            </select>
            <Button className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => runQuery(false)} disabled={running}>
              {running ? "Running…" : "Query"}
            </Button>
            <Button variant="outline" className="border-slate-700" onClick={() => runQuery(true)} disabled={running}>
              Last hour
            </Button>
          </div>
          <div className="flex gap-2 text-xs flex-wrap">
            {['{job=~".+"} |= "error"', '{job=~".+"} |= "exception"', '{job=~".+"} |~ "(?i)timeout|refused"'].map((q) => (
              <button key={q} onClick={() => setQuery(q)} className="px-2 py-1 rounded border border-slate-700 text-slate-400 font-mono hover:bg-slate-800">
                {q}
              </button>
            ))}
          </div>
          <p className="text-xs text-slate-500">{totalEntries} entries · {streams.length} streams</p>
          <div className="max-h-[50vh] overflow-auto rounded border border-slate-800 bg-slate-950 p-2 font-mono text-xs leading-relaxed">
            {streams.length === 0 && <p className="text-slate-600 text-center py-8">No results yet — run a query.</p>}
            {streams.slice(0, 30).map((s, i) => (
              <div key={i} className="mb-2">
                <p className="text-slate-500 text-[10px]">{JSON.stringify(s.stream)}</p>
                {s.values.slice(-50).map(([ts, line], j) => (
                  <div key={j} className="flex gap-2 py-px hover:bg-slate-900/60 rounded px-1">
                    <span className="text-slate-600 shrink-0">{ts.slice(0, 19).replace("T", " ")}</span>
                    <span className={`break-all ${/error|exception|fail/i.test(line) ? "text-red-300" : "text-slate-300"}`}>{line.slice(0, 500)}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-sm text-white flex items-center gap-2">
            <Tags className="h-4 w-4 text-purple-500" /> Labels ({labels.length}) <FileText className="h-3 w-3 text-slate-600" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          {labels.length === 0 && <p className="text-xs text-slate-500">No labels — is Loki ingesting? Check promtail targets.</p>}
          <div className="flex flex-wrap gap-1.5">
            {labels.map((name) => (
              <button
                key={name}
                onClick={() => loadValues(name)}
                title={(labelValues[name] ?? []).slice(0, 10).join(", ") || "click to load values"}
                className="px-2 py-1 rounded bg-slate-900 border border-slate-800 font-mono text-xs text-slate-300 hover:bg-slate-800"
              >
                {name}
                {labelValues[name] ? ` (${labelValues[name].length})` : ""}
              </button>
            ))}
          </div>
          {Object.entries(labelValues).filter(([, v]) => v.length > 0).map(([name, vals]) => (
            <p key={name} className="pt-2 text-xs font-mono text-slate-500">
              <span className="text-slate-300">{name}:</span> {vals.slice(0, 12).join(", ")}
              {vals.length > 12 ? ` …+${vals.length - 12}` : ""}
            </p>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
