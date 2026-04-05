import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { HelpCircle, Book, Shield, Zap, Info } from "lucide-react";

export function Help() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Help & Documentation</h2>
                <p className="text-slate-400">Reference guide for System Monitoring MCP</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Book className="h-5 w-5 text-blue-500" />
                            <CardTitle className="text-white">Quick Start</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>1. Open the System Interface to ask natural language questions about your hardware.</p>
                        <p>2. Review the Overview dashboard for real-time telemetry like CPU temp and RAM load.</p>
                        <p>3. Use MCP Tools for low-level diagnostic commands or metric resets.</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Shield className="h-5 w-5 text-purple-500" />
                            <CardTitle className="text-white">Security & Auth</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>Web access requires Basic Authentication. Default credentials are s:sandra p:sandra123.</p>
                        <p>Monitoring data is read-only for most components; system mutation requires higher privileges.</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Zap className="h-5 w-5 text-yellow-500" />
                            <CardTitle className="text-white">MCP Parameters</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 space-y-4">
                        <p>Port: 10810 (Standard for Monitoring MCP)</p>
                        <p>Transport: Dual (STDIO + HTTP Bridge)</p>
                        <p>Backend: FastAPI / FastMCP 2.14+</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Info className="h-5 w-5 text-emerald-500" />
                            <CardTitle className="text-white">About SOTA</CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400">
                        <p>Part of the Sandra SOTA Fleet (January 2026). Standardized UI for unified system observability and AI-driven diagnostics.</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
