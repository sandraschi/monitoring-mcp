"use client";

import { API_BASE } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ExternalLink, HelpCircle, LayoutGrid } from "lucide-react";

const APPS_CATALOG: { id: string; label: string; url: string; icon: any }[] = [];

export function Topbar() {
  const backendOk = useAppStore((s) => s.backendOk);
  const toolCount = useAppStore((s) => s.toolCount);

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-6 backdrop-blur-xl">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-medium text-slate-400">
          Navigation / <span className="text-slate-100">Monitoring Control Center</span>
        </h1>
      </div>

      <div className="flex items-center gap-2">
        {/* Backend Status Indicator */}
        <div
          data-testid="backend-dot"
          className={`mr-4 flex items-center gap-2 rounded-full px-3 py-1 text-xs border ${
            backendOk === null
              ? "bg-gray-500/10 text-gray-500 border-gray-500/20"
              : backendOk
                ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                : "bg-red-500/10 text-red-500 border-red-500/20"
          }`}
        >
          <span className="relative flex h-2 w-2">
            {backendOk !== false && (
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-75"></span>
            )}
            <span className={`relative inline-flex h-2 w-2 rounded-full bg-current`}></span>
          </span>
          {backendOk === null ? "Connecting..." : backendOk ? `Online (${toolCount} tools)` : "Offline"}
        </div>

        {/* Global Apps Navigation */}
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-900/50 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-700">
              <LayoutGrid className="h-4 w-4" />
              Apps
            </button>
          </DropdownMenu.Trigger>

          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 min-w-[220px] animate-in fade-in zoom-in-95 data-[side=bottom]:slide-in-from-top-2 rounded-md border border-slate-800 bg-slate-950 p-1 shadow-xl"
              sideOffset={5}
              align="end"
            >
              <DropdownMenu.Label className="px-2 py-1.5 text-xs font-semibold text-slate-500">
                Switch Application
              </DropdownMenu.Label>

              <div className="h-px bg-slate-800 my-1" />

              {APPS_CATALOG.length === 0 ? (
                <div className="px-2 py-3 text-xs text-slate-500 text-center">No fleet apps detected</div>
              ) : (
                APPS_CATALOG.map((app) => (
                  <DropdownMenu.Item key={app.id} asChild>
                    <a
                      href={app.url}
                      className="flex w-full select-none items-center rounded-sm px-2 py-1.5 text-sm text-slate-300 hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white outline-none cursor-pointer"
                    >
                      <app.icon className="mr-2 h-4 w-4 text-slate-400" />
                      <span>{app.label}</span>
                      <ExternalLink className="ml-auto h-3 w-3 opacity-50" />
                    </a>
                  </DropdownMenu.Item>
                ))
              )}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        <a
          href={`${API_BASE}/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
        >
          <HelpCircle className="h-4 w-4" />
        </a>
      </div>
    </header>
  );
}
