import { cn } from "@/common/utils";
import {
  Activity,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Code2,
  HelpCircle,
  LayoutDashboard,
  LayoutGrid,
  MessageSquare,
  Settings,
  Wrench,
} from "lucide-react";
import { Link, useLocation } from "react-router-dom";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const location = useLocation();

  const navItems = [
    { href: "/", label: "Overview", icon: LayoutDashboard },
    { href: "/chat", label: "AI Command", icon: MessageSquare },
    { href: "/tools", label: "MCP Tools", icon: Wrench },
    { href: "/skills", label: "Skills", icon: BookOpen },
    { href: "/apps", label: "Apps Hub", icon: LayoutGrid },
    { href: "/logging", label: "Logging", icon: Activity },
    { href: "/api-docs", label: "API Docs", icon: Code2 },
    { href: "/help", label: "Help", icon: HelpCircle },
    { href: "/settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-slate-800 bg-slate-950/50 backdrop-blur-xl transition-all duration-300 ease-in-out",
        collapsed ? "w-16" : "w-64",
      )}
    >
      <div className="flex h-16 items-center justify-between border-b border-slate-800 px-4">
        <div className="flex items-center gap-2 font-semibold text-slate-100">
          <Activity className="h-6 w-6 text-blue-500 shrink-0" />
          {!collapsed && (
            <span className="animate-in fade-in duration-300">
              System Monitoring
            </span>
          )}
        </div>
        <button
          onClick={onToggle}
          className="flex items-center justify-center rounded-md p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors shrink-0"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-slate-800 hover:text-white",
                isActive ? "bg-slate-800 text-white" : "text-slate-400",
                collapsed ? "justify-center" : "justify-start",
              )}
            >
              <item.icon
                className={cn(
                  "h-5 w-5 shrink-0",
                  !collapsed && "mr-3",
                  isActive && "text-blue-400",
                )}
              />
              {!collapsed && <span>{item.label}</span>}

              {/* Tooltip for collapsed mode */}
              {collapsed && (
                <div className="absolute left-full ml-2 hidden rounded bg-slate-800 px-2 py-1 text-xs text-white group-hover:block z-50 whitespace-nowrap">
                  {item.label}
                </div>
              )}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
