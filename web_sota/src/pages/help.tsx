import * as Tabs from "@radix-ui/react-tabs";
import { Activity, BarChart3, BookOpen, Bug, Database, FileText, Globe, Server, Terminal, Wrench } from "lucide-react";

const TABS = [
  { id: "overview", label: "Overview", icon: Activity },
  { id: "install", label: "Install", icon: Terminal },
  { id: "config", label: "Configuration", icon: Server },
  { id: "tools", label: "Tools", icon: Wrench },
  { id: "prometheus", label: "Prometheus", icon: BarChart3 },
  { id: "loki", label: "Loki", icon: FileText },
  { id: "grafana", label: "Grafana", icon: Database },
  { id: "dev", label: "Development", icon: BookOpen },
  { id: "links", label: "Links", icon: Globe },
  { id: "trouble", label: "Troubleshooting", icon: Bug },
];

function Code({ children }: { children: string }) {
  return <code className="text-xs bg-slate-900 px-1.5 py-0.5 rounded text-slate-300 font-mono">{children}</code>;
}

function TabContent({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <Tabs.Content value={id} className="outline-none data-[state=active]:animate-in fade-in duration-200">
      <div className="text-sm text-slate-300 space-y-4 leading-relaxed">
        {children}
      </div>
    </Tabs.Content>
  );
}

export function Help() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Help & Documentation</h2>
        <p className="text-slate-400">Reference guides for monitoring-mcp</p>
      </div>

      <Tabs.Root defaultValue="overview" className="space-y-4">
        <Tabs.List className="flex gap-1 border-b border-slate-800 overflow-x-auto pb-px" role="tablist">
          {TABS.map((tab) => (
            <Tabs.Trigger
              key={tab.id}
              value={tab.id}
              className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-slate-500 data-[state=active]:text-white data-[state=active]:border-b-2 data-[state=active]:border-blue-500 hover:text-slate-300 transition-colors whitespace-nowrap outline-none"
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        {/* ── Overview ─────────────────────────────────────────────── */}
        <TabContent id="overview">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-white font-semibold mb-2">What is monitoring-mcp?</h3>
              <p>An MCP server that connects AI assistants (Claude Desktop, Cursor, custom clients) to your <span className="text-emerald-400">Grafana</span> + <span className="text-orange-400">Prometheus</span> + <span className="text-blue-400">Loki</span> observability stack — local, Docker, or remote.</p>
            </div>
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-white font-semibold mb-2">Ports</h3>
              <table className="w-full text-sm">
                <tbody>
                  <tr><td className="py-1 text-slate-500">Frontend (Vite)</td><td className="text-right font-mono">10850</td></tr>
                  <tr><td className="py-1 text-slate-500">Backend (FastAPI)</td><td className="text-right font-mono">10851</td></tr>
                  <tr><td className="py-1 text-slate-500">MCP HTTP</td><td className="text-right font-mono">10851 /mcp</td></tr>
                </tbody>
              </table>
            </div>
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-white font-semibold mb-2">Stack</h3>
              <ul className="space-y-1 text-sm">
                <li><span className="text-emerald-400">Python 3.13</span> — FastMCP 3.4 + FastAPI</li>
                <li><span className="text-blue-400">React 19</span> — Vite + Tailwind + Zustand</li>
                <li><span className="text-purple-400">Rust</span> — Tauri 2.0 NSIS wrapper</li>
              </ul>
            </div>
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-white font-semibold mb-2">Quick Start</h3>
              <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-2 rounded-md">git clone https://github.com/sandraschi/monitoring-mcp
cd monitoring-mcp
just</pre>
            </div>
          </div>
        </TabContent>

        {/* ── Install ──────────────────────────────────────────────── */}
        <TabContent id="install">
          <h3 className="text-white font-semibold text-base">Prerequisites</h3>
          <ul className="list-disc list-inside text-sm text-slate-400 space-y-1">
            <li><Code>uv</Code> (recommended) or <Code>pip</Code></li>
            <li>Python 3.12+</li>
            <li>Access to Grafana, Prometheus, and Loki instances</li>
          </ul>

          <h3 className="text-white font-semibold text-base pt-2">From source</h3>
          <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">git clone https://github.com/sandraschi/monitoring-mcp
cd monitoring-mcp
uv sync
uv run uvicorn monitoring_mcp.server:app --port 10851</pre>

          <h3 className="text-white font-semibold text-base pt-2">Claude Desktop</h3>
          <p>Add to <Code>claude_desktop_config.json</Code>:</p>
          <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">{`{
  "mcpServers": {
    "monitoring": {
      "command": "uv",
      "args": ["--directory", "D:/Dev/repos/monitoring-mcp", "run", "monitoring-mcp"]
    }
  }
}`}</pre>

          <h3 className="text-white font-semibold text-base pt-2">Environment</h3>
          <p>Copy <Code>.env.example</Code> to <Code>.env</Code> and set at minimum:</p>
          <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">MCP_WEB_USER=admin
MCP_WEB_PASSWORD=your_password</pre>
        </TabContent>

        {/* ── Configuration ────────────────────────────────────────── */}
        <TabContent id="config">
          <h3 className="text-white font-semibold text-base">Web Authentication (REQUIRED)</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead><tr className="border-b border-slate-800 text-slate-500 text-xs uppercase"><th className="text-left py-2 pr-4">Variable</th><th className="text-left py-2 pr-4">Description</th><th className="text-left py-2">Default</th></tr></thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MCP_WEB_USER</td><td className="py-2 pr-4">Web UI username</td><td className="py-2 text-amber-500">(required)</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MCP_WEB_PASSWORD</td><td className="py-2 pr-4">Web UI password</td><td className="py-2 text-amber-500">(required)</td></tr>
              </tbody>
            </table>
          </div>

          <h3 className="text-white font-semibold text-base pt-2">Monitoring Endpoints</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead><tr className="border-b border-slate-800 text-slate-500 text-xs uppercase"><th className="text-left py-2 pr-4">Variable</th><th className="text-left py-2 pr-4">Description</th><th className="text-left py-2">Default</th></tr></thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_GRAFANA_URL</td><td className="py-2 pr-4">Grafana URL</td><td className="py-2 font-mono text-xs">http://localhost:3000</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_PROMETHEUS_URL</td><td className="py-2 pr-4">Prometheus URL</td><td className="py-2 font-mono text-xs">http://localhost:9090</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_LOKI_URL</td><td className="py-2 pr-4">Loki URL</td><td className="py-2 font-mono text-xs">http://localhost:3100</td></tr>
              </tbody>
            </table>
          </div>

          <h3 className="text-white font-semibold text-base pt-2">Grafana Auth</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead><tr className="border-b border-slate-800 text-slate-500 text-xs uppercase"><th className="text-left py-2 pr-4">Variable</th><th className="text-left py-2">Description</th></tr></thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_GRAFANA_API_KEY</td><td className="py-2">API key (recommended)</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_GRAFANA_USERNAME</td><td className="py-2">Username (alt)</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_GRAFANA_PASSWORD</td><td className="py-2">Password (alt)</td></tr>
              </tbody>
            </table>
          </div>

          <h3 className="text-white font-semibold text-base pt-2">Performance</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead><tr className="border-b border-slate-800 text-slate-500 text-xs uppercase"><th className="text-left py-2 pr-4">Variable</th><th className="text-left py-2 pr-4">Default</th><th className="text-left py-2">Description</th></tr></thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_REQUEST_TIMEOUT</td><td className="py-2 pr-4 font-mono text-xs">30</td><td className="py-2">Request timeout (s)</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_MAX_RESULTS_LIMIT</td><td className="py-2 pr-4 font-mono text-xs">1000</td><td className="py-2">Max query results</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MONITORING_MCP_ENABLE_SAMPLING</td><td className="py-2 pr-4 font-mono text-xs">true</td><td className="py-2">Auto-sample large datasets</td></tr>
              </tbody>
            </table>
          </div>

          <h3 className="text-white font-semibold text-base pt-2">Transport (MCP mode)</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead><tr className="border-b border-slate-800 text-slate-500 text-xs uppercase"><th className="text-left py-2 pr-4">Variable</th><th className="text-left py-2 pr-4">Default</th><th className="text-left py-2">Description</th></tr></thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MCP_TRANSPORT</td><td className="py-2 pr-4 font-mono text-xs">stdio</td><td className="py-2">stdio | http | sse</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MCP_PORT</td><td className="py-2 pr-4 font-mono text-xs">10851</td><td className="py-2">HTTP listening port</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">MCP_HOST</td><td className="py-2 pr-4 font-mono text-xs">127.0.0.1</td><td className="py-2">Bind address</td></tr>
              </tbody>
            </table>
          </div>
        </TabContent>

        {/* ── Tools ────────────────────────────────────────────────── */}
        <TabContent id="tools">
          <p>The server exposes <strong className="text-white">5 portmanteau tools</strong> (each with multiple operations via an <Code>operation</Code> parameter):</p>

          <div className="space-y-4">
            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-800">
                <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                  <span className="text-emerald-400">grafana_management</span>
                </h4>
              </div>
              <div className="p-4 text-sm text-slate-400">
                <p className="mb-2">Implemented: <span className="text-emerald-400">list_dashboards, get_dashboard, create_dashboard, update_dashboard, delete_dashboard, search_dashboards, list_datasources, query_datasource, analyze_dashboard</span></p>
                <p>Planned: create_panel, update_panel, create_alert, export_dashboard, import_dashboard, list_folders, create_folder, get_dashboard_permissions</p>
              </div>
            </div>

            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-800">
                <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                  <span className="text-orange-400">prometheus_monitoring</span>
                </h4>
              </div>
              <div className="p-4 text-sm text-slate-400">
                <p className="mb-2">Implemented: <span className="text-emerald-400">query_metrics, query_range, list_targets, get_target_health, list_rules, list_alerts, get_build_info, analyze_metrics, optimize_queries</span></p>
                <p>Planned: create_alert_rule, update_alert_rule, delete_alert_rule, silence_alert, list_silences, expire_silence, get_config, get_flags</p>
              </div>
            </div>

            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-800">
                <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                  <span className="text-blue-400">loki_logging</span>
                </h4>
              </div>
              <div className="p-4 text-sm text-slate-400">
                <p className="mb-2">Implemented: <span className="text-emerald-400">query_logs, query_range, tail_logs, get_labels, get_label_values, get_series, analyze_logs, detect_anomalies, search_errors, trace_requests</span></p>
                <p>Planned: create_alert_rule, list_alerts, optimize_queries, export_logs, compare_timeframes, generate_report</p>
              </div>
            </div>

            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-800">
                <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                  <span className="text-purple-400">cross_system_correlation</span>
                </h4>
              </div>
              <div className="p-4 text-sm text-slate-400">
                <p className="mb-2">Implemented: <span className="text-emerald-400">correlate_incident, find_root_cause, performance_correlation, error_correlation, health_assessment</span></p>
                <p>Planned: anomaly_correlation, service_dependency_map, impact_analysis, predictive_insights, bottleneck_detection</p>
              </div>
            </div>

            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-800">
                <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                  <span className="text-teal-400">monitoring_status</span>
                </h4>
              </div>
              <div className="p-4 text-sm text-slate-400">
                <p className="mb-2">Implemented: <span className="text-emerald-400">system_health, connectivity_test, configuration_validation, performance_metrics, data_flow_status, alert_status</span></p>
                <p>Planned: storage_status, backup_status, security_status, capacity_planning</p>
              </div>
            </div>
          </div>

          <div className="border border-blue-900/30 bg-blue-950/10 rounded-lg p-4 mt-4">
            <p className="text-sm text-blue-300">Full tool reference with operation details at <Code>docs/TOOLS.md</Code>.</p>
          </div>
        </TabContent>

        {/* ── Prometheus ──────────────────────────────────────────── */}
        <TabContent id="prometheus">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-orange-400 font-semibold mb-2">What it monitors</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>• CPU / memory / disk metrics via node_exporter</li>
                <li>• HTTP request rates, latencies, error ratios</li>
                <li>• Custom application metrics via client libraries</li>
                <li>• Alerting rules + recording rules</li>
                <li>• Scrape target health and up/down status</li>
              </ul>
            </div>
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-orange-400 font-semibold mb-2">Operations exposed</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li><span className="text-emerald-400">query_metrics</span> — instant PromQL</li>
                <li><span className="text-emerald-400">query_range</span> — range queries</li>
                <li><span className="text-emerald-400">list_targets</span> — scrape targets</li>
                <li><span className="text-emerald-400">list_alerts</span> — firing alerts</li>
                <li><span className="text-emerald-400">analyze_metrics</span> — anomaly detection</li>
              </ul>
            </div>
          </div>

          <h3 className="text-white font-semibold text-base">Example queries</h3>
          <div className="space-y-2">
            <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">{`# CPU usage per instance
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`}</pre>
            <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">{`# HTTP error ratio (5xx / total)
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])`}</pre>
            <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">{`# Memory usage by job
sum by(job) (node_memory_MemTotal_bytes - node_memory_MemFree_bytes)`}</pre>
          </div>

          <h3 className="text-white font-semibold text-base pt-2">Default endpoint</h3>
          <p className="text-sm text-slate-400"><Code>http://localhost:9090</Code> — set via <Code>MONITORING_MCP_PROMETHEUS_URL</Code></p>
        </TabContent>

        {/* ── Loki ─────────────────────────────────────────────────── */}
        <TabContent id="loki">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-blue-400 font-semibold mb-2">What it does</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>• Aggregates structured + unstructured log streams</li>
                <li>• Labels-based indexing (no full-text inversion)</li>
                <li>• LogQL query language (like PromQL for logs)</li>
                <li>• Real-time tailing of live log output</li>
                <li>• Multi-tenancy via label selectors</li>
              </ul>
            </div>
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-blue-400 font-semibold mb-2">Operations exposed</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li><span className="text-emerald-400">query_logs</span> — instant LogQL</li>
                <li><span className="text-emerald-400">tail_logs</span> — live stream</li>
                <li><span className="text-emerald-400">search_errors</span> — error pattern finder</li>
                <li><span className="text-emerald-400">detect_anomalies</span> — log spike detection</li>
                <li><span className="text-emerald-400">trace_requests</span> — correlation ID tracing</li>
              </ul>
            </div>
          </div>

          <h3 className="text-white font-semibold text-base">Example LogQL queries</h3>
          <div className="space-y-2">
            <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">{`# Find all ERROR in the web-api service
{job="web-api"} |= "ERROR"`}</pre>
            <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">{`# Rate of 5xx responses per minute
rate({job="nginx"} |~ "HTTP/1.1\\" 5[0-9][0-9]" [5m])`}</pre>
            <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">{`# JSON parser for structured logs
{job="api"} |= "duration" | json | duration > 1s`}</pre>
          </div>

          <h3 className="text-white font-semibold text-base pt-2">Default endpoint</h3>
          <p className="text-sm text-slate-400"><Code>http://localhost:3100</Code> — set via <Code>MONITORING_MCP_LOKI_URL</Code></p>
        </TabContent>

        {/* ── Grafana ──────────────────────────────────────────────── */}
        <TabContent id="grafana">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-emerald-400 font-semibold mb-2">What it provides</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>• Unified dashboards for metrics + logs + traces</li>
                <li>• Prometheus, Loki, and 100+ other datasources</li>
                <li>• Alerting with labels, silences, and routing</li>
                <li>• RBAC, folders, dashboard provisioning</li>
                <li>• Annotation-based event tracking</li>
              </ul>
            </div>
            <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
              <h3 className="text-emerald-400 font-semibold mb-2">Operations exposed</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li><span className="text-emerald-400">list_dashboards</span> — all dashboards</li>
                <li><span className="text-emerald-400">get_dashboard</span> — by UID</li>
                <li><span className="text-emerald-400">create_dashboard</span> — from JSON</li>
                <li><span className="text-emerald-400">analyze_dashboard</span> — structure scoring</li>
                <li><span className="text-emerald-400">query_datasource</span> — run queries</li>
              </ul>
            </div>
          </div>

          <h3 className="text-white font-semibold text-base">Dashboard JSON structure</h3>
          <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">{`{
  "dashboard": {
    "title": "API Performance",
    "tags": ["api", "production"],
    "panels": [{
      "title": "Request Rate",
      "type": "timeseries",
      "targets": [{"expr": "rate(http_requests_total[5m])"}]
    }],
    "time": { "from": "now-6h", "to": "now" }
  }
}`}</pre>

          <h3 className="text-white font-semibold text-base pt-2">Default endpoint</h3>
          <p className="text-sm text-slate-400"><Code>http://localhost:3000</Code> — set via <Code>MONITORING_MCP_GRAFANA_URL</Code></p>
        </TabContent>

        {/* ── Development ──────────────────────────────────────────── */}
        <TabContent id="dev">
          <h3 className="text-white font-semibold text-base">Setup</h3>
          <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">uv sync
cd web_sota && npm install</pre>

          <h3 className="text-white font-semibold text-base pt-2">Running locally</h3>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="border border-slate-800 rounded-lg p-3 bg-slate-900/30">
              <p className="text-xs text-slate-500 mb-1">Terminal 1 — backend</p>
              <pre className="text-xs text-slate-400 font-mono">uv run uvicorn monitoring_mcp.server:app --port 10851</pre>
            </div>
            <div className="border border-slate-800 rounded-lg p-3 bg-slate-900/30">
              <p className="text-xs text-slate-500 mb-1">Terminal 2 — frontend</p>
              <pre className="text-xs text-slate-400 font-mono">cd web_sota && npm run dev</pre>
            </div>
          </div>

          <h3 className="text-white font-semibold text-base pt-2">Commands</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead><tr className="border-b border-slate-800 text-slate-500 text-xs uppercase"><th className="text-left py-2 pr-4">Command</th><th className="text-left py-2">What it does</th></tr></thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">just lint</td><td className="py-2">Ruff (Python) + Biome (JS/TS)</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">just fix</td><td className="py-2">Auto-fix lint issues</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">uv run pytest</td><td className="py-2">Run unit tests</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">npx playwright test</td><td className="py-2">Run E2E tests</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">just build-native</td><td className="py-2">Full Tauri/NSIS build pipeline</td></tr>
                <tr className="border-b border-slate-800/50"><td className="py-2 pr-4 font-mono text-xs">just cua-nsis-test</td><td className="py-2">NSIS smoke test</td></tr>
              </tbody>
            </table>
          </div>

          <h3 className="text-white font-semibold text-base pt-2">Architecture</h3>
          <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-md border border-slate-800">web_sota (React/Vite) ──HTTP──► backend (FastAPI/FastMCP) ──HTTP──► Grafana / Prometheus / Loki
    :10850                       :10851</pre>

          <h3 className="text-white font-semibold text-base pt-2">Code Standards</h3>
          <ul className="list-disc list-inside text-sm text-slate-400 space-y-1">
            <li><span className="text-slate-300">Python</span>: Ruff linting + formatting, mypy type checking</li>
            <li><span className="text-slate-300">TypeScript</span>: Biome linting, strict TypeScript</li>
            <li><span className="text-slate-300">FastMCP</span>: Portmanteau tools with <Code>operation</Code> enum param</li>
            <li><span className="text-slate-300">Tool returns</span>: Dict with <Code>success</Code>, <Code>message</Code>, domain data</li>
          </ul>
        </TabContent>

        {/* ── Links ───────────────────────────────────────────────── */}
        <TabContent id="links">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-3">Prometheus</h3>
              <ul className="text-sm space-y-2">
                <li><a href="https://prometheus.io/docs/prometheus/latest/querying/basics/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">PromQL basics</a><p className="text-xs text-slate-500 mt-0.5">Official query language reference</p></li>
                <li><a href="https://prometheus.io/docs/alerting/latest/alerting_rules/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Alerting rules</a><p className="text-xs text-slate-500 mt-0.5">Define and manage alert rules</p></li>
                <li><a href="https://awesome-prometheus-alerts.grep.to/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Awesome Prometheus alerts</a><p className="text-xs text-slate-500 mt-0.5">Community alert rule collection</p></li>
                <li><a href="https://grafana.com/docs/grafana/latest/datasources/prometheus/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Grafana + Prometheus</a><p className="text-xs text-slate-500 mt-0.5">Datasource setup guide</p></li>
              </ul>
            </div>

            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-3">Loki / LogQL</h3>
              <ul className="text-sm space-y-2">
                <li><a href="https://grafana.com/docs/loki/latest/logql/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">LogQL reference</a><p className="text-xs text-slate-500 mt-0.5">Official LogQL documentation</p></li>
                <li><a href="https://grafana.com/docs/loki/latest/api/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Loki API</a><p className="text-xs text-slate-500 mt-0.5">HTTP API for pushing/querying logs</p></li>
                <li><a href="https://grafana.com/blog/2024/02/05/loki-logql-alerting-rules/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">LogQL alerting rules</a><p className="text-xs text-slate-500 mt-0.5">Log-based alerting examples</p></li>
                <li><a href="https://promtail.io/docs/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Promtail</a><p className="text-xs text-slate-500 mt-0.5">Log collection agent for Loki</p></li>
              </ul>
            </div>

            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-3">Grafana</h3>
              <ul className="text-sm space-y-2">
                <li><a href="https://grafana.com/docs/grafana/latest/dashboards/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Dashboard documentation</a><p className="text-xs text-slate-500 mt-0.5">Create and manage dashboards</p></li>
                <li><a href="https://grafana.com/docs/grafana/latest/alerting/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Grafana Alerting</a><p className="text-xs text-slate-500 mt-0.5">Alert setup, silences, routing</p></li>
                <li><a href="https://grafana.com/docs/grafana/latest/administration/provisioning/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Provisioning</a><p className="text-xs text-slate-500 mt-0.5">Declarative dashboard/datasource config</p></li>
                <li><a href="https://grafana.com/docs/grafana/latest/http_api/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">HTTP API</a><p className="text-xs text-slate-500 mt-0.5">Full REST API reference</p></li>
              </ul>
            </div>

            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-3">Tools & Ecosystem</h3>
              <ul className="text-sm space-y-2">
                <li><a href="https://github.com/jlowin/fastmcp" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">FastMCP</a><p className="text-xs text-slate-500 mt-0.5">Python MCP framework used by this server</p></li>
                <li><a href="https://modelcontextprotocol.io/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">MCP specification</a><p className="text-xs text-slate-500 mt-0.5">Model Context Protocol docs</p></li>
                <li><a href="https://prometheus.io/docs/introduction/overview/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Prometheus overview</a><p className="text-xs text-slate-500 mt-0.5">Architecture and design philosophy</p></li>
                <li><a href="https://grafana.com/oss/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Grafana Labs OSS</a><p className="text-xs text-slate-500 mt-0.5">Grafana, Loki, Tempo, Mimir overview</p></li>
              </ul>
            </div>
          </div>

          <div className="border border-blue-900/30 bg-blue-950/10 rounded-lg p-4 mt-2">
            <p className="text-sm text-blue-300">Repository: <a href="https://github.com/sandraschi/monitoring-mcp" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">github.com/sandraschi/monitoring-mcp</a></p>
          </div>
        </TabContent>

        {/* ── Troubleshooting ──────────────────────────────────────── */}
        <TabContent id="trouble">
          <div className="space-y-4">
            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-2">"Failed to fetch" in web UI</h3>
              <ol className="list-decimal list-inside text-sm text-slate-400 space-y-1">
                <li>Backend is running: <Code>uv run uvicorn monitoring_mcp.server:app --port 10851</Code></li>
                <li>Port matches <Code>web_sota/src/lib/api.ts</Code> (<Code>API_BASE = "http://127.0.0.1:10851"</Code>)</li>
                <li>CORS allows <Code>http://127.0.0.1:10850</Code> (frontend origin)</li>
              </ol>
            </div>

            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-2">Backend starts but tools return connection errors</h3>
              <p className="text-sm text-slate-400 mb-2">The server can't reach Grafana/Prometheus/Loki. Check:</p>
              <ul className="list-disc list-inside text-sm text-slate-400 space-y-1">
                <li>Are the services running? (<Code>docker ps</Code>)</li>
                <li><Code>MONITORING_MCP_*_URL</Code> env vars point to the right host:port</li>
                <li>For Docker, use <Code>host.docker.internal</Code> instead of <Code>localhost</Code></li>
              </ul>
            </div>

            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-2">Auth errors (401 / 500)</h3>
              <p className="text-sm text-slate-400">Set <Code>MCP_WEB_USER</Code> and <Code>MCP_WEB_PASSWORD</Code> in <Code>.env</Code> or as environment variables. Without these, the web API returns 500.</p>
            </div>

            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-2">"Operation X is not yet implemented"</h3>
              <p className="text-sm text-slate-400">Advanced operations are placeholders. See the <strong className="text-slate-300">Tools</strong> tab for the implemented subset. Check <Code>docs/TOOLS.md</Code> for each operation's status.</p>
            </div>

            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-2">NSIS installer hangs</h3>
              <p className="text-sm text-slate-400 mb-2">Kill zombie processes manually:</p>
              <pre className="text-xs text-slate-400 font-mono bg-slate-950 p-2 rounded-md">taskkill /F /IM monitoring-mcp-backend.exe
taskkill /F /IM monitoring-mcp-native.exe</pre>
            </div>

            <div className="border border-slate-800 rounded-lg p-4">
              <h3 className="text-white font-semibold text-sm mb-2">Windows Defender flags PyInstaller .exe</h3>
              <p className="text-sm text-slate-400">Common false positive for <Code>--onefile</Code> PyInstaller binaries. Add an exclusion or build with <Code>--onedir</Code> to reduce false positive rate.</p>
            </div>
          </div>
        </TabContent>
      </Tabs.Root>
    </div>
  );
}
