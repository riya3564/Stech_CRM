
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Users,
  Search,
  RefreshCw,
  Eye,
  X,
  Phone,
  FileText,
  Package,
  LoaderCircle,
  AlertCircle,
} from "lucide-react";
import api from "../../services/api";

const css = {
  page: {
    padding: "30px 4%",
    minHeight: "100%",
    background: "#f6f8fb",
    color: "#172b4d",
    fontFamily: "Inter, Segoe UI, Arial, sans-serif",
  },
  heading: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 14,
    marginBottom: 24,
  },
  title: { margin: 0, fontSize: 28, fontWeight: 750, color: "#14233b" },
  subtitle: { margin: "8px 0 0", color: "#65758b", fontSize: 14 },
  button: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    padding: "10px 14px",
    border: "1px solid #d5deea",
    borderRadius: 8,
    background: "#fff",
    color: "#253b5b",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 600,
  },
  stats: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: 14,
    marginBottom: 20,
  },
  stat: {
    background: "#fff",
    border: "1px solid #e2e8f0",
    borderRadius: 10,
    padding: 20,
  },
  searchPanel: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: 14,
    marginBottom: 16,
    border: "1px solid #e2e8f0",
    background: "#fff",
    borderRadius: 10,
  },
  searchInput: {
    flex: 1,
    minWidth: 0,
    border: 0,
    outline: 0,
    padding: "8px 0",
    fontSize: 14,
    color: "#172b4d",
  },
  tableWrap: {
    overflowX: "auto",
    background: "#fff",
    border: "1px solid #e2e8f0",
    borderRadius: 10,
  },
  table: { width: "100%", minWidth: 760, borderCollapse: "collapse" },
  th: {
    textAlign: "left",
    padding: "15px 16px",
    background: "#f8fafc",
    color: "#62748b",
    fontSize: 12,
    fontWeight: 700,
    borderBottom: "1px solid #e5eaf1",
    whiteSpace: "nowrap",
  },
  td: {
    padding: "15px 16px",
    borderBottom: "1px solid #edf0f5",
    fontSize: 14,
    verticalAlign: "middle",
  },
  overlay: {
    position: "fixed",
    inset: 0,
    zIndex: 1000,
    background: "rgba(15,28,48,.45)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 18,
  },
  modal: {
    width: "min(780px, 100%)",
    maxHeight: "90vh",
    overflowY: "auto",
    background: "#fff",
    borderRadius: 12,
    boxShadow: "0 18px 60px rgba(0,0,0,.18)",
  },
  modalHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "18px 22px",
    borderBottom: "1px solid #e7ebf2",
  },
  modalBody: { padding: 22 },
  message: {
    padding: 14,
    borderRadius: 8,
    marginBottom: 16,
    background: "#fff7ed",
    color: "#9a3412",
    fontSize: 14,
  },
};

function getArray(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.value)) return data.value;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function valueOf(item, keys, fallback = "") {
  for (const key of keys) {
    if (item?.[key] !== undefined && item[key] !== null && item[key] !== "") {
      return item[key];
    }
  }
  return fallback;
}

function customerId(customer) {
  return valueOf(customer, ["id", "customer_id", "customerId"]);
}

function customerName(customer) {
  return valueOf(
    customer,
    ["customer_name", "name", "full_name", "customerName"],
    "Unnamed Customer"
  );
}

function phoneOf(customer) {
  return valueOf(
    customer,
    ["mobile", "mobile_number", "phone", "phone_number", "contact_number"],
    ""
  );
}

function customerNumber(customer) {
  return valueOf(
    customer,
    ["customer_number", "customer_code", "customer_no", "customer_ref"],
    ""
  );
}

function callCustomerId(call) {
  return valueOf(call, ["customer_id", "customerId", "customer"]);
}

function callNumber(call) {
  return valueOf(
    call,
    ["call_number", "complaint_number", "complaint_id", "call_no", "call_code"],
    `Call #${valueOf(call, ["id", "service_call_id"], "-")}`
  );
}

function callStatus(call) {
  return valueOf(call, ["status", "call_status", "current_status"], "Open");
}

function callCustomerName(call) {
  return valueOf(
    call,
    ["customer_name", "customer_full_name"],
    call?.customer?.name || ""
  );
}

function callPhone(call) {
  return valueOf(
    call,
    ["customer_phone", "mobile", "phone", "phone_number"],
    call?.customer?.mobile || ""
  );
}

function serialNumber(call) {
  return valueOf(call, ["serial_number", "serial_no", "product_serial_number"]);
}

function dateOf(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function statusColors(status) {
  const value = String(status).toLowerCase();
  if (value.includes("closed")) {
    return { background: "#dcfce7", color: "#166534" };
  }
  if (value.includes("progress") || value.includes("assigned")) {
    return { background: "#dbeafe", color: "#1d4ed8" };
  }
  if (value.includes("part")) {
    return { background: "#fff7ed", color: "#c2410c" };
  }
  return { background: "#f1f5f9", color: "#475569" };
}

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [calls, setCalls] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  const loadData = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      else setRefreshing(true);
      setError("");

      const [customerResult, callResult] = await Promise.allSettled([
        api.get("/customers"),
        api.get("/service-calls"),
      ]);

      if (customerResult.status === "rejected") {
        throw new Error(
          customerResult.reason?.response?.data?.message ||
          customerResult.reason?.message ||
          "Customers load nahi ho paaye."
        );
      }

      setCustomers(getArray(customerResult.value.data));

      if (callResult.status === "fulfilled") {
        setCalls(getArray(callResult.value.data));
      } else {
        setCalls([]);
      }
    } catch (err) {
      setError(err.message || "Data load nahi ho paaya.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const customerRows = useMemo(() => {
    const query = search.trim().toLowerCase();

    return customers.filter((customer) => {
      const relatedCalls = calls.filter((call) => {
        const id = customerId(customer);
        const linkedId = callCustomerId(call);

        if (id !== "" && linkedId !== "") {
          return String(id) === String(linkedId);
        }

        const name = callCustomerName(call).toLowerCase();
        const phone = callPhone(call);
        return (
          name === customerName(customer).toLowerCase() ||
          (phone && phone === phoneOf(customer))
        );
      });

      const searchFields = [
        customerName(customer),
        phoneOf(customer),
        customerNumber(customer),
        customerId(customer),
        valueOf(customer, ["email", "email_address"]),
        valueOf(customer, ["serial_number", "serial_no"]),
        ...relatedCalls.map((call) => callNumber(call)),
        ...relatedCalls.map((call) => serialNumber(call)),
      ];

      return !query || searchFields.some((value) =>
        String(value ?? "").toLowerCase().includes(query)
      );
    });
  }, [customers, calls, search]);

  function complaintsFor(customer) {
    const id = customerId(customer);
    const name = customerName(customer).toLowerCase();
    const phone = phoneOf(customer);

    return calls.filter((call) => {
      const linkedId = callCustomerId(call);

      if (id !== "" && linkedId !== "") {
        return String(id) === String(linkedId);
      }

      const linkedName = callCustomerName(call).toLowerCase();
      const linkedPhone = callPhone(call);

      return (
        (name && linkedName === name) ||
        (phone && linkedPhone === phone)
      );
    });
  }

  return (
    <div style={css.page}>
      <div style={css.heading}>
        <div>
          <h1 style={css.title}>Customers</h1>
          <p style={css.subtitle}>
            Customers aur unki service complaints ek jagah manage karein.
          </p>
        </div>
        <button
          type="button"
          style={css.button}
          onClick={() => loadData(false)}
          disabled={refreshing}
        >
          <RefreshCw size={16} />
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error && <div style={css.message}>{error}</div>}

      <div style={css.stats}>
        <div style={css.stat}>
          <Users size={19} color="#175ce5" />
          <div style={{ color: "#65758b", fontSize: 13, marginTop: 12 }}>
            Total Customers
          </div>
          <div style={{ fontSize: 27, fontWeight: 750, marginTop: 5 }}>
            {loading ? "—" : customers.length}
          </div>
        </div>
        <div style={css.stat}>
          <FileText size={19} color="#175ce5" />
          <div style={{ color: "#65758b", fontSize: 13, marginTop: 12 }}>
            Total Service Calls
          </div>
          <div style={{ fontSize: 27, fontWeight: 750, marginTop: 5 }}>
            {loading ? "—" : calls.length}
          </div>
        </div>
        <div style={css.stat}>
          <Search size={19} color="#175ce5" />
          <div style={{ color: "#65758b", fontSize: 13, marginTop: 12 }}>
            Matching Customers
          </div>
          <div style={{ fontSize: 27, fontWeight: 750, marginTop: 5 }}>
            {loading ? "—" : customerRows.length}
          </div>
        </div>
      </div>

      <div style={css.searchPanel}>
        <Search size={19} color="#8797ad" />
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by customer name, mobile, customer number, complaint ID or serial number..."
          aria-label="Search customers and complaints"
          style={css.searchInput}
        />
        {search && (
          <button
            type="button"
            style={{ ...css.button, padding: 7 }}
            onClick={() => setSearch("")}
            aria-label="Clear search"
          >
            <X size={16} />
          </button>
        )}
      </div>

      <div style={{ marginBottom: 12, color: "#64748b", fontSize: 13 }}>
        Showing {customerRows.length} of {customers.length} customers
      </div>

      <div style={css.tableWrap}>
        <table style={css.table}>
          <thead>
            <tr>
              {["CUSTOMER", "CUSTOMER NUMBER", "MOBILE", "EMAIL", "COMPLAINTS", "ACTION"].map((heading) => (
                <th key={heading} style={css.th}>{heading}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} style={{ ...css.td, textAlign: "center", padding: 36 }}>
                  <LoaderCircle size={18} style={{ verticalAlign: "middle", marginRight: 8 }} />
                  Loading customers...
                </td>
              </tr>
            ) : customerRows.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ ...css.td, textAlign: "center", padding: 36, color: "#64748b" }}>
                  {error ? "Customers data load nahi hua." : "Koi matching customer nahi mila."}
                </td>
              </tr>
            ) : (
              customerRows.map((customer, index) => {
                const customerCalls = complaintsFor(customer);

                return (
                  <tr key={customerId(customer) || index}>
                    <td style={css.td}>
                      <div style={{ fontWeight: 700 }}>
                        {customerName(customer)}
                      </div>
                      <div style={{ color: "#73839a", fontSize: 12, marginTop: 5 }}>
                        ID: {customerId(customer) || "—"}
                      </div>
                    </td>
                    <td style={css.td}>{customerNumber(customer) || "—"}</td>
                    <td style={css.td}>
                      {phoneOf(customer) ? (
                        <span style={{ display: "inline-flex", gap: 7, alignItems: "center" }}>
                          <Phone size={14} color="#71839b" />
                          {phoneOf(customer)}
                        </span>
                      ) : "—"}
                    </td>
                    <td style={css.td}>
                      {valueOf(customer, ["email", "email_address"], "—")}
                    </td>
                    <td style={css.td}>
                      <span style={{ background: "#eff6ff", color: "#1d4ed8", borderRadius: 20, padding: "5px 10px", fontSize: 12, fontWeight: 700 }}>
                        {customerCalls.length}
                      </span>
                    </td>
                    <td style={css.td}>
                      <button
                        type="button"
                        style={css.button}
                        onClick={() => setSelectedCustomer(customer)}
                      >
                        <Eye size={15} /> View Details
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {selectedCustomer && (
        <div
          style={css.overlay}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setSelectedCustomer(null);
          }}
        >
          <div style={css.modal} role="dialog" aria-modal="true" aria-label="Customer details">
            <div style={css.modalHeader}>
              <div>
                <h2 style={{ margin: 0, fontSize: 20 }}>
                  {customerName(selectedCustomer)}
                </h2>
                <p style={{ margin: "6px 0 0", color: "#64748b", fontSize: 13 }}>
                  Customer ID: {customerId(selectedCustomer) || "—"}
                </p>
              </div>
              <button
                type="button"
                style={{ ...css.button, padding: 8 }}
                onClick={() => setSelectedCustomer(null)}
                aria-label="Close customer details"
              >
                <X size={18} />
              </button>
            </div>

            <div style={css.modalBody}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 14 }}>
                {[
                  ["Customer Number", customerNumber(selectedCustomer) || "—"],
                  ["Mobile", phoneOf(selectedCustomer) || "—"],
                  ["Email", valueOf(selectedCustomer, ["email", "email_address"], "—")],
                  ["Address", valueOf(selectedCustomer, ["address", "service_address"], "—")],
                ].map(([label, value]) => (
                  <div key={label}>
                    <div style={{ fontSize: 12, color: "#65758b", marginBottom: 6, fontWeight: 650 }}>
                      {label}
                    </div>
                    <div style={{ fontSize: 14, overflowWrap: "anywhere" }}>{value}</div>
                  </div>
                ))}
              </div>

              <div style={{ borderTop: "1px solid #e7ebf2", margin: "22px 0 18px" }} />

              <h3 style={{ margin: "0 0 14px", fontSize: 17 }}>
                <FileText size={17} style={{ verticalAlign: "middle", marginRight: 8 }} />
                Customer Complaints
              </h3>

              {complaintsFor(selectedCustomer).length === 0 ? (
                <div style={{ padding: 20, border: "1px solid #e5eaf1", borderRadius: 8, color: "#64748b", fontSize: 14 }}>
                  Is customer ki linked service complaints nahi mili.
                </div>
              ) : (
                <div style={{ overflowX: "auto", border: "1px solid #e2e8f0", borderRadius: 8 }}>
                  <table style={{ width: "100%", minWidth: 580, borderCollapse: "collapse" }}>
                    <thead>
                      <tr>
                        {["COMPLAINT ID", "SERIAL NUMBER", "STATUS", "DATE"].map((heading) => (
                          <th key={heading} style={css.th}>{heading}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {complaintsFor(selectedCustomer).map((call, index) => {
                        const status = callStatus(call);
                        return (
                          <tr key={valueOf(call, ["id", "service_call_id"], index)}>
                            <td style={css.td}>
                              <div style={{ fontWeight: 700 }}>{callNumber(call)}</div>
                            </td>
                            <td style={css.td}>
                              <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                                <Package size={14} color="#64748b" />
                                {serialNumber(call) || "—"}
                              </span>
                            </td>
                            <td style={css.td}>
                              <span style={{ ...statusColors(status), padding: "5px 9px", borderRadius: 20, fontSize: 12, fontWeight: 650, whiteSpace: "nowrap" }}>
                                {status}
                              </span>
                            </td>
                            <td style={css.td}>
                              {dateOf(valueOf(call, ["created_at", "created_on", "call_date"]))}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 20 }}>
                <button type="button" style={css.button} onClick={() => setSelectedCustomer(null)}>
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
