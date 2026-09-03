import {
  BarChart3,
  BrainCircuit,
  FileText,
  LayoutDashboard,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const navigation = [
  {
    name: "Overview",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Financials",
    path: "/financials",
    icon: BarChart3,
  },
  {
    name: "Documents",
    path: "/documents",
    icon: FileText,
  },
  {
    name: "AI Analysis",
    path: "/ai-analysis",
    icon: BrainCircuit,
  },
];

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 w-64 border-r border-zinc-200 bg-white">
      <div className="flex h-20 items-center border-b border-zinc-200 px-6">
        <div>
          <div className="text-lg font-semibold tracking-tight">
            SENUS
          </div>

          <div className="text-xs text-zinc-500">
            Board Intelligence
          </div>
        </div>
      </div>

      <nav className="space-y-1 p-4">
        {navigation.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition",
                  isActive
                    ? "bg-zinc-900 text-white"
                    : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900",
                ].join(" ")
              }
            >
              <Icon size={18} />

              {item.name}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}