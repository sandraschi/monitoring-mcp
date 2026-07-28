import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Activity,
  Battery,
  Power,
  RefreshCw,
  Wifi,
} from "lucide-react";

// Mock Data from legacy temp_robot_control.tsx
interface RobotStatus {
  id: string;
  name: string;
  type: "humanoid" | "quadruped" | "wheeled";
  status: "online" | "offline" | "error" | "charging";
  battery: number;
  wifi: number;
  temperature: number;
  task: string;
}

const ROBOTS: RobotStatus[] = [
  {
    id: "unitree-h1",
    name: "Unitree H1",
    type: "humanoid",
    status: "online",
    battery: 87,
    wifi: 92,
    temperature: 45,
    task: "Idle - Ready for teleop",
  },
  {
    id: "go2-alpha",
    name: "Go2 Alpha",
    type: "quadruped",
    status: "charging",
    battery: 45,
    wifi: 88,
    temperature: 38,
    task: "Charging - Dock A",
  },
  {
    id: "scout-mini",
    name: "Scout Mini",
    type: "wheeled",
    status: "offline",
    battery: 0,
    wifi: 0,
    temperature: 0,
    task: "Connection lost",
  },
];

export function Control() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Control Center
          </h2>
          <p className="text-slate-400">
            Direct teleoperation and fleet management
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="border-slate-800 bg-slate-900/50 hover:bg-slate-800"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button className="bg-emerald-600 hover:bg-emerald-700 text-white border-0">
            <Power className="mr-2 h-4 w-4" />
            Emergency Stop
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {ROBOTS.map((robot) => (
          <RobotCard key={robot.id} robot={robot} />
        ))}
      </div>

      <Tabs defaultValue="logs" className="space-y-4">
        <TabsList className="bg-slate-900/50 border border-slate-800">
          <TabsTrigger
            value="logs"
            className="data-[state=active]:bg-slate-800"
          >
            System Logs
          </TabsTrigger>
          <TabsTrigger
            value="config"
            className="data-[state=active]:bg-slate-800"
          >
            Configuration
          </TabsTrigger>
        </TabsList>
        <TabsContent value="logs">
          <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader>
              <CardTitle>System Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-mono text-sm text-slate-400 space-y-2">
                <p>
                  [10:42:15] <span className="text-emerald-500">INFO</span>{" "}
                  Monitoring agent connected
                </p>
                <p>
                  [10:41:22] <span className="text-yellow-500">WARN</span>{" "}
                  Scrape latency spike (145ms)
                </p>
                <p>
                  [10:40:05] <span className="text-blue-500">DEBUG</span>{" "}
                  Metrics connection established
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function RobotCard({ robot }: { robot: RobotStatus }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-emerald-500 text-emerald-500";
      case "charging":
        return "bg-blue-500 text-blue-500";
      case "error":
        return "bg-red-500 text-red-500";
      case "offline":
        return "bg-slate-500 text-slate-500";
      default:
        return "bg-slate-500";
    }
  };

  return (
    <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-sm transition-all hover:bg-slate-900/50">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-slate-200">
          {robot.name}
        </CardTitle>
        <Badge
          variant="outline"
          className={`border-opacity-20 bg-opacity-10 capitalize ${getStatusColor(robot.status)} border-current bg-current`}
        >
          {robot.status}
        </Badge>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 py-4">
          <div className="flex items-center gap-4">
            <div className="grid gap-1">
              <p className="text-sm font-medium leading-none text-slate-400">
                Battery
              </p>
              <div className="flex items-center gap-2">
                <Battery className="h-4 w-4 text-slate-500" />
                <span className="text-sm font-bold text-slate-200">
                  {robot.battery}%
                </span>
              </div>
            </div>
            <div className="grid gap-1">
              <p className="text-sm font-medium leading-none text-slate-400">
                Signal
              </p>
              <div className="flex items-center gap-2">
                <Wifi className="h-4 w-4 text-slate-500" />
                <span className="text-sm font-bold text-slate-200">
                  {robot.wifi}%
                </span>
              </div>
            </div>
            <div className="grid gap-1">
              <p className="text-sm font-medium leading-none text-slate-400">
                Temp
              </p>
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-slate-500" />
                <span className="text-sm font-bold text-slate-200">
                  {robot.temperature}°C
                </span>
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Current Task</span>
              <span className="text-slate-200">{robot.task}</span>
            </div>
            <Progress
              value={robot.battery}
              className="h-1 bg-slate-800"
              indicatorClassName={
                robot.battery < 20 ? "bg-red-500" : "bg-emerald-500"
              }
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


