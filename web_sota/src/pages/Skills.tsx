import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, Loader2 } from "lucide-react";

export function Skills() {
  const [skills, setSkills] = useState<string[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/api/skills`);
        if (r.ok) {
          const d = await r.json();
          setSkills(d.skills || []);
        }
      } catch { /* no skills endpoint */ }
      finally { setLoading(false); }
    })();
  }, []);

  useEffect(() => {
    if (!selected) return;
    (async () => {
      setContent("Loading...");
      try {
        const r = await fetch(`${API_BASE}/api/skills/${selected}`);
        if (r.ok) setContent(await r.text());
        else setContent("Skill not found.");
      } catch { setContent("Failed to load skill."); }
    })();
  }, [selected]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Skills</h2>
          <p className="text-slate-400">Server capabilities and usage guides</p>
        </div>
        <BookOpen className="h-5 w-5 text-blue-500" />
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      ) : skills.length === 0 ? (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="p-6 text-center text-sm text-slate-500">
            No skills available. Skills are exposed by the MCP server as skill:// resources.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            {skills.map((s) => (
              <button
                key={s}
                onClick={() => setSelected(s)}
                className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                  selected === s ? "bg-slate-800 text-white" : "text-slate-400 hover:bg-slate-800/50"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
          <div className="md:col-span-2">
            {content && (
              <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader><CardTitle className="text-white text-sm">{selected}</CardTitle></CardHeader>
                <CardContent className="prose prose-invert prose-sm max-w-none text-slate-300 whitespace-pre-wrap">
                  {content}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
