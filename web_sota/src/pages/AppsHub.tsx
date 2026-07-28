import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LayoutGrid, ExternalLink, Loader2 } from "lucide-react";

type AppEntry = {
  name: string;
  url: string;
  port: number;
  status?: string;
};

export function AppsHub() {
  const [apps, setApps] = useState<AppEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const knownPorts: { port: number; name: string }[] = [];
        const results: AppEntry[] = [];
        for (const { port, name } of knownPorts) {
          try {
            const r = await fetch(`http://127.0.0.1:${port}/health`, { signal: AbortSignal.timeout(2000) });
            if (r.ok) results.push({ name, url: `http://127.0.0.1:${port}`, port, status: "online" });
          } catch { /* offline */ }
        }
        setApps(results);
      } catch { /* no discovery */ }
      finally { setLoading(false); }
    })();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Apps Hub</h2>
          <p className="text-slate-400">Fleet application discovery</p>
        </div>
        <LayoutGrid className="h-5 w-5 text-emerald-500" />
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      ) : apps.length === 0 ? (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="p-6 text-center text-sm text-slate-500">
            No fleet apps detected on standard ports.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {apps.map((app) => (
            <Card key={app.port} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-semibold text-white">{app.name}</CardTitle>
                  <span className={`h-2 w-2 rounded-full ${app.status === "online" ? "bg-green-500" : "bg-red-500"}`} />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-slate-500 mb-2">Port {app.port}</p>
                <a
                  href={app.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                >
                  Open <ExternalLink className="h-3 w-3" />
                </a>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
