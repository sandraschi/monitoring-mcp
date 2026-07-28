import { useState } from "react";
import { API_BASE } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, Code2, ExternalLink } from "lucide-react";

export function ApiDocs() {
  const [view, setView] = useState<"swagger" | "redoc">("swagger");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">API Documentation</h2>
          <p className="text-slate-400">FastAPI auto-generated docs</p>
        </div>
        <Code2 className="h-5 w-5 text-blue-500" />
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => setView("swagger")}
          className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
            view === "swagger" ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
          }`}
        >
          Swagger UI
        </button>
        <button
          onClick={() => setView("redoc")}
          className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
            view === "redoc" ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
          }`}
        >
          ReDoc
        </button>
        <a
          href={`${API_BASE}/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs text-slate-400 hover:text-blue-400 transition-colors"
        >
          Open in browser <ExternalLink className="h-3 w-3" />
        </a>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white text-sm">
            {view === "swagger" ? "Swagger UI" : "ReDoc"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[65vh] rounded border border-slate-800 overflow-hidden bg-white">
            <iframe
              src={view === "swagger" ? `${API_BASE}/docs` : `${API_BASE}/redoc`}
              className="w-full h-full"
              title={view}
            />
          </div>
          <p className="text-xs text-slate-500 mt-2">
            If the docs don't load,{" "}
            <a href={`${API_BASE}/docs`} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
              open them directly
            </a>
            .
          </p>
        </CardContent>
      </Card>

      <div className="flex gap-2 overflow-x-auto pb-2">
        {["GET /health", "GET /api/health", "GET /api/status", "GET /api/tools", "GET /api/v1/diagnostics", "POST /api/chat"].map((ep) => (
          <span key={ep} className="shrink-0 px-3 py-1 rounded-full bg-slate-800 text-xs text-slate-400 font-mono">
            {ep}
          </span>
        ))}
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white text-sm">MCP Tool Reference</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 space-y-3">
          <p>
            The MCP tools (PromQL queries, LogQL search, Grafana dashboard management, etc.)
            are registered as FastMCP tools and accessed via the MCP protocol (stdio).
            They are not REST endpoints and don't appear in Swagger.
          </p>
          <a
            href={`${API_BASE}/docs/TOOLS.md`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 text-xs"
          >
            <BookOpen className="h-3 w-3" /> Full MCP tool reference <ExternalLink className="h-3 w-3" />
          </a>
        </CardContent>
      </Card>
    </div>
  );
}
