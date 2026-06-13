import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Cpu, Activity } from "lucide-react";

function LLMSettings() {
    const [providers, setProviders] = useState<Record<string, {name:string}[]>>({});
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");
    useEffect(() => {
        fetch("/api/llm/providers").then(r => r.json()).then(d => {
            setProviders(d);
            const savedP = localStorage.getItem("llm_provider") || "ollama";
            const savedM = localStorage.getItem("llm_model") || "";
            setSelectedProvider(savedP);
            const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
            setSelectedModel(savedM && models.some((m:{name:string}) => m.name === savedM) ? savedM : (models[0]?.name || ""));
        }).catch(() => {
            setProviders({ ollama: [{name:"llama3.2:3b"}] });
            setSelectedModel(localStorage.getItem("llm_model") || "llama3.2:3b");
        });
    }, []);
    const save = (p:string, m:string) => { localStorage.setItem("llm_provider", p); localStorage.setItem("llm_model", m); };
    const models = providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
    return (
        <div className="space-y-3">
            <Select value={selectedProvider} onValueChange={(v) => { setSelectedProvider(v); save(v, ""); }}>
                <SelectTrigger className="bg-slate-900 border-slate-800 text-slate-100">
                    <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 text-slate-100">
                    <SelectItem value="ollama">Ollama</SelectItem>
                    <SelectItem value="lm_studio">LM Studio</SelectItem>
                </SelectContent>
            </Select>
            <Select value={selectedModel} onValueChange={(v) => { setSelectedModel(v); save(selectedProvider, v); }}>
                <SelectTrigger className="bg-slate-900 border-slate-800 text-slate-100">
                    <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 text-slate-100">
                    {models.map((m) => <SelectItem key={m.name} value={m.name}>{m.name}</SelectItem>)}
                </SelectContent>
            </Select>
        </div>
    );
}

export function Settings() {

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
                <p className="text-slate-400">Configure Local LLM and monitoring orchestration preferences</p>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Cpu className="h-5 w-5 text-blue-500" />
                        <CardTitle className="text-white">Local LLM Configuration</CardTitle>
                    </div>
                    <CardDescription className="text-slate-400">Provider and model selection</CardDescription>
                </CardHeader>
                <CardContent>
                    <LLMSettings />
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Activity className="h-5 w-5 text-emerald-500" />
                        <CardTitle className="text-white">Monitoring Thresholds</CardTitle>
                    </div>
                    <CardDescription className="text-slate-400">Define critical limits for system health alerts</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">CPU Critical (%)</Label>
                            <Input defaultValue="90" className="bg-slate-900 border-slate-800 text-slate-100" />
                        </div>
                        <div className="grid gap-2">
                            <Label className="text-slate-300">RAM Critical (%)</Label>
                            <Input defaultValue="95" className="bg-slate-900 border-slate-800 text-slate-100" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">App Information</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-slate-400 space-y-1">
                    <p>System Monitoring Hub v0.1.0 (SOTA)</p>
                    <p>Dual Transport: STDIO + HTTP (10809)</p>
                    <p>Frontend Port: 10808</p>
                </CardContent>
            </Card>
        </div>
    );
}
