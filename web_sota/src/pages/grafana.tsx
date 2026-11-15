import { useCallback, useEffect, useState } from "react";
import { apiJSON } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Database, FolderOpen, Plus, Rocket, Trash2 } from "lucide-react";

type Dashboard = { uid?: string; title?: string; tags?: string[]; url?: string; folderTitle?: string };
type Datasource = { id?: number; name?: string; type?: string; url?: string; isDefault?: boolean };

export function Grafana() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [datasources, setDatasources] = useState<Datasource[]>([]);
  const [folders, setFolders] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [provisioning, setProvisioning] = useState(false);
  const [provisionMsg, setProvisionMsg] = useState<string | null>(null);

  // Create-dashboard form (active setup)
  const [newTitle, setNewTitle] = useState("Fleet Service Health");
  const [newExpr, setNewExpr] = useState("up");
  const [creating, setCreating] = useState(false);
  const [stackHost, setStackHost] = useState<string | null>(null);

  const load = useCallback(async (q = "") => {
    setLoading(true);
    try {
      const params = q ? `?q=${encodeURIComponent(q)}` : "";
      const [d, ds, f, cfg] = await Promise.all([
        apiJSON(`/api/grafana/dashboards${params}`),
        apiJSON("/api/grafana/datasources"),
        apiJSON("/api/grafana/folders"),
        apiJSON("/api/monitoring/config").catch(() => null),
      ]);
      if (d?.error) throw new Error(d.error);
      setDashboards(d?.dashboards ?? []);
      setDatasources(ds?.datasources ?? []);
      setFolders(f?.folders ?? []);
      setStackHost(cfg?.grafana_url ?? null);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Grafana unreachable (auth? URL?)");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const provision = async () => {
    setProvisioning(true);
    setProvisionMsg(null);
    try {
      const res = await apiJSON("/api/grafana/provision/fleet-overview", { method: "POST" });
      if (res?.error) throw new Error(res.error);
      setProvisionMsg(`Provisioned Fleet Overview (folder ${res?.folderId ?? "?"}). Reloading…`);
      await load(search);
    } catch (e) {
      setProvisionMsg(`Provision failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setProvisioning(false);
    }
  };

  const createDashboard = async () => {
    if (!newTitle.trim() || !newExpr.trim()) return;
    setCreating(true);
    try {
      const fleet = folders.find((f) => String(f?.title).toLowerCase() === "fleet");
      const dashboard = {
        title: newTitle.trim(),
        tags: ["monitoring-mcp", "created-by-webapp"],
        refresh: "30s",
        time: { from: "now-1h", to: "now" },
        panels: [
          {
            id: 1,
            title: newExpr,
            type: "timeseries",
            gridPos: { h: 12, w: 24, x: 0, y: 0 },
            targets: [{ expr: newExpr, refId: "A" }],
          },
        ],
      };
      const res = await apiJSON("/api/grafana/dashboards", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dashboard, folderId: fleet?.id ?? undefined }),
      });
      if (res?.error) throw new Error(res.error);
      setNewTitle("");
      await load(search);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Create failed");
    } finally {
      setCreating(false);
    }
  };

  const removeDashboard = async (uid?: string) => {
    if (!uid || !confirm(`Delete dashboard ${uid}?`)) return;
    try {
      await apiJSON(`/api/grafana/dashboard/${encodeURIComponent(uid)}`, { method: "DELETE" });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
      return;
    }
    await load(search);
  };

  return (
    <div className="space-y-6" data-testid="grafana-page">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Grafana — Dashboards</h2>
          <p className="text-slate-400">
            {loading ? "Loading…" : `${dashboards.length} dashboards · ${datasources.length} datasources · ${folders.length} folders`}
            {stackHost ? ` · talking to ${stackHost}` : ""}
          </p>
        </div>
        <div className="flex gap-2">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && load(search)}
            placeholder="Search dashboards…"
            className="bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
          <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800" onClick={() => load(search)}>
            Search
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white" onClick={provision} disabled={provisioning}>
            <Rocket className="mr-2 h-4 w-4" /> {provisioning ? "Provisioning…" : "Provision Fleet Overview"}
          </Button>
        </div>
      </div>

      {error && <p className="text-sm text-red-400">Grafana error: {error}</p>}
      {provisionMsg && <p className="text-sm text-emerald-400">{provisionMsg}</p>}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-sm text-white flex items-center gap-2">
              <Database className="h-4 w-4 text-purple-500" /> Datasources
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1.5 text-xs">
            {datasources.length === 0 && <p className="text-slate-500">No datasources — provision Prometheus + Loki in Grafana first.</p>}
            {datasources.map((ds, i) => (
              <div key={i} className="flex items-center gap-2 rounded border border-slate-800 px-2 py-1.5">
                <span className="text-slate-200 font-medium">{ds.name}</span>
                <span className="text-slate-500 font-mono">{ds.type}</span>
                {ds.isDefault && <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-400">default</span>}
                <span className="text-slate-600 font-mono ml-auto truncate max-w-[200px]">{ds.url}</span>
              </div>
            ))}
            {folders.length > 0 && (
              <p className="pt-2 text-slate-500 flex items-center gap-1">
                <FolderOpen className="h-3 w-3" /> {folders.map((f) => f.title).join(" · ")}
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-sm text-white flex items-center gap-2">
              <Plus className="h-4 w-4 text-emerald-500" /> New dashboard (active setup)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Dashboard title"
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
            <input
              value={newExpr}
              onChange={(e) => setNewExpr(e.target.value)}
              placeholder="PromQL expr, e.g. up"
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-white font-mono focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
            <Button className="w-full bg-emerald-600 hover:bg-emerald-700 text-white" onClick={createDashboard} disabled={creating}>
              {creating ? "Creating…" : "Create dashboard in Grafana"}
            </Button>
            <p className="text-[11px] text-slate-600">Creates a one-panel timeseries dashboard in the Fleet folder (or General). Full JSON editing lives in Grafana itself.</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-sm text-white">Dashboards ({dashboards.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {dashboards.length === 0 && !loading && (
            <p className="text-xs text-slate-500 py-6 text-center">No dashboards yet — hit “Provision Fleet Overview” to create the first one.</p>
          )}
          <div className="grid gap-2 md:grid-cols-2">
            {dashboards.map((d, i) => (
              <div key={d.uid ?? i} className="flex items-center gap-2 rounded border border-slate-800 px-3 py-2">
                <div className="min-w-0">
                  <p className="text-sm text-slate-200 truncate">{d.title ?? d.uid}</p>
                  <p className="text-[11px] text-slate-500 font-mono truncate">{(d.tags ?? []).join(", ")}{d.folderTitle ? ` · ${d.folderTitle}` : ""}</p>
                </div>
                <Button variant="ghost" size="icon" className="ml-auto h-8 w-8 text-slate-500 hover:text-red-400" onClick={() => removeDashboard(d.uid)} title="Delete">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
