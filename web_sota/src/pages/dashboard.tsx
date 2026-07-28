import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, BarChart3, Database, FileText, Search, Server, Wifi } from "lucide-react";

type HealthData = {
  status: string;
  server: string;
  version: string;
  uptime_seconds?: number;
  tool_count?: number;
};

type SystemInfo = {
  status: string;
  mcp: string;
};

const CAPABILITIES = [
  { icon: BarChart3, label: "Metrics", desc: "Prometheus query, targets, alerts" },
  { icon: FileText, label: "Logs", desc: "Loki search, tail, anomaly detection" },
  { icon: Database, label: "Dashboards", desc: "Grafana create, list, analyze" },
  { icon: Search, label: "Correlation", desc: "Cross-system root cause analysis" },
];

export function Dashboard() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [sysInfo, setSysInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [h, s] = await Promise.allSettled([
        fetch(`${API_BASE}/api/health`).then(r => r.ok ? r.json() : null),
        fetch(`${API_BASE}/api/status`).then(r => r.ok ? r.json() : null),
      ]);
      if (h.status === "fulfilled" && h.value) setHealth(h.value);
      if (s.status === "fulfilled" && s.value) setSysInfo(s.value);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backend unreachable");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); const iv = setInterval(fetchData, 15000); return () => clearInterval(iv); }, [fetchData]);

  const uptime = health?.uptime_seconds ?? 0;
  const uptimeStr = uptime > 3600
    ? `${Math.floor(uptime / 3600)}h ${Math.floor((uptime % 3600) / 60)}m`
    : uptime > 60
      ? `${Math.floor(uptime / 60)}m ${uptime % 60}s`
      : `${uptime}s`;

  return (
    <div className="space-y-6" data-testid="dashboard">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-950 to-blue-950/40 p-8">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        <div className="relative z-10">
          <div className="flex items-start justify-between">
            <div className="space-y-3 max-w-2xl">
              <div className="flex items-center gap-2">
                <span data-testid="backend-dot" className={`relative flex h-3 w-3 ${error ? "bg-red-500" : loading ? "bg-gray-500" : "bg-emerald-500"} rounded-full`}>
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${error ? "bg-red-400" : "bg-emerald-400"} opacity-75`}></span>
                </span>
                <span className={`text-xs font-medium uppercase tracking-widest ${error ? "text-red-400" : "text-emerald-400"}`}>
                  {loading ? "Connecting..." : error ? "Offline" : "Online"}
                </span>
              </div>

              <h1 className="text-3xl font-bold tracking-tight text-white">
                monitoring-mcp
              </h1>
              <p className="text-base text-slate-300 leading-relaxed">
                An MCP server that connects AI assistants to your Grafana + Prometheus + Loki
                observability stack (local, Docker, or remote). Query metrics, search logs,
                manage dashboards, and correlate incidents across all three — all through
                natural language.
              </p>

              <div className="flex flex-wrap gap-2 pt-1">
                <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 font-mono">Grafana</span>
                <span className="px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-xs text-orange-400 font-mono">Prometheus</span>
                <span className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs text-blue-400 font-mono">Loki</span>
                <span className="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-xs text-purple-400 font-mono">FastMCP</span>
              </div>
            </div>

            <div className="hidden lg:block text-right">
              <div className="text-2xl font-bold text-white">{health?.tool_count ?? "—"}</div>
              <p className="text-xs text-slate-500">MCP tools</p>
            </div>
          </div>
        </div>
      </div>

      {/* Capability cards */}
      <div className="grid gap-3 md:grid-cols-4">
        {CAPABILITIES.map((cap) => (
          <Card key={cap.label} className="border-slate-800 bg-slate-950/50">
            <CardHeader className="flex flex-row items-center gap-3 space-y-0 pb-2">
              <cap.icon className="h-5 w-5 text-blue-500 shrink-0" />
              <div>
                <CardTitle className="text-sm font-medium text-slate-200">{cap.label}</CardTitle>
                <p className="text-xs text-slate-500">{cap.desc}</p>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>

      {/* KPI row */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200" data-testid="kpi-server">Server</CardTitle>
            <Server className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold text-white">{health?.server ?? "—"}</div>
            <p className="text-xs text-slate-400">v{health?.version ?? "?"}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Auth</CardTitle>
            <Wifi className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className={`text-lg font-bold ${error ? "text-red-400" : "text-emerald-400"}`}>
              {error ? "Disconnected" : "Connected"}
            </div>
            <p className="text-xs text-slate-400">{sysInfo?.mcp ?? "monitoring-mcp"}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200" data-testid="kpi-tools">Tools</CardTitle>
            <Database className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{health?.tool_count ?? "—"}</div>
            <p className="text-xs text-slate-400">Registered MCP tools</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Uptime</CardTitle>
            <Activity className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{uptimeStr}</div>
            <p className="text-xs text-slate-400">Since last restart</p>
          </CardContent>
        </Card>
      </div>

      {/* Status panels */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4 border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white text-sm">System Log</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] font-mono text-xs p-4 overflow-y-auto border border-slate-800 rounded-md bg-slate-900/50 text-slate-400 space-y-1">
              {error ? (
                <p className="text-red-400">[ERROR] Backend unreachable: {error}</p>
              ) : (
                <>
                  <p className="text-blue-400">[info] Server {health?.server ?? "?"} v{health?.version ?? "?"} running</p>
                  <p className="text-emerald-400">[info] {health?.tool_count ?? 0} MCP tools registered</p>
                  <p className="text-slate-500">[info] Server: {sysInfo?.mcp ?? "monitoring-mcp"}</p>
                  <div className="animate-pulse inline-block h-2 w-1 bg-slate-500 ml-1" />
                </>
              )}
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-3 border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white text-sm">Connection Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className={`relative flex h-2 w-2 ${error ? "bg-red-500" : "bg-emerald-500"}`}>
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${error ? "bg-red-400" : "bg-emerald-400"} opacity-75`}></span>
                </span>
                <div className="space-y-0.5">
                  <p className="text-sm font-medium leading-none text-white">Backend</p>
                  <p className="text-xs text-slate-500">{error ? "Unreachable" : `Up ${uptimeStr}`}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-slate-600">
                <span className="h-2 w-2 rounded-full bg-slate-700" />
                <div className="space-y-0.5">
                  <p className="text-sm font-medium leading-none text-slate-500">Grafana</p>
                  <p className="text-xs text-slate-600">Awaiting query</p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-slate-600">
                <span className="h-2 w-2 rounded-full bg-slate-700" />
                <div className="space-y-0.5">
                  <p className="text-sm font-medium leading-none text-slate-500">Prometheus</p>
                  <p className="text-xs text-slate-600">Awaiting query</p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-slate-600">
                <span className="h-2 w-2 rounded-full bg-slate-700" />
                <div className="space-y-0.5">
                  <p className="text-sm font-medium leading-none text-slate-500">Loki</p>
                  <p className="text-xs text-slate-600">Awaiting query</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
