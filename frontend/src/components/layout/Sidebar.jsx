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
  ArrowRightLeft,
} from "lucide-react";

import stechLogo from "../../assets/stech-logo.png";

const navigation = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Customers",
    path: "/customers",
    icon: Users,
  },
  {
    name: "Products",
    path: "/products",
    icon: Package,
  },
  {
    name: "Service Calls",
    path: "/service-calls",
    icon: Headphones,
  },
  {
    name: "Call Transfer",
    path: "/service-calls?mode=transfer",
    icon: ArrowRightLeft,
  },
  {
    name: "Engineers",
    path: "/engineers",
    icon: UserCog,
  },
  {
    name: "Appointments",
    path: "/appointments",
    icon: CalendarDays,
  },
  {
    name: "Parts & Inventory",
    path: "/parts",
    icon: Boxes,
  },
  {
    name: "Reports",
    path: "/reports",
    icon: BarChart3,
  },
];

function Sidebar({
  expanded,
  mobileOpen,
  setMobileOpen,
  setSidebarHover,
}) {
  const open = expanded || mobileOpen;

  return (
    <>
      {/* Mobile Overlay */}
      {mobileOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-40 bg-slate-900/20 lg:hidden"
        />
      )}

      {/* Sidebar */}
      <aside
        onMouseEnter={() => setSidebarHover(true)}
        onMouseLeave={() => setSidebarHover(false)}
        className={`
          fixed inset-y-0 left-0 z-50
          border-r border-slate-200
          bg-white
          shadow-[4px_0_20px_rgba(15,23,42,0.05)]
          transition-[width,transform] duration-200 ease-out

          ${open ? "lg:w-64" : "lg:w-[76px]"}

          ${
            mobileOpen
              ? "w-64 translate-x-0"
              : "w-64 -translate-x-full lg:translate-x-0"
          }
        `}
      >
        <div className="flex h-full flex-col">

          {/* =========================
              STECH LOGO
          ========================= */}
          <div
            className={`
              flex h-[72px] shrink-0
              items-center
              border-b border-slate-100
              ${
                open
                  ? "justify-start px-5"
                  : "justify-center px-2"
              }
            `}
          >
            <img
              src={stechLogo}
              alt="STech"
              className={`
                object-contain
                transition-all duration-200
                ${
                  open
                    ? "h-10 w-auto max-w-[190px]"
                    : "h-9 w-10 object-cover object-left"
                }
              `}
            />

            {/* Mobile close button */}
            {mobileOpen && (
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="
                  ml-auto
                  rounded-lg
                  p-2
                  text-slate-400
                  hover:bg-slate-100
                  hover:text-slate-700
                  lg:hidden
                "
              >
                <X size={18} />
              </button>
            )}
          </div>

          {/* =========================
              NAVIGATION
          ========================= */}
          <nav className="flex-1 overflow-y-auto px-3 py-5">

            {open && (
              <p
                className="
                  mb-3
                  px-3
                  text-[10px]
                  font-bold
                  uppercase
                  tracking-[0.16em]
                  text-slate-400
                "
              >
                Workspace
              </p>
            )}

            <div className="space-y-1">

              {navigation.map((item) => {
                const Icon = item.icon;

                return (
                  <NavLink
                    key={item.name}
                    to={item.path}
                    onClick={() => setMobileOpen(false)}
                    title={!open ? item.name : undefined}
                    className={({ isActive }) =>
                      `
                      group
                      flex
                      items-center
                      rounded-xl
                      transition-all
                      duration-150

                      ${
                        open
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

                    {open && (
                      <span className="truncate text-sm font-medium">
                        {item.name}
                      </span>
                    )}
                  </NavLink>
                );
              })}

            </div>
          </nav>

          {/* =========================
              SETTINGS
          ========================= */}
          <div className="shrink-0 border-t border-slate-100 p-3">

            <NavLink
              to="/settings"
              title={!open ? "Settings" : undefined}
              className={`
                flex
                items-center
                rounded-xl
                text-slate-500
                transition-all
                duration-150
                hover:bg-slate-50
                hover:text-slate-800

                ${
                  open
                    ? "gap-3 px-3 py-2.5"
                    : "justify-center px-2 py-3"
                }
              `}
            >
              <Settings
                size={19}
                strokeWidth={1.8}
              />

              {open && (
                <span className="text-sm font-medium">
                  Settings
                </span>
              )}
            </NavLink>

          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;