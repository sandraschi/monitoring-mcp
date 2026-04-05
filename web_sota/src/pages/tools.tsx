import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Wrench, Play, AlertCircle, Loader2 } from "lucide-react";

export function Tools() {
    const [tools, setTools] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTools = async () => {
            try {
                const response = await fetch('/api/tools');
                const data = await response.json();
                setTools(data.tools || []);
            } catch (error) {
                console.error("Failed to fetch tools", error);
            } finally {
                setLoading(false);
            }
        };
        fetchTools();
    }, []);

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">System MCP Tools</h2>
                <p className="text-slate-400">Directly execute monitoring and diagnostic operations</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {loading ? (
                    <div className="col-span-full flex items-center justify-center p-12">
                        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                    </div>
                ) : tools.map((tool) => (
                    <Card key={tool} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors">
                        <CardHeader className="pb-2">
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-sm font-semibold text-white">{tool}</CardTitle>
                                <Wrench className="h-4 w-4 text-blue-500" />
                            </div>
                            <CardDescription className="text-xs text-slate-400">
                                System management tool
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button size="sm" className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200">
                                <Play className="mr-2 h-3 w-3" /> Execute
                            </Button>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {!loading && tools.length === 0 && (
                <div className="flex flex-col items-center justify-center p-12 border border-dashed border-slate-800 rounded-lg">
                    <AlertCircle className="h-8 w-8 text-slate-600 mb-2" />
                    <p className="text-slate-500">No tools detected from backend</p>
                </div>
            )}
        </div>
    );
}
