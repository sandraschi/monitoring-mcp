import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Cpu, HardDrive, Zap } from "lucide-react";

export function Dashboard() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">System Monitoring Dashboard</h2>
                    <p className="text-slate-400">Real-time telemetry and health monitoring</p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            CPU Load
                        </CardTitle>
                        <Cpu className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">12.5%</div>
                        <p className="text-xs text-slate-400">
                            AMD Ryzen 9 5900X
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            RAM Utilization
                        </CardTitle>
                        <Activity className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">45.2%</div>
                        <p className="text-xs text-slate-400">
                            28.9GB of 64GB
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Thermal Status
                        </CardTitle>
                        <Zap className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">54°C</div>
                        <p className="text-xs text-slate-400">
                            Package temp • Stable
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Disk I/O
                        </CardTitle>
                        <HardDrive className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">42 MB/s</div>
                        <p className="text-xs text-slate-400">
                            NVMe Write active
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Recent Metrics</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[200px] font-mono text-xs p-4 overflow-y-auto border border-slate-800 rounded-md bg-slate-900/50 text-slate-400 space-y-1">
                            <p className="text-blue-400">[08:42:01] Prometheus scrape successful (234 metrics)</p>
                            <p>[08:42:05] CPU: 12.5% | RAM: 45.2% | SWAP: 0%</p>
                            <p>[08:42:10] SmartCTL scan passed: All drives healthy</p>
                            <p className="text-emerald-400">[08:42:15] AI Analyzer: No health anomalies detected</p>
                            <div className="animate-pulse inline-block h-2 w-1 bg-slate-500 ml-1" />
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">System Alerts</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                </span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white">System Guard: Online</p>
                                    <p className="text-xs text-slate-400">Monitoring all local services</p>
                                </div>
                            </div>
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2 bg-slate-700 rounded-full"></span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white text-opacity-50">Backup Sequence</p>
                                    <p className="text-xs text-slate-500">Awaiting Multi-Backup trigger</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
