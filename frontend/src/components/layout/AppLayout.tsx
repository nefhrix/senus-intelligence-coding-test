import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-zinc-50">
      <Sidebar />

      <main className="ml-64 min-h-screen">
        <div className="mx-auto max-w-[1600px] p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}