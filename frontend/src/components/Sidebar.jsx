import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Package,
  Headphones,
  UserCog,
  CalendarDays,
  Boxes,
  BarChart3,
  Settings,
  X,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { name: "Customers", path: "/customers", icon: Users },
  { name: "Products", path: "/products", icon: Package },
  { name: "Service Calls", path: "/service-calls", icon: Headphones },
  { name: "Engineers", path: "/engineers", icon: UserCog },
  { name: "Appointments", path: "/appointments", icon: CalendarDays },
  { name: "Parts & Inventory", path: "/parts", icon: Boxes },
  { name: "Reports", path: "/reports", icon: BarChart3 },
];

function Sidebar({
  expanded,
  mobileOpen,
  setMobileOpen,
  setSidebarHover,
}) {
  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-40 bg-slate-900/20 lg:hidden"
        />
      )}

      <aside
        onMouseEnter={() => setSidebarHover(true)}
        onMouseLeave={() => setSidebarHover(false)}
        className={`
          fixed inset-y-0 left-0 z-50
          border-r border-slate-200
          bg-white
          shadow-[4px_0_18px_rgba(15,23,42,0.04)]
          transition-all duration-200 ease-out
          lg:block
          ${expanded ? "lg:w-64" : "lg:w-[76px]"}
          ${mobileOpen ? "w-64 translate-x-0" : "w-64 -translate-x-full lg:translate-x-0"}
        `}
      >
        <div className="flex h-full flex-col">

          {/* Logo */}
          <div
            className={`
              flex h-[72px] items-center border-b border-slate-100
              ${expanded || mobileOpen ? "px-5" : "justify-center px-2"}
            `}
          >
            <img
              src="/src/assets/stech-logo.png"
              alt="STech"
              className={`
                object-contain transition-all duration-200
                ${expanded || mobileOpen ? "h-10 w-auto max-w-[190px]" : "h-9 w-10 object-cover object-left"}
              `}
            />

            {(expanded || mobileOpen) && (
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="ml-auto rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 lg:hidden"
              >
                <X size={18} />
              </button>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-5">

            {(expanded || mobileOpen) && (
              <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">
                Workspace
              </p>
            )}

            {navigation.map((item) => {
              const Icon = item.icon;

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileOpen(false)}
                  title={!expanded && !mobileOpen ? item.name : undefined}
                  className={({ isActive }) =>
                    `
                    group flex items-center rounded-xl
                    transition-all duration-150
                    ${
                      expanded || mobileOpen
                        ? "gap-3 px-3 py-2.5"
                        : "justify-center px-2 py-3"
                    }
                    ${
                      isActive
                        ? "bg-[#eaf2fb] text-[#173b67]"
                        : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
                    }
                    `
                  }
                >
                  <Icon
                    size={19}
                    strokeWidth={1.8}
                    className="shrink-0"
                  />

                  {(expanded || mobileOpen) && (
                    <span className="truncate text-sm font-medium">
                      {item.name}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>

          {/* Settings */}
          <div className="border-t border-slate-100 p-3">
            <NavLink
              to="/settings"
              title={!expanded && !mobileOpen ? "Settings" : undefined}
              className={`
                flex items-center rounded-xl text-slate-500
                transition-all hover:bg-slate-50 hover:text-slate-800
                ${
                  expanded || mobileOpen
                    ? "gap-3 px-3 py-2.5"
                    : "justify-center px-2 py-3"
                }
              `}
            >
              <Settings size={19} strokeWidth={1.8} />

              {(expanded || mobileOpen) && (
                <span className="text-sm font-medium">Settings</span>
              )}
            </NavLink>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
