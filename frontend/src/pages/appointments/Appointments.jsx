
import { useEffect, useMemo, useState } from "react";
import api from "../../services/api";

const styles = {
  page: { padding: "24px", color: "#1f2937" },
  heading: { margin: "0 0 6px", fontSize: "26px", fontWeight: 700 },
  subtitle: { color: "#6b7280", marginBottom: "22px" },
  cards: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: "14px",
    marginBottom: "22px",
  },
  card: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    padding: "17px",
  },
  cardLabel: { color: "#6b7280", fontSize: "13px", marginBottom: "8px" },
  cardValue: { fontSize: "25px", fontWeight: 700 },
  toolbar: {
    display: "flex",
    gap: "12px",
    flexWrap: "wrap",
    marginBottom: "16px",
  },
  input: {
    padding: "11px 12px",
    border: "1px solid #d1d5db",
    borderRadius: "7px",
    minWidth: "220px",
    flex: "1",
    fontSize: "14px",
  },
  button: {
    border: "none",
    borderRadius: "7px",
    background: "#2563eb",
    color: "#fff",
    padding: "11px 17px",
    cursor: "pointer",
    fontWeight: 600,
  },
  panel: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    overflow: "hidden",
  },
  tableWrap: { overflowX: "auto" },
  table: { width: "100%", borderCollapse: "collapse", minWidth: "1050px" },
  th: {
    textAlign: "left",
    background: "#f9fafb",
    padding: "13px",
    borderBottom: "1px solid #e5e7eb",
    fontSize: "12px",
    color: "#6b7280",
    whiteSpace: "nowrap",
  },
  td: {
    padding: "14px 13px",
    borderBottom: "1px solid #f3f4f6",
    fontSize: "13px",
    verticalAlign: "top",
  },
  muted: { color: "#6b7280", fontSize: "12px", marginTop: "5px" },
};

function getList(response) {
  const data = response?.data ?? response;

  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.appointments)) return data.appointments;
  if (Array.isArray(data?.service_calls)) return data.service_calls;
  if (Array.isArray(data?.serviceCalls)) return data.serviceCalls;
  if (Array.isArray(data?.data)) return data.data;
  if (Array.isArray(data?.results)) return data.results;

  return [];
}

function formatDate(value) {
  if (!value) return "Not scheduled";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function getCustomerName(call) {
  return (
    call?.customer?.name ||
    call?.customer?.customer_name ||
    call?.customer_name ||
    "Not available"
  );
}

function getCustomerPhone(call) {
  return (
    call?.customer?.mobile ||
    call?.customer?.mobile_number ||
    call?.customer?.phone ||
    call?.customer_mobile ||
    call?.mobile_number ||
    "Not available"
  );
}

function getProductName(call) {
  return (
    call?.product_model?.model_name ||
    call?.product_model?.name ||
    call?.product_model_name ||
    call?.product?.name ||
    "Not available"
  );
}

function Status({ value }) {
  const status = value || "Scheduled";
  const lower = String(status).toLowerCase();

  let background = "#dbeafe";
  let color = "#1d4ed8";

  if (lower.includes("complete") || lower.includes("closed")) {
    background = "#dcfce7";
    color = "#166534";
  } else if (
    lower.includes("cancel") ||
    lower.includes("reject") ||
    lower.includes("fail")
  ) {
    background = "#fee2e2";
    color = "#991b1b";
  } else if (lower.includes("progress")) {
    background = "#fef3c7";
    color = "#92400e";
  }

  return (
    <span
      style={{
        display: "inline-block",
        background,
        color,
        borderRadius: "20px",
        padding: "5px 9px",
        fontSize: "12px",
        fontWeight: 600,
        whiteSpace: "nowrap",
      }}
    >
      {status}
    </span>
  );
}

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [serviceCalls, setServiceCalls] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  async function loadAppointments(showRefresh = false) {
    if (showRefresh) setRefreshing(true);
    else setLoading(true);

    setError("");

    try {
      const appointmentResponse = await api.get("/appointments");
      const appointmentList = getList(appointmentResponse);
      setAppointments(appointmentList);

      try {
        const callsResponse = await api.get("/service-calls");
        setServiceCalls(getList(callsResponse));
      } catch {
        // Appointment list remains usable if the calls endpoint is unavailable.
        setServiceCalls([]);
      }
    } catch (err) {
      setError(
        err?.response?.data?.message ||
          err?.response?.data?.error ||
          "Appointments load nahi ho paaye. Backend/API check karna hoga."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadAppointments();
  }, []);

  const callMap = useMemo(() => {
    const map = new Map();

    serviceCalls.forEach((call) => {
      const keys = [
        call?.id,
        call?.service_call_id,
        call?.call_id,
        call?.complaint_id,
      ];

      keys.forEach((key) => {
        if (key !== undefined && key !== null) {
          map.set(String(key), call);
        }
      });
    });

    return map;
  }, [serviceCalls]);

  const rows = useMemo(() => {
    return appointments.map((appointment) => {
      const callId =
        appointment?.service_call_id ??
        appointment?.call_id ??
        appointment?.service_call?.id;

      const linkedCall =
        appointment?.service_call ||
        callMap.get(String(callId)) ||
        {};

      return { appointment, call: linkedCall, callId };
    });
  }, [appointments, callMap]);

  const filteredRows = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return rows;

    return rows.filter(({ appointment, call, callId }) => {
      const values = [
        appointment?.id,
        appointment?.appointment_id,
        appointment?.complaint_id,
        appointment?.engineer?.name,
        appointment?.engineer_name,
        appointment?.asc?.name,
        appointment?.asc_name,
        appointment?.status,
        appointment?.appointment_point,
        callId,
        call?.complaint_id,
        call?.call_id,
        call?.serial_number,
        call?.customer?.name,
        call?.customer?.customer_name,
        call?.customer?.mobile,
        call?.customer_name,
        call?.customer_mobile,
        call?.complaint_description,
      ];

      return values.some(
        (value) =>
          value !== undefined &&
          value !== null &&
          String(value).toLowerCase().includes(term)
      );
    });
  }, [rows, search]);

  const today = new Date().toDateString();

  const todayCount = appointments.filter((appointment) => {
    const value = appointment?.appointment_date;
    return value && new Date(value).toDateString() === today;
  }).length;

  const scheduledCount = appointments.filter((appointment) =>
    ["scheduled", "confirmed"].includes(
      String(appointment?.status || "Scheduled").toLowerCase()
    )
  ).length;

  const completedCount = appointments.filter((appointment) =>
    String(appointment?.status || "").toLowerCase().includes("complete")
  ).length;

  return (
    <div style={styles.page}>
      <h1 style={styles.heading}>Appointments</h1>
      <div style={styles.subtitle}>
        Service appointments, customer details and engineer schedules
      </div>

      <div style={styles.cards}>
        <div style={styles.card}>
          <div style={styles.cardLabel}>Total Appointments</div>
          <div style={styles.cardValue}>{appointments.length}</div>
        </div>
        <div style={styles.card}>
          <div style={styles.cardLabel}>Today's Appointments</div>
          <div style={styles.cardValue}>{todayCount}</div>
        </div>
        <div style={styles.card}>
          <div style={styles.cardLabel}>Scheduled / Confirmed</div>
          <div style={styles.cardValue}>{scheduledCount}</div>
        </div>
        <div style={styles.card}>
          <div style={styles.cardLabel}>Completed</div>
          <div style={styles.cardValue}>{completedCount}</div>
        </div>
      </div>

      <div style={styles.toolbar}>
        <input
          style={styles.input}
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search complaint, customer, mobile, serial no..."
          aria-label="Search appointments"
        />
        <button
          style={styles.button}
          onClick={() => loadAppointments(true)}
          disabled={refreshing || loading}
        >
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div style={styles.panel}>
        {loading ? (
          <div style={{ padding: "35px", textAlign: "center" }}>
            Loading appointments...
          </div>
        ) : error ? (
          <div style={{ padding: "25px", color: "#b91c1c" }}>
            <p>{error}</p>
            <button style={styles.button} onClick={() => loadAppointments()}>
              Try Again
            </button>
          </div>
        ) : filteredRows.length === 0 ? (
          <div style={{ padding: "35px", textAlign: "center" }}>
            <strong>
              {search ? "No matching appointments found" : "No appointments found"}
            </strong>
            <p style={styles.muted}>
              {search
                ? "Search text change karke dekho."
                : "Appointments backend mein create hone ke baad yahan dikhengi."}
            </p>
          </div>
        ) : (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Complaint / Call</th>
                  <th style={styles.th}>Customer</th>
                  <th style={styles.th}>Product Details</th>
                  <th style={styles.th}>Appointment</th>
                  <th style={styles.th}>Engineer / ASC</th>
                  <th style={styles.th}>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map(({ appointment, call, callId }, index) => (
                  <tr key={appointment?.id ?? appointment?.appointment_id ?? index}>
                    <td style={styles.td}>
                      <strong>
                        {appointment?.complaint_id ||
                          call?.complaint_id ||
                          call?.call_id ||
                          callId ||
                          "Not available"}
                      </strong>
                      <div style={styles.muted}>
                        Appointment ID: {appointment?.id ?? appointment?.appointment_id ?? "—"}
                      </div>
                      <div style={styles.muted}>
                        Call ID: {callId ?? "—"}
                      </div>
                    </td>

                    <td style={styles.td}>
                      <strong>{getCustomerName(call)}</strong>
                      <div style={styles.muted}>{getCustomerPhone(call)}</div>
                    </td>

                    <td style={styles.td}>
                      <strong>{getProductName(call)}</strong>
                      <div style={styles.muted}>
                        Serial No: {call?.serial_number || "Not available"}
                      </div>
                      <div style={styles.muted}>
                        {call?.complaint_description || "Complaint details unavailable"}
                      </div>
                    </td>

                    <td style={styles.td}>
                      <strong>{formatDate(appointment?.appointment_date)}</strong>
                      <div style={styles.muted}>
                        Time: {appointment?.appointment_time || "Not set"}
                      </div>
                      <div style={styles.muted}>
                        Point: {appointment?.appointment_point || "Not set"}
                      </div>
                    </td>

                    <td style={styles.td}>
                      <strong>
                        {appointment?.engineer?.name ||
                          appointment?.engineer_name ||
                          `Engineer ID: ${appointment?.engineer_id ?? "—"}`}
                      </strong>
                      <div style={styles.muted}>
                        {appointment?.asc?.name ||
                          appointment?.asc_name ||
                          `ASC ID: ${appointment?.asc_id ?? "—"}`}
                      </div>
                    </td>

                    <td style={styles.td}>
                      <Status value={appointment?.status} />
                      {appointment?.remarks && (
                        <div style={styles.muted}>
                          Remarks: {appointment.remarks}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
