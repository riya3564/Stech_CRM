
import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

function AppLayout() {
  const [sidebarHover, setSidebarHover] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#f5f8fc] text-slate-900">
      <Sidebar
        expanded={sidebarHover}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        setSidebarHover={setSidebarHover}
      />

      <div className="min-h-screen lg:pl-[76px]">
        <Topbar onMenuClick={() => setMobileOpen(true)} />

        <main className="min-h-[calc(100vh-72px)] p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
