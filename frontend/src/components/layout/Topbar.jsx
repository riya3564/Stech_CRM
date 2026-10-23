
import { useEffect, useState } from "react";
import { Bell, Menu, ClipboardList, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

function Topbar({ onMenuClick }) {
  const navigate = useNavigate();

  const [counts, setCounts] = useState({
    unassigned: null,
    overdue: null,
    confirmations: null,
  });

  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadPendingActions() {
      try {
        setError("");

        const [callsResult, appointmentsResult] = await Promise.allSettled([
          api.get("/service-calls"),
          api.get("/appointments"),
        ]);

        if (!active) return;

        let unassigned = null;
        let overdue = null;
        let confirmations = null;

        if (callsResult.status === "fulfilled") {
          const data = callsResult.value.data;
          const calls = Array.isArray(data)
            ? data
            : data?.service_calls || data?.data || [];

          unassigned = calls.filter(
            (call) => String(call.status || "").toLowerCase() === "open"
          ).length;

          confirmations = calls.filter(
            (call) =>
              String(call.status || "").toLowerCase() ===
              "customer confirmation"
          ).length;
        }

        if (appointmentsResult.status === "fulfilled") {
          const data = appointmentsResult.value.data;
          const appointments = Array.isArray(data)
            ? data
            : data?.appointments || data?.data || [];

          const now = new Date();
          now.setHours(0, 0, 0, 0);

          overdue = appointments.filter((appointment) => {
            const status = String(appointment.status || "").toLowerCase();

            if (
              status.includes("complete") ||
              status.includes("closed") ||
              status.includes("cancel")
            ) {
              return false;
            }

            const dateValue =
              appointment.appointment_date ||
              appointment.scheduled_date;

            if (!dateValue) return false;

            const appointmentDate = new Date(dateValue);

            if (Number.isNaN(appointmentDate.getTime())) return false;

            appointmentDate.setHours(0, 0, 0, 0);
            return appointmentDate < now;
          }).length;
        }

        setCounts({ unassigned, overdue, confirmations });

        if (
          callsResult.status === "rejected" &&
          appointmentsResult.status === "rejected"
        ) {
          setError("Pending actions load nahi hue. Refresh karke dekho.");
        }
      } catch {
        if (active) {
          setError("Pending actions load nahi hue.");
        }
      }
    }

    loadPendingActions();

    const interval = window.setInterval(loadPendingActions, 60000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  const items = [
    {
      label: "Unassigned Calls",
      count: counts.unassigned,
      color: "bg-red-100 text-red-700",
      path: "/service-calls?filter=unassigned",
    },
    {
      label: "Overdue Appointments",
      count: counts.overdue,
      color: "bg-amber-100 text-amber-700",
      path: "/appointments?filter=overdue",
    },
    {
      label: "Pending Confirmations",
      count: counts.confirmations,
      color: "bg-blue-100 text-blue-700",
      path: "/service-calls?filter=pending-confirmation",
    },
  ];

  return (
    <header className="sticky top-0 z-30 h-[72px] border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex h-full items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
        <button
          type="button"
          onClick={onMenuClick}
          aria-label="Open menu"
          className="rounded-xl border border-slate-200 p-2 text-slate-600 hover:bg-slate-50 lg:hidden"
        >
          <Menu size={20} />
        </button>

        <div className="mx-auto hidden min-w-0 flex-1 justify-center md:flex">
          <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2">
            <div className="flex shrink-0 items-center gap-2">
              <ClipboardList size={20} className="text-blue-700" />
              <span className="whitespace-nowrap text-sm font-semibold text-slate-800">
                Pending Actions
              </span>
            </div>

            <div className="flex items-center gap-1">
              {items.map((item) => (
                <button
                  key={item.label}
                  type="button"
                  onClick={() => navigate(item.path)}
                  title={`Open ${item.label}`}
                  className="flex min-w-[100px] flex-col items-center rounded-xl px-2 py-1 transition hover:bg-white"
                >
                  <span
                    className={`rounded-lg px-3 py-0.5 text-sm font-bold ${item.color}`}
                  >
                    {item.count === null ? "—" : item.count}
                  </span>
                  <span className="mt-1 whitespace-nowrap text-[10px] text-slate-600">
                    {item.label}
                  </span>
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={() => window.location.reload()}
              title="Refresh pending actions"
              className="rounded-lg p-2 text-slate-500 hover:bg-white"
            >
              <RefreshCw size={15} />
            </button>
          </div>
        </div>

        <div className="ml-auto flex shrink-0 items-center gap-3">
          <button
            type="button"
            aria-label="Notifications"
            className="relative rounded-xl p-2.5 text-slate-500 hover:bg-slate-100"
          >
            <Bell size={19} />
            {error && (
              <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-red-500" />
            )}
          </button>

          <div className="flex items-center gap-3 border-l border-slate-200 pl-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-50 text-xs font-bold text-blue-900">
              AD
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-semibold text-slate-800">
                Admin User
              </p>
              <p className="text-xs text-slate-500">
                Service Administrator
              </p>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="absolute right-4 top-[72px] rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800 shadow-sm">
          {error}
        </div>
      )}
    </header>
  );
}

export default Topbar;
