import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  Clock3,
  FilePlus2,
  Loader2,
  Package,
  RefreshCw,
  UserRound,
  Users,
  X,
  Wrench,
} from "lucide-react";

import api from "../../services/api";

const STATUS_BUCKETS = [
  { key: "Assigned", label: "Assigned", icon: UserRound },
  { key: "In Progress", label: "In Progress / Testing", icon: Activity },
  { key: "Part Flow", label: "Part Required / Pending", icon: Package },
  { key: "Reopened", label: "Call Reopened", icon: RefreshCw },
  { key: "Cancelled", label: "Call Cancelled", icon: X },
  { key: "Closed", label: "Call Closed", icon: CheckCircle2 },
];

function getArray(data) {
  if (Array.isArray(data)) return data;

  if (Array.isArray(data?.value)) return data.value;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;

  return [];
}

function formatDate(value) {
  if (!value) return "-";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}


function normaliseStatus(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ");
}

function getCallStatus(call) {
  return normaliseStatus(
    call?.status ?? call?.call_status ?? call?.current_status ??
    call?.service_call_status ?? call?.workflow_status ?? call?.state
  );
}

// A call belongs to one primary lifecycle bucket, so KPI totals don't overlap.
function getLifecycleBucket(call) {
  const status = getCallStatus(call);
  if (!status) return "Other";
  if (status.includes("reopen")) return "Reopened";
  if (status.includes("cancel")) return "Cancelled";
  if (status === "closed" || status.includes("call closed") || status.includes("closure complete")) return "Closed";
  if (status.includes("part") || status.includes("spare") || status.includes("waiting for part")) return "Part Flow";
  if (status.includes("appointment") || status.includes("scheduled")) return "Appointment Scheduled";
  if (status.includes("revisit") || status.includes("repeat visit")) return "Revisit";
  if (status.includes("assign")) return "Assigned";
  if (status.includes("progress") || status.includes("testing") || status.includes("diagnos") || status.includes("repair") || status.includes("confirmation") || status === "working") return "In Progress";
  if (["open", "registered", "new", "validated", "pending", "created"].includes(status) || status.includes("open /") || status.includes("registered")) return "Open";
  return "Other";
}

function matchesBucket(call, key) {
  const status = getCallStatus(call);
  if (key === "SLA") {
    const dueValue = call?.sla_due_at ?? call?.sla_due_date ?? call?.sla_deadline;
    if (!dueValue) return false;
    const due = new Date(dueValue).getTime();
    const bucket = getLifecycleBucket(call);
    return !Number.isNaN(due) && due <= Date.now() + 24 * 60 * 60 * 1000 && !["Closed", "Cancelled"].includes(bucket);
  }
  if (["Part Required", "Part Pending", "Part Transit"].includes(key)) {
    if (key === "Part Required") return status.includes("part required") || status.includes("spare required");
    if (key === "Part Pending") return status.includes("part pending") || status.includes("pending part") || status.includes("waiting for part");
    return status.includes("part in transit") || status.includes("part ordered") || status === "ordered" || status === "in transit";
  }
  return getLifecycleBucket(call) === key;
}

function statusClass(status) {
  const value = String(status || "").toLowerCase();

  if (value === "closed") return "status closed";
  if (value === "in progress") return "status progress";
  if (value === "open") return "status open";
  if (value === "validated") return "status validated";
  if (value === "assigned") return "status assigned";
  if (value.includes("appointment")) return "status appointment";
  if (value.includes("part")) return "status part";
  if (value.includes("confirmation")) return "status confirmation";

  return "status";
}

export default function Dashboard() {
  const [serviceCalls, setServiceCalls] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [selectedBucket, setSelectedBucket] = useState(null);
  const [selectedCall, setSelectedCall] = useState(null);
  const [statusSaving, setStatusSaving] = useState(false);
  const [statusDraft, setStatusDraft] = useState("");

  const [showNewCall, setShowNewCall] = useState(false);

  const [engineers, setEngineers] = useState([]);
  const [assigningCall, setAssigningCall] = useState(null);
  const [selectedEngineer, setSelectedEngineer] = useState("");
  const [assignmentRemarks, setAssignmentRemarks] = useState("");

  const [newCall, setNewCall] = useState({
    customer_id: "",
    product_model_id: "",
    call_type_id: "",
    symptom_id: "",
    complaint_description: "",
    state: "",
    district: "",
    serial_number: "",
    invoice_number: "",
    purchase_date: "",
    installation_date: "",
    warranty_start_date: "",
    warranty_end_date: "",
    city: "",
    pin_code: "",
    service_address: "",
    priority: "Normal",
  });

  const [newCallLoading, setNewCallLoading] = useState(false);
  const [newCallMessage, setNewCallMessage] = useState("");

  const [customers, setCustomers] = useState([]);
  const [customerSearch, setCustomerSearch] = useState("");
  const [productModels, setProductModels] = useState([]);
  const [callTypes, setCallTypes] = useState([]);
  const [symptoms, setSymptoms] = useState([]);
  const [ascCentres, setAscCentres] = useState([]);

  const filteredCustomers = useMemo(() => {
    const query = customerSearch.trim().toLowerCase();
    if (!query) return customers;
    return customers.filter((customer) => {
      const searchable = [
        customer.customer_name, customer.name, customer.mobile,
        customer.mobile_number, customer.phone, customer.phone_number,
        customer.email, customer.customer_code,
      ].filter(Boolean).join(" ").toLowerCase();
      return searchable.includes(query);
    });
  }, [customers, customerSearch]);

  const selectedCustomer = useMemo(
    () => customers.find((customer) => String(customer.id) === String(newCall.customer_id)),
    [customers, newCall.customer_id]
  );

  const selectedProduct = useMemo(
    () => productModels.find((product) => String(product.id) === String(newCall.product_model_id)),
    [productModels, newCall.product_model_id]
  );

  const selectedCallType = useMemo(
    () => callTypes.find((item) => String(item.id) === String(newCall.call_type_id)),
    [callTypes, newCall.call_type_id]
  );

  async function loadDashboard(showSpinner = true) {
    try {
      if (showSpinner) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      setError("");

      const [callsResponse, assignmentsResponse] =
        await Promise.allSettled([
          api.get("/service-calls"),
          api.get("/asc-assignments"),
        ]);

      if (callsResponse.status === "rejected") {
        const backendError =
          callsResponse.reason?.response?.data?.message ||
          callsResponse.reason?.message ||
          "Unable to load service calls.";

        throw new Error(backendError);
      }

      const callsData = callsResponse.value.data;

      const calls = getArray(callsData);

      setServiceCalls(calls);

      if (assignmentsResponse.status === "fulfilled") {
        setAssignments(getArray(assignmentsResponse.value.data));
      } else {
        setAssignments([]);
      }
    } catch (err) {
      console.error("Dashboard API error:", err);

      setError(
        err?.message ||
          err?.response?.data?.message ||
          "Backend data load nahi ho raha."
      );

      setServiceCalls([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  async function loadMasterData() {
    const requests = [
      ["customers", "/customers", setCustomers],
      ["productModels", "/product-models", setProductModels],
      ["callTypes", "/call-types", setCallTypes],
      ["symptoms", "/symptoms", setSymptoms],
      ["engineers", "/engineers", setEngineers],
      ["ascCentres", "/asc", setAscCentres],
    ];

    await Promise.allSettled(
      requests.map(async ([, endpoint, setter]) => {
        try {
          const response = await api.get(endpoint);
          setter(getArray(response.data));
        } catch (err) {
          console.warn(`Unable to load ${endpoint}`, err);
        }
      })
    );
  }

  useEffect(() => {
    loadDashboard(true);
    loadMasterData();
  }, []);

  const assignmentMap = useMemo(() => {
    const map = {};

    assignments.forEach((assignment) => {
      if (assignment.service_call_id != null) {
        map[assignment.service_call_id] = assignment;
      }
    });

    return map;
  }, [assignments]);

  const counts = useMemo(() => {
    const result = {
      open: 0, slaRisk: 0, partPending: 0, assigned: 0, inProgress: 0,
      appointment: 0, partRequired: 0, partTransit: 0, revisit: 0,
      cancelled: 0, closed: 0, reopened: 0,
    };
    const now = Date.now();
    const next24Hours = now + 24 * 60 * 60 * 1000;

    serviceCalls.forEach((call) => {
      const bucket = getLifecycleBucket(call);
      if (bucket === "Open") result.open += 1;
      else if (bucket === "Assigned") result.assigned += 1;
      else if (bucket === "Appointment Scheduled") result.appointment += 1;
      else if (bucket === "In Progress") result.inProgress += 1;
      else if (bucket === "Part Flow") {
        const status = getCallStatus(call);
        if (status.includes("required") || status.includes("spare")) result.partRequired += 1;
        else if (status.includes("pending") || status.includes("waiting")) result.partPending += 1;
        else result.partTransit += 1;
      }
      else if (bucket === "Revisit") result.revisit += 1;
      else if (bucket === "Cancelled") result.cancelled += 1;
      else if (bucket === "Closed") result.closed += 1;
      else if (bucket === "Reopened") result.reopened += 1;

      const dueValue = call?.sla_due_at ?? call?.sla_due_date ?? call?.sla_deadline;
      if (dueValue && !["Closed", "Cancelled"].includes(bucket)) {
        const due = new Date(dueValue).getTime();
        if (!Number.isNaN(due) && due <= next24Hours) result.slaRisk += 1;
      }
    });
    result.partPending = serviceCalls.filter((call) => matchesBucket(call, "Part Pending")).length;
    return result;
  }, [serviceCalls]);

  function getCustomerName(call) {
    if (call.customer_name) return call.customer_name;

    const customer = customers.find(
      (item) =>
        Number(item.id) === Number(call.customer_id)
    );

    return (
      customer?.customer_name ||
      customer?.name ||
      `Customer #${call.customer_id ?? "-"}`
    );
  }

  function getProductName(call) {
    if (call.product_model_name) {
      return call.product_model_name;
    }

    const product = productModels.find(
      (item) =>
        Number(item.id) === Number(call.product_model_id)
    );

    return (
      product?.product_model_name ||
      product?.model_name ||
      product?.name ||
      `Product Model #${call.product_model_id ?? "-"}`
    );
  }

  function getEngineer(call) {
    const assignment = assignmentMap[call.id];

    return (
      call.engineer_name ||
      assignment?.engineer_name ||
      "Unassigned"
    );
  }

  function openBucket(bucket) {
    setSelectedCall(null);
    setSelectedBucket(bucket);
  }

  async function updateCallStatus() {
    if (!selectedCall || !statusDraft) return;
    setStatusSaving(true);
    let lastError;
    // Try the common update contracts used by service-call APIs. The backend
    // must implement at least one of these routes for the status to persist.
    const attempts = [
      () => api.patch(`/service-calls/${selectedCall.id}`, { status: statusDraft }),
      () => api.put(`/service-calls/${selectedCall.id}`, { status: statusDraft }),
      () => api.patch(`/service-calls/${selectedCall.id}/status`, { status: statusDraft }),
      () => api.put(`/service-calls/${selectedCall.id}/status`, { status: statusDraft }),
    ];
    try {
      let saved = false;
      for (const attempt of attempts) {
        try { await attempt(); saved = true; break; }
        catch (err) { lastError = err; }
      }
      if (!saved) throw lastError;
      const updatedCall = { ...selectedCall, status: statusDraft, call_status: statusDraft };
      setSelectedCall(updatedCall);
      setServiceCalls((current) => current.map((call) => Number(call.id) === Number(updatedCall.id) ? { ...call, status: statusDraft, call_status: statusDraft } : call));
      await loadDashboard(false);
      alert("Service call status updated.");
    } catch (err) {
      console.error("Status update failed:", err);
      alert(err?.response?.data?.message || "Status update nahi hua. Backend mein service-call status update route/field configure hona zaroori hai. Backend terminal ka error check karo.");
    } finally {
      setStatusSaving(false);
    }
  }

  function closePanels() {
    setSelectedBucket(null);
    setSelectedCall(null);
    setAssigningCall(null);
  }

  function openCall(call) {
    setSelectedCall(call);
    setStatusDraft(call?.status || call?.call_status || call?.current_status || "Open");
    setSelectedBucket(null);
  }

  async function startAssign(call) {
    setAssigningCall(call);
    setSelectedEngineer("");
    setAssignmentRemarks("");

    if (engineers.length === 0) {
      try {
        const response = await api.get("/engineers");
        setEngineers(getArray(response.data));
      } catch (err) {
        console.error(err);
      }
    }
  }

  async function assignEngineer() {
    if (!assigningCall || !selectedEngineer) {
      return;
    }

    try {
      setRefreshing(true);

      await api.post(
        `/asc-assignments/service-calls/${assigningCall.id}/assign-engineer`,
        {
          engineer_id: Number(selectedEngineer),
          remarks:
            assignmentRemarks ||
            "Assigned from dashboard",
        }
      );

      alert("Engineer assigned successfully.");

      setAssigningCall(null);
      setSelectedEngineer("");
      setAssignmentRemarks("");

      await loadDashboard(false);
    } catch (err) {
      console.error("Engineer assignment error:", err);

      alert(
        err?.response?.data?.message ||
          "Engineer assign nahi ho paya."
      );
    } finally {
      setRefreshing(false);
    }
  }

  async function createServiceCall(event) {
    event.preventDefault();

    try {
      setNewCallLoading(true);
      setNewCallMessage("");

      if (
        !newCall.customer_id ||
        !newCall.product_model_id ||
        !newCall.call_type_id ||
        !newCall.symptom_id ||
        !newCall.state.trim() ||
        !newCall.district.trim() ||
        !newCall.complaint_description.trim()
      ) {
        setNewCallMessage("Please complete all required fields before submitting.");
        setNewCallLoading(false);
        return;
      }

      const payload = {
        customer_id: Number(newCall.customer_id),
        product_model_id: Number(newCall.product_model_id),
        call_type_id: Number(newCall.call_type_id),
        symptom_id: Number(newCall.symptom_id),
        complaint_description: newCall.complaint_description.trim(),
        state: newCall.state.trim(),
        district: newCall.district.trim(),
        priority: newCall.priority || "Normal",
      };

      // Product-registration details captured alongside the service call.
      // The API must persist these fields for them to appear in later records.
      if (newCall.serial_number.trim()) payload.serial_number = newCall.serial_number.trim();
      if (newCall.invoice_number.trim()) payload.invoice_number = newCall.invoice_number.trim();
      if (newCall.purchase_date) payload.purchase_date = newCall.purchase_date;
      if (newCall.installation_date) payload.installation_date = newCall.installation_date;
      if (newCall.warranty_start_date) payload.warranty_start_date = newCall.warranty_start_date;
      if (newCall.warranty_end_date) payload.warranty_end_date = newCall.warranty_end_date;

      if (newCall.city) {
        payload.city = newCall.city;
      }

      if (newCall.pin_code) {
        payload.pin_code = newCall.pin_code;
      }

      if (newCall.service_address) {
        payload.service_address =
          newCall.service_address;
      }

      await api.post("/service-calls", payload);

      setNewCallMessage(
        "Service call created successfully."
      );
      setCustomerSearch("");

      setNewCall({
        customer_id: "",
        product_model_id: "",
        call_type_id: "",
        symptom_id: "",
        complaint_description: "",
        state: "",
        district: "",
        serial_number: "",
        invoice_number: "",
        purchase_date: "",
        installation_date: "",
        warranty_start_date: "",
        warranty_end_date: "",
        city: "",
        pin_code: "",
        service_address: "",
        priority: "Normal",
      });

      await loadDashboard(false);

      setTimeout(() => {
        setShowNewCall(false);
        setNewCallMessage("");
      }, 800);
    } catch (err) {
      console.error("Create service call error:", err);

      setNewCallMessage(
        err?.response?.data?.message ||
          "Service call create nahi ho paya."
      );
    } finally {
      setNewCallLoading(false);
    }
  }

  function goToServiceCalls() {
    window.location.href = "/service-calls";
  }

  function goToEngineers() {
    window.location.href = "/engineers";
  }

  function goToAppointments() {
    window.location.href = "/appointments";
  }

  function goToParts() {
    window.location.href = "/parts";
  }

  const analytics = useMemo(() => {
    const normalise = (value) => String(value ?? "").trim().toLowerCase();
    const statusRows = [
      { label: "Open / Registered", key: "Open", value: 0, color: "blue" },
      { label: "Assigned", key: "Assigned", value: 0, color: "teal" },
      { label: "In Progress / Testing", key: "In Progress", value: 0, color: "orange" },
      { label: "Part Required", key: "Part Required", value: 0, color: "red" },
      { label: "Part Pending / In Transit", key: "Part Flow", value: 0, color: "purple" },
      { label: "Call Reopened", key: "Reopened", value: 0, color: "blue" },
      { label: "Call Cancelled", key: "Cancelled", value: 0, color: "slate" },
      { label: "Call Closed", key: "Closed", value: 0, color: "green" },
    ];
    const ageingRows = [
      { label: "0–2 days", value: 0 },
      { label: "3–4 days", value: 0 },
      { label: "5–7 days", value: 0 },
      { label: "8–10 days", value: 0 },
      { label: "Above 10 days", value: 0 },
    ];
    const partCounts = [
      { label: "Part Required", key: "Part Required", value: 0 },
      { label: "Part Pending", key: "Part Pending", value: 0 },
      { label: "Part In Transit / Ordered", key: "Part Transit", value: 0 },
    ];
    const now = Date.now();

    serviceCalls.forEach((call) => {
      const status = getCallStatus(call);
      const lifecycleBucket = getLifecycleBucket(call);
      const closedLike = ["Closed", "Cancelled"].includes(lifecycleBucket);
      let statusKey = lifecycleBucket;
      if (lifecycleBucket === "Part Flow") {
        statusKey = status.includes("required") || status.includes("spare") ? "Part Required" : "Part Flow";
      }
      const statusRow = statusRows.find((row) => row.key === statusKey);
      if (statusRow) statusRow.value += 1;

      const createdAt = new Date(call.registered_at || call.created_at || call.createdAt || 0).getTime();
      if (createdAt && !Number.isNaN(createdAt) && !closedLike) {
        const ageDays = Math.max(0, Math.floor((now - createdAt) / 86400000));
        const ageIndex = ageDays <= 2 ? 0 : ageDays <= 4 ? 1 : ageDays <= 7 ? 2 : ageDays <= 10 ? 3 : 4;
        ageingRows[ageIndex].value += 1;
      }

      if (matchesBucket(call, "Part Required")) partCounts[0].value += 1;
      else if (matchesBucket(call, "Part Pending")) partCounts[1].value += 1;
      else if (matchesBucket(call, "Part Transit")) partCounts[2].value += 1;
    });

    return { statusRows, ageingRows, partCounts };
  }, [serviceCalls]);
  const lifecycleValues = {
    Open: counts.open,
    Assigned: counts.assigned,
    "Appointment Scheduled": counts.appointment,
    "In Progress": counts.inProgress,
    "Part Flow": counts.partRequired + counts.partPending + counts.partTransit,
    Revisit: counts.revisit,
    Cancelled: counts.cancelled,
    Closed: counts.closed,
    Reopened: counts.reopened,
  };

  if (loading) {
    return (
      <div className="dashboard-page">
        <style>{dashboardStyles}</style>

        <div className="dashboard-loading">
          <Loader2 className="spin" size={28} />
          <span>Loading dashboard data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <style>{dashboardStyles}</style>

      <div className="dashboard-container">
        <div className="dashboard-header">
          <div>
            <h1>Dashboard</h1>

            <p>
              Monitor service operations, SLA health and
              AI-assisted workflows.
            </p>
          </div>

          <div className="dashboard-actions">
            <button
              className="refresh-button"
              onClick={() => loadDashboard(false)}
              disabled={refreshing}
            >
              <RefreshCw
                size={17}
                className={
                  refreshing ? "spin" : ""
                }
              />

              {refreshing ? "Refreshing..." : "Refresh"}
            </button>

            <button
              className="new-call-button"
              onClick={() => setShowNewCall(true)}
            >
              <FilePlus2 size={17} />
              New Service Call
            </button>
          </div>
        </div>

        {error && (
          <div className="dashboard-error">
            <AlertTriangle size={18} />

            <div>
              <strong>Backend data load error</strong>
              <div>{error}</div>
            </div>

            <button
              onClick={() => loadDashboard(true)}
            >
              Retry
            </button>
          </div>
        )}

        <section className="dashboard-card lifecycle-card">
          <div className="section-heading">
            <div>
              <h2>Service Call Lifecycle</h2>
              <p>
                Live service call status from backend
              </p>
            </div>

            <button onClick={goToServiceCalls}>
              View all
              <ArrowRight size={16} />
            </button>
          </div>

          <div className="lifecycle-grid">
            {STATUS_BUCKETS.map(
              (bucket, index) => {
                const Icon = bucket.icon;

                return (
                  <div
                    key={bucket.key}
                    className="lifecycle-wrap"
                  >
                    <button
                      className="lifecycle-item"
                      onClick={() =>
                        openBucket(bucket)
                      }
                    >
                      <div className="lifecycle-icon">
                        <Icon size={18} />
                      </div>

                      <span>{bucket.label}</span>

                      <strong>
                        {lifecycleValues[bucket.key] ||
                          0}
                      </strong>
                    </button>

                    {index <
                      STATUS_BUCKETS.length - 1 && (
                      <ArrowRight
                        className="lifecycle-arrow"
                        size={18}
                      />
                    )}
                  </div>
                );
              }
            )}
          </div>
        </section>

        <section className="analytics-section" aria-label="Service operations analytics">
          <div className="analytics-title-row">
            <div>
              <h2>Service Operations Analytics</h2>
              <p>Live summaries calculated from service-call records returned by the backend.</p>
            </div>
            <span className="analytics-live"><span /> Backend data</span>
          </div>

          <div className="analytics-grid three-analytics">
            <article className="analytics-card">
              <div className="analytics-card-heading">
                <div><h3>Call Status</h3><p>Click a status to inspect its calls</p></div>
                <Activity size={18} />
              </div>
              <div className="bar-chart">
                {analytics.statusRows.map((item) => {
                  const max = Math.max(1, ...analytics.statusRows.map((row) => row.value));
                  return (
                    <button
                      type="button"
                      className="bar-row"
                      key={item.label}
                      onClick={() => openBucket({ key: item.key, label: item.label })}
                      title={`View ${item.label}`}
                    >
                      <span className="bar-label">{item.label}</span>
                      <span className="bar-track"><span className={`bar-fill ${item.color}`} style={{ width: `${(item.value / max) * 100}%` }} /></span>
                      <strong>{item.value}</strong>
                    </button>
                  );
                })}
              </div>
            </article>

            <article className="analytics-card">
              <div className="analytics-card-heading">
                <div><h3>Ticket Ageing</h3><p>Active calls grouped by age</p></div>
                <Clock3 size={18} />
              </div>
              <div className="ageing-chart">
                {analytics.ageingRows.map((item) => {
                  const max = Math.max(1, ...analytics.ageingRows.map((row) => row.value));
                  return (
                    <div className="age-column" key={item.label} title={`${item.label}: ${item.value} calls`}>
                      <strong>{item.value}</strong>
                      <div className="age-track"><span style={{ height: `${item.value ? Math.max(5, (item.value / max) * 100) : 0}%` }} /></div>
                      <span>{item.label}</span>
                    </div>
                  );
                })}
              </div>
              <p className="chart-note">Age is calculated from registered/created date. Closed and cancelled calls are excluded.</p>
            </article>

            <article className="analytics-card">
              <div className="analytics-card-heading">
                <div><h3>Part Status</h3><p>Calls currently in the part workflow</p></div>
                <Package size={18} />
              </div>
              <div className="bar-chart">
                {analytics.partCounts.map((item, index) => {
                  const max = Math.max(1, ...analytics.partCounts.map((row) => row.value));
                  return (
                    <button
                      type="button"
                      className="bar-row"
                      key={item.label}
                      onClick={() => openBucket({ key: item.key, label: item.label })}
                      title={`View ${item.label} calls`}
                    >
                      <span className="bar-label">{item.label}</span>
                      <span className="bar-track"><span className={`bar-fill ${index === 0 ? "red" : index === 1 ? "orange" : "purple"}`} style={{ width: `${(item.value / max) * 100}%` }} /></span>
                      <strong>{item.value}</strong>
                    </button>
                  );
                })}
              </div>
            </article>
          </div>
        </section>
        <div className="quick-actions">
          <button onClick={goToEngineers}>
            <Users size={18} />
            Engineers
          </button>

          <button onClick={goToAppointments}>
            <CalendarDays size={18} />
            Appointments
          </button>

          <button onClick={goToParts}>
            <Wrench size={18} />
            Parts
          </button>
        </div>
      </div>

      {selectedBucket && (
        <div
          className="modal-backdrop"
          onMouseDown={closePanels}
        >
          <div
            className="modal large-modal"
            onMouseDown={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-header">
              <div>
                <h2>{selectedBucket.label}</h2>

                <p>
                  {serviceCalls.filter((call) => matchesBucket(call, selectedBucket.key)).length} matching call(s) · Select a call or use Details / Assign Engineer.
                </p>
              </div>

              <button
                className="icon-button"
                onClick={closePanels}
              >
                <X size={20} />
              </button>
            </div>

            <div className="modal-body">
              {(() => {
                let filteredCalls = [];

                filteredCalls = serviceCalls.filter((call) => matchesBucket(call, selectedBucket.key));

                if (
                  filteredCalls.length === 0
                ) {
                  return (
                    <div className="empty-state big">
                      No calls found in this section.
                    </div>
                  );
                }

                return (
                  <div className="modal-call-list">
                    {filteredCalls.map(
                      (call) => (
                        <div
                          className="modal-call"
                          key={call.id}
                          role="button"
                          tabIndex={0}
                          onClick={() => openCall(call)}
                          onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); openCall(call); } }}
                          title="Open service call details"
                        >
                          <div>
                            <strong>
                              {call.call_id || `CALL-${call.id}`}
                            </strong>

                            <span>
                              {
                                call.complaint_id
                              }
                            </span>
                          </div>

                          <div>
                            <strong>
                              {getCustomerName(
                                call
                              )}
                            </strong>

                            <span>
                              {getProductName(
                                call
                              )}
                            </span>
                          </div>

                          <div>
                            <span
                              className={statusClass(
                                call.status
                              )}
                            >
                              {call.status}
                            </span>
                          </div>

                          <div className="modal-actions">
                            <button
                              className="small-button"
                              type="button"
                              onClick={(event) => { event.stopPropagation(); openCall(call); }}
                            >
                              Details
                            </button>

                            {!call.engineer_id &&
                              !assignmentMap[
                                call.id
                              ]?.engineer_id && (
                                <button
                                  className="small-button primary"
                                  type="button"
                                  onClick={(event) => { event.stopPropagation(); startAssign(call); }}
                                >
                                  Assign Engineer
                                </button>
                              )}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}

      {selectedCall && (
        <div
          className="modal-backdrop"
          onMouseDown={closePanels}
        >
          <div
            className="modal"
            onMouseDown={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-header">
              <div>
                <h2>
                  {selectedCall.call_id || `CALL-${selectedCall.id}`}
                </h2>

                <p>
                  {selectedCall.complaint_id ||
                    "Service Call"}
                </p>
              </div>

              <button
                className="icon-button"
                onClick={closePanels}
              >
                <X size={20} />
              </button>
            </div>

            <div className="detail-grid">
              <div>
                <span>Customer</span>
                <strong>
                  {getCustomerName(
                    selectedCall
                  )}
                </strong>
              </div>

              <div>
                <span>Product</span>
                <strong>
                  {getProductName(
                    selectedCall
                  )}
                </strong>
              </div>

              <div className="status-edit-field">
                <span>Status</span>
                <select value={statusDraft} onChange={(event) => setStatusDraft(event.target.value)}>
                  {["Open", "Registered", "Assigned", "Appointment Scheduled", "In Progress", "Testing", "Part Required", "Part Pending", "Part In Transit", "Reopened", "Cancelled", "Closed"].map((status) => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                  {statusDraft && !["Open", "Registered", "Assigned", "Appointment Scheduled", "In Progress", "Testing", "Part Required", "Part Pending", "Part In Transit", "Reopened", "Cancelled", "Closed"].includes(statusDraft) && <option value={statusDraft}>{statusDraft}</option>}
                </select>
              </div>

              <div>
                <span>Priority</span>
                <strong>
                  {selectedCall.priority || "-"}
                </strong>
              </div>

              <div>
                <span>Engineer</span>
                <strong>
                  {getEngineer(selectedCall)}
                </strong>
              </div>

              <div>
                <span>Registered</span>
                <strong>
                  {formatDate(
                    selectedCall.registered_at
                  )}
                </strong>
              </div>

              <div>
                <span>SLA Due</span>
                <strong>
                  {formatDate(
                    selectedCall.sla_due_at
                  )}
                </strong>
              </div>

              <div>
                <span>Serial Number</span>
                <strong>
                  {selectedCall.serial_number ||
                    "-"}
                </strong>
              </div>
            </div>

            <div className="complaint-box">
              <span>
                Complaint Description
              </span>

              <p>
                {selectedCall.complaint_description ||
                  "No complaint description available."}
              </p>
            </div>

            <button className="primary full-button" type="button" onClick={updateCallStatus} disabled={statusSaving}>
              {statusSaving ? "Updating status..." : "Update Call Status"}
            </button>

            {!selectedCall.engineer_id &&
              !assignmentMap[
                selectedCall.id
              ]?.engineer_id && (
                <button
                  className="primary full-button"
                  onClick={() =>
                    startAssign(selectedCall)
                  }
                >
                  <UserRound size={17} />
                  Assign Engineer
                </button>
              )}
          </div>
        </div>
      )}

      {assigningCall && (
        <div
          className="modal-backdrop"
          onMouseDown={() =>
            setAssigningCall(null)
          }
        >
          <div
            className="modal"
            onMouseDown={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-header">
              <div>
                <h2>Assign Engineer</h2>

                <p>
                  {assigningCall.call_id}
                </p>
              </div>

              <button
                className="icon-button"
                onClick={() =>
                  setAssigningCall(null)
                }
              >
                <X size={20} />
              </button>
            </div>

            <div className="form-group">
              <label>Select Engineer</label>

              <select
                value={selectedEngineer}
                onChange={(event) =>
                  setSelectedEngineer(
                    event.target.value
                  )
                }
              >
                <option value="">
                  Select engineer
                </option>

                {engineers.map((engineer) => (
                  <option
                    key={engineer.id}
                    value={engineer.id}
                  >
                    {engineer.engineer_name ||
                      engineer.name ||
                      engineer.engineer_code ||
                      `Engineer #${engineer.id}`}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Remarks</label>

              <textarea
                value={assignmentRemarks}
                onChange={(event) =>
                  setAssignmentRemarks(
                    event.target.value
                  )
                }
                placeholder="Enter assignment remarks"
              />
            </div>

            <div className="modal-footer">
              <button
                className="secondary-button"
                onClick={() =>
                  setAssigningCall(null)
                }
              >
                Cancel
              </button>

              <button
                className="primary"
                disabled={
                  !selectedEngineer ||
                  refreshing
                }
                onClick={assignEngineer}
              >
                {refreshing ? (
                  <>
                    <Loader2
                      size={16}
                      className="spin"
                    />
                    Assigning...
                  </>
                ) : (
                  <>
                    <UserRound size={16} />
                    Assign Engineer
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {showNewCall && (
        <div
          className="modal-backdrop"
          onMouseDown={() =>
            setShowNewCall(false)
          }
        >
          <form
            className="modal large-modal"
            onSubmit={createServiceCall}
            onMouseDown={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-header">
              <div>
                <h2>New Service Call</h2>

                <p>
                  Create a real service call in
                  backend
                </p>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={() =>
                  setShowNewCall(false)
                }
              >
                <X size={20} />
              </button>
            </div>

            {newCallMessage && (
              <div className="form-message">
                {newCallMessage}
              </div>
            )}

            <div className="form-grid">
              <div className="form-group">
                <label>Find Customer (name, mobile, email or code)</label>
                <input
                  type="search"
                  value={customerSearch}
                  onChange={(event) => setCustomerSearch(event.target.value)}
                  placeholder="Search customer..."
                  autoComplete="off"
                />
                <select
                  required
                  value={newCall.customer_id}
                  onChange={(event) =>
                    setNewCall({ ...newCall, customer_id: event.target.value })
                  }
                >
                  <option value="">Select customer</option>
                  {filteredCustomers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.customer_name || customer.name || `Customer #${customer.id}`}
                      {" · "}
                      {customer.mobile || customer.mobile_number || customer.phone ||
                        customer.phone_number || customer.customer_code || `ID ${customer.id}`}
                    </option>
                  ))}
                </select>
                {selectedCustomer && (
                  <div className="selected-customer-preview">
                    <strong>{selectedCustomer.customer_name || selectedCustomer.name || `Customer #${selectedCustomer.id}`}</strong>
                    <span>
                      {selectedCustomer.mobile || selectedCustomer.mobile_number ||
                        selectedCustomer.phone || selectedCustomer.phone_number || "Phone not available"}
                    </span>
                    {selectedCustomer.email && <span>{selectedCustomer.email}</span>}
                  </div>
                )}
                {customers.length === 0 && (
                  <small className="field-hint">
                    Customer list could not be loaded. Check the /customers API before creating a call.
                  </small>
                )}
              </div>

              <div className="form-group">
                <label>Product Model</label>

                <select
                  required
                  value={
                    newCall.product_model_id
                  }
                  onChange={(event) =>
                    setNewCall({
                      ...newCall,
                      product_model_id:
                        event.target.value,
                    })
                  }
                >
                  <option value="">
                    Select product model
                  </option>

                  {productModels.map((product) => (
                    <option
                      key={product.id}
                      value={product.id}
                    >
                      {product.product_model_name ||
                        product.model_name ||
                        product.name ||
                        `Model #${product.id}`}
                    </option>
                  ))}
                </select>
                {selectedProduct && (
                  <div className="selected-customer-preview product-preview">
                    <strong>Selected Product Details</strong>
                    <span>Brand: {selectedProduct.brand_name || selectedProduct.brand?.brand_name || selectedProduct.brand?.name || selectedProduct.brand || "-"}</span>
                    <span>Category: {selectedProduct.product_category_name || selectedProduct.category_name || selectedProduct.category?.name || selectedProduct.product_category?.name || "-"}</span>
                    <span>Product Type: {selectedProduct.product_type_name || selectedProduct.product_type?.product_type_name || selectedProduct.product_type?.name || selectedProduct.type_name || "-"}</span>
                    <span>Product Family: {selectedProduct.product_family_name || selectedProduct.product_family?.name || selectedProduct.family_name || "-"}</span>
                    <span>Model: {selectedProduct.model_name || selectedProduct.product_model_name || selectedProduct.name || "-"}</span>
                    <span>Model Code / SKU: {selectedProduct.model_number || selectedProduct.model_code || selectedProduct.sku || "-"}</span>
                    <span>Variant: {selectedProduct.variant_name || selectedProduct.variant?.name || selectedProduct.variant || "-"}</span>
                    <span>Warranty Period: {selectedProduct.warranty_period || selectedProduct.warranty_months ? `${selectedProduct.warranty_period || selectedProduct.warranty_months} ${selectedProduct.warranty_unit || "months"}` : (selectedProduct.warranty_applicable ? "Applicable — enter warranty dates below" : "Not provided by Product Master")}</span>
                  </div>
                )}
                {productModels.length === 0 && (
                  <small className="field-hint">Product models could not be loaded. Check the /product-models API and Product Master records.</small>
                )}
              </div>

              <div className="form-group">
                <label>Call Type</label>

                <select
                  required
                  value={newCall.call_type_id}
                  onChange={(event) =>
                    setNewCall({
                      ...newCall,
                      call_type_id:
                        event.target.value,
                    })
                  }
                >
                  <option value="">
                    Select call type
                  </option>

                  {callTypes.map((item) => (
                    <option
                      key={item.id}
                      value={item.id}
                    >
                      {item.call_type_name ||
                        item.name ||
                        `Call Type #${item.id}`}
                    </option>
                  ))}
                </select>
                {selectedCallType && (
                  <small className="field-hint">
                    Selected call type: {selectedCallType.call_type_name || selectedCallType.name || "Configured call type"}.
                    Closure and visit requirements should follow the configured Call Type Master.
                  </small>
                )}
              </div>

              <div className="form-group">
                <label>Symptom</label>

                <select
                  required
                  value={newCall.symptom_id}
                  onChange={(event) =>
                    setNewCall({
                      ...newCall,
                      symptom_id:
                        event.target.value,
                    })
                  }
                >
                  <option value="">
                    Select symptom
                  </option>

                  {symptoms.map((item) => (
                    <option
                      key={item.id}
                      value={item.id}
                    >
                      {item.symptom_name ||
                        item.name ||
                        item.description ||
                        `Symptom #${item.id}`}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>State</label>

                <input
                  required
                  value={newCall.state}
                  onChange={(event) =>
                    setNewCall({
                      ...newCall,
                      state: event.target.value,
                    })
                  }
                  placeholder="State"
                />
              </div>

              <div className="form-group">
                <label>District</label>

                <input
                  required
                  value={newCall.district}
                  onChange={(event) =>
                    setNewCall({
                      ...newCall,
                      district:
                        event.target.value,
                    })
                  }
                  placeholder="District"
                />
              </div>

              <div className="form-group">
                <label>Serial Number</label>

                <input
                  required
                  value={newCall.serial_number}
                  onChange={(event) =>
                    setNewCall({
                      ...newCall,
                      serial_number: event.target.value,
                    })
                  }
                  placeholder="Enter product serial number"
                />
                <small className="field-hint">Use the serial number printed on the product label. Duplicate validation depends on backend support.</small>
              </div>

              <div className="form-group">
                <label>Date of Purchase (DOP)</label>
                <input
                  type="date"
                  value={newCall.purchase_date}
                  onChange={(event) => setNewCall({ ...newCall, purchase_date: event.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Invoice Number</label>
                <input
                  value={newCall.invoice_number}
                  onChange={(event) => setNewCall({ ...newCall, invoice_number: event.target.value })}
                  placeholder="Enter invoice number"
                />
              </div>

              <div className="form-group">
                <label>Installation Date</label>
                <input
                  type="date"
                  value={newCall.installation_date}
                  onChange={(event) => setNewCall({ ...newCall, installation_date: event.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Warranty Start Date</label>
                <input
                  type="date"
                  value={newCall.warranty_start_date}
                  onChange={(event) => setNewCall({ ...newCall, warranty_start_date: event.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Warranty End Date</label>
                <input
                  type="date"
                  value={newCall.warranty_end_date}
                  onChange={(event) => setNewCall({ ...newCall, warranty_end_date: event.target.value })}
                />
              </div>

              <div className="form-group">
                <label>PIN Code</label>

                <input
                  value={newCall.pin_code}
                  onChange={(event) =>
                    setNewCall({
                      ...newCall,
                      pin_code:
                        event.target.value,
                    })
                  }
                  placeholder="PIN code"
                />
              </div>

              <div className="form-group">
                <label>City / Town</label>
                <input
                  value={newCall.city}
                  onChange={(event) =>
                    setNewCall({ ...newCall, city: event.target.value })
                  }
                  placeholder="Enter city or town"
                />
              </div>

              <div className="form-group">
                <label>Priority</label>
                <select
                  required
                  value={newCall.priority}
                  onChange={(event) =>
                    setNewCall({ ...newCall, priority: event.target.value })
                  }
                >
                  <option value="Normal">Normal</option>
                  <option value="High">High</option>
                  <option value="Urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Complete Service Address</label>
              <textarea
                rows={2}
                value={newCall.service_address}
                onChange={(event) =>
                  setNewCall({ ...newCall, service_address: event.target.value })
                }
                placeholder="House / building, street, landmark, area"
              />
            </div>

            <div className="form-group">
              <label>Complaint Description</label>

              <textarea
                required
                value={
                  newCall.complaint_description
                }
                onChange={(event) =>
                  setNewCall({
                    ...newCall,
                    complaint_description:
                      event.target.value,
                  })
                }
                placeholder="Describe customer complaint"
              />
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  setShowNewCall(false)
                }
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary"
                disabled={newCallLoading}
              >
                {newCallLoading ? (
                  <>
                    <Loader2
                      size={16}
                      className="spin"
                    />
                    Creating...
                  </>
                ) : (
                  <>
                    <FilePlus2 size={16} />
                    Create Service Call
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

const dashboardStyles = `
.dashboard-page {
  min-height: calc(100vh - 72px);
  background: #f6f9fd;
  padding: 28px 32px 40px;
  color: #172033;
  box-sizing: border-box;
}

.dashboard-container {
  width: 100%;
  max-width: 1500px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 25px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 29px;
  font-weight: 750;
  letter-spacing: -0.5px;
}

.dashboard-header p {
  margin: 7px 0 0;
  color: #748096;
  font-size: 14px;
}

.dashboard-actions {
  display: flex;
  gap: 10px;
}

.refresh-button,
.new-call-button,
.dashboard-actions button {
  border: 1px solid #e1e7f0;
  background: white;
  color: #25314a;
  height: 40px;
  padding: 0 15px;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 600;
}

.new-call-button {
  background: #1557f5;
  color: white;
  border-color: #1557f5;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.kpi-card {
  min-height: 116px;
  border: 1px solid #e5eaf2;
  background: white;
  border-radius: 15px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  text-align: left;
  cursor: pointer;
  color: #172033;
  transition: 0.18s ease;
}

.kpi-card:hover,
.lifecycle-item:hover,
.call-row:hover,
.attention-row:hover {
  transform: translateY(-1px);
  border-color: #cdd8eb;
  box-shadow: 0 8px 24px rgba(31, 55, 95, 0.07);
}

.kpi-card > svg {
  margin-left: auto;
  color: #9aa7ba;
}

.kpi-icon {
  width: 45px;
  height: 45px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.kpi-icon.blue {
  background: #edf4ff;
  color: #1557f5;
}

.kpi-icon.orange {
  background: #fff5e9;
  color: #e58a20;
}

.kpi-icon.purple {
  background: #f3efff;
  color: #7b55d9;
}

.kpi-icon.red {
  background: #fff0f0;
  color: #df4e55;
}

.kpi-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.kpi-content span {
  color: #748096;
  font-size: 13px;
  font-weight: 600;
}

.kpi-content strong {
  font-size: 26px;
  line-height: 1;
}

.dashboard-card {
  background: white;
  border: 1px solid #e5eaf2;
  border-radius: 16px;
  overflow: hidden;
}

.lifecycle-card {
  padding: 22px;
  margin-bottom: 18px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 19px;
}

.section-heading h2 {
  margin: 0;
  font-size: 17px;
  font-weight: 720;
}

.section-heading p {
  margin: 5px 0 0;
  color: #8994a7;
  font-size: 12px;
}

.section-heading > button {
  border: 0;
  background: transparent;
  color: #1557f5;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 650;
}

.lifecycle-grid {
  display: grid;
  grid-template-columns: repeat(9, minmax(0, 1fr));
  align-items: center;
}

.lifecycle-wrap {
  min-width: 0;
  position: relative;
  display: flex;
  align-items: center;
}

.lifecycle-item {
  width: 100%;
  min-height: 112px;
  background: #f9fbfe;
  border: 1px solid #e8edf4;
  border-radius: 12px;
  padding: 13px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 7px;
  cursor: pointer;
  color: #263249;
}

.lifecycle-icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: #edf4ff;
  color: #1557f5;
  display: grid;
  place-items: center;
}

.lifecycle-item span {
  color: #69768d;
  font-size: 11px;
  text-align: center;
}

.lifecycle-item strong {
  font-size: 20px;
}

.lifecycle-arrow {
  position: absolute;
  right: -9px;
  z-index: 2;
  color: #b2bdcc;
  background: white;
  border-radius: 50%;
}

.bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: 18px;
}

.bottom-grid .dashboard-card {
  padding: 22px;
}

.call-list,
.attention-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.call-row {
  width: 100%;
  min-height: 66px;
  border: 1px solid transparent;
  background: #f9fbfe;
  border-radius: 10px;
  display: grid;
  grid-template-columns: 1.15fr 1.1fr 1fr auto;
  align-items: center;
  gap: 15px;
  padding: 10px 13px;
  text-align: left;
  cursor: pointer;
  color: #263249;
}

.call-main {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.call-main strong {
  font-size: 13px;
}

.call-main span,
.call-product,
.call-engineer {
  color: #7a8699;
  font-size: 12px;
}

.call-product,
.call-engineer {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  white-space: nowrap;
  padding: 5px 9px;
  border-radius: 20px;
  background: #eef2f7;
  color: #5c687c;
  font-size: 11px;
  font-weight: 700;
}

.status.open {
  background: #edf4ff;
  color: #1557f5;
}

.status.progress {
  background: #fff4e7;
  color: #d77b12;
}

.status.closed {
  background: #ebf8f0;
  color: #218653;
}

.status.validated {
  background: #f0edff;
  color: #7355c7;
}

.status.assigned {
  background: #eaf8f8;
  color: #18868a;
}

.status.appointment {
  background: #eef0ff;
  color: #5e63cb;
}

.status.part {
  background: #fff0f0;
  color: #c94f55;
}

.status.confirmation {
  background: #eaf8f0;
  color: #238653;
}

.attention-row {
  width: 100%;
  min-height: 62px;
  border: 1px solid transparent;
  background: #f9fbfe;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 13px;
  text-align: left;
  cursor: pointer;
  color: #263249;
}

.attention-row > svg {
  margin-left: auto;
  color: #a0acbd;
}

.attention-icon {
  width: 35px;
  height: 35px;
  border-radius: 9px;
  background: #fff4e7;
  color: #e38b20;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.attention-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.attention-content strong {
  font-size: 13px;
}

.attention-content span {
  color: #7a8699;
  font-size: 12px;
}

.quick-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
}

.quick-actions button {
  border: 1px solid #e3e8f0;
  background: white;
  border-radius: 9px;
  height: 38px;
  padding: 0 13px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #536078;
  cursor: pointer;
  font-size: 12px;
  font-weight: 650;
}

.dashboard-error {
  background: #fff5f5;
  border: 1px solid #f2cccc;
  color: #a33b3b;
  padding: 13px 15px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 17px;
}

.dashboard-error div {
  flex: 1;
  font-size: 12px;
}

.dashboard-error button {
  border: 0;
  background: white;
  color: #a33b3b;
  border-radius: 7px;
  padding: 7px 12px;
  cursor: pointer;
  font-weight: 700;
}

.dashboard-loading {
  min-height: 65vh;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #647188;
  font-size: 14px;
}

.empty-state {
  padding: 35px 10px;
  text-align: center;
  color: #8a96a8;
  font-size: 13px;
}

.empty-state.big {
  padding: 70px 10px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(18, 29, 48, 0.42);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 25px;
}

.modal {
  width: min(600px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  background: white;
  border-radius: 16px;
  box-shadow: 0 25px 70px rgba(18, 29, 48, 0.2);
}

.large-modal {
  width: min(1000px, 100%);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 21px 23px;
  border-bottom: 1px solid #edf0f5;
}

.modal-header h2 {
  margin: 0;
  font-size: 19px;
}

.modal-header p {
  margin: 5px 0 0;
  color: #8792a5;
  font-size: 12px;
}

.icon-button {
  width: 34px;
  height: 34px;
  border: 1px solid #e4e9f0;
  background: white;
  border-radius: 8px;
  display: grid;
  place-items: center;
  cursor: pointer;
  color: #68758a;
}

.modal-body {
  padding: 18px 22px 22px;
}

.modal-call-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.modal-call {
  border: 1px solid #e7ebf2;
  border-radius: 10px;
  padding: 13px;
  display: grid;
  grid-template-columns: 1.1fr 1.1fr 0.7fr auto;
  gap: 14px;
  align-items: center;
}

.modal-call > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.modal-call span {
  color: #818da0;
  font-size: 11px;
}

.modal-actions {
  flex-direction: row !important;
  justify-content: flex-end;
}

.small-button {
  border: 1px solid #e0e6ef;
  background: white;
  color: #536078;
  border-radius: 7px;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 650;
  white-space: nowrap;
}

.small-button.primary {
  background: #1557f5;
  color: white;
  border-color: #1557f5;
}

.detail-grid {
  padding: 20px 23px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.detail-grid > div {
  background: #f8fafd;
  border: 1px solid #edf0f5;
  border-radius: 9px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-grid span,
.complaint-box > span {
  color: #8a96a8;
  font-size: 11px;
}

.detail-grid strong {
  color: #263249;
  font-size: 13px;
}

.complaint-box {
  margin: 0 23px 20px;
  padding: 14px;
  border: 1px solid #e7ebf2;
  background: #f9fbfe;
  border-radius: 10px;
}

.complaint-box p {
  margin: 7px 0 0;
  color: #536078;
  font-size: 13px;
  line-height: 1.5;
}

.form-grid {
  padding: 20px 23px 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.form-group {
  padding: 0 23px;
  margin-top: 16px;
}

.form-grid .form-group {
  padding: 0;
  margin-top: 0;
}

.form-group label {
  display: block;
  color: #59667d;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 6px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #dfe5ee;
  border-radius: 8px;
  padding: 10px 11px;
  background: white;
  color: #27334a;
  outline: none;
  font-family: inherit;
  font-size: 13px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #1557f5;
  box-shadow: 0 0 0 3px rgba(21, 87, 245, 0.08);
}

.form-group textarea {
  min-height: 90px;
  resize: vertical;
}

.selected-customer-preview {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
  padding: 10px 11px;
  border: 1px solid #dcefe4;
  border-radius: 8px;
  background: #f4fbf6;
  color: #236b43;
  font-size: 12px;
}
.selected-customer-preview span,
.field-hint {
  color: #78869a;
  font-size: 11px;
  line-height: 1.45;
}
.field-hint {
  display: block;
  margin-top: 6px;
}
.product-preview {
  background: #f5f8ff;
  border-color: #dbe5ff;
  color: #28477e;
}
.product-preview strong {
  font-size: 12px;
  margin-bottom: 2px;
}

.form-message {
  margin: 16px 23px 0;
  padding: 10px 12px;
  background: #eef8f1;
  color: #237b48;
  border-radius: 8px;
  font-size: 12px;
}

.modal-footer {
  padding: 20px 23px;
  margin-top: 20px;
  border-top: 1px solid #edf0f5;
  display: flex;
  justify-content: flex-end;
  gap: 9px;
}

.primary,
.secondary-button,
.full-button {
  border: 0;
  border-radius: 8px;
  min-height: 38px;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.primary {
  background: #1557f5;
  color: white;
}

.primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.secondary-button {
  background: #f2f5f9;
  color: #59667d;
}

.full-button {
  width: calc(100% - 46px);
  margin: 0 23px 23px;
  background: #1557f5;
  color: white;
}

.spin {
  animation: dashboardSpin 0.8s linear infinite;
}

@keyframes dashboardSpin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}



.analytics-section {
  margin: 0 0 20px;
  padding: 22px;
  border: 1px solid #e5eaf2;
  border-radius: 16px;
  background: #f9fbff;
}
.analytics-title-row { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:16px; }
.analytics-title-row h2 { margin:0; font-size:19px; font-weight:750; color:#172033; }
.analytics-title-row p { margin:6px 0 0; font-size:12px; color:#8994a7; }
.analytics-live { display:inline-flex; align-items:center; gap:7px; padding:7px 10px; border:1px solid #dcefe4; border-radius:20px; background:#f0faf4; color:#238653; font-size:11px; font-weight:700; white-space:nowrap; }
.analytics-live span { width:7px; height:7px; border-radius:50%; background:#2ba66a; }
.analytics-kpis { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin-bottom:14px; }
.analytics-mini-card { padding:16px 18px; background:#fff; border:1px solid #e5eaf2; border-radius:12px; display:flex; flex-direction:column; gap:6px; }
.analytics-mini-card span { font-size:12px; color:#748096; font-weight:650; }
.analytics-mini-card strong { font-size:27px; line-height:1.1; color:#172033; }
.analytics-mini-card small { font-size:11px; color:#929db0; }
.analytics-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }\n.three-analytics .analytics-card { min-height: 280px; }
.analytics-card { min-width:0; padding:18px; background:#fff; border:1px solid #e5eaf2; border-radius:13px; }
.analytics-card-heading { display:flex; align-items:flex-start; justify-content:space-between; gap:10px; margin-bottom:18px; }
.analytics-card-heading h3 { margin:0; font-size:15px; font-weight:750; color:#172033; }
.analytics-card-heading p { margin:5px 0 0; color:#8994a7; font-size:11px; line-height:1.4; }
.analytics-card-heading > svg { flex-shrink:0; color:#1557f5; }
.bar-chart { display:flex; flex-direction:column; gap:14px; }
.bar-row { width:100%; display:grid; grid-template-columns:minmax(88px,1fr) minmax(35px,1.25fr) 25px; gap:9px; align-items:center; border:0; padding:0; background:transparent; text-align:left; color:#536078; font:inherit; }
button.bar-row { cursor:pointer; }
.bar-label { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:11px; }
.bar-row > strong { text-align:right; font-size:12px; color:#263249; }
.bar-track { height:9px; border-radius:10px; overflow:hidden; background:#eef2f8; display:block; }
.bar-fill { display:block; height:100%; min-width:0; border-radius:10px; transition:width .2s ease; }
.bar-fill.blue { background:#2563eb; }
.bar-fill.teal { background:#0d9488; }
.bar-fill.purple { background:#8b5cf6; }
.bar-fill.orange { background:#e59b26; }
.bar-fill.red { background:#e05260; }
.bar-fill.green { background:#27a36a; }
.bar-fill.slate { background:#64748b; }
.ageing-chart { height:190px; display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); align-items:end; gap:9px; padding-top:4px; }
.age-column { min-width:0; height:100%; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; gap:8px; }
.age-column strong { color:#263249; font-size:12px; }
.age-track { height:125px; width:100%; max-width:34px; display:flex; align-items:flex-end; background:#f0f3f8; border-radius:7px 7px 3px 3px; overflow:hidden; }
.age-track span { display:block; width:100%; border-radius:7px 7px 3px 3px; background:#c69b13; min-height:0; }
.age-column > span { min-height:28px; color:#748096; font-size:10px; text-align:center; line-height:1.3; }
.escalation-summary { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.escalation-number { min-height:115px; border:1px solid #edf0f5; background:#fafbfe; border-radius:11px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:9px; }
.escalation-number span { color:#748096; font-size:11px; text-align:center; }
.escalation-number strong { font-size:29px; color:#172033; }
.chart-note { margin:14px 0 0; color:#8994a7; font-size:10px; line-height:1.5; }

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .lifecycle-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .lifecycle-arrow {
    display: none;
  }
}

@media (max-width: 1100px) {
  .analytics-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media (max-width: 900px) {
  .analytics-grid { grid-template-columns:1fr; }
  .analytics-kpis { grid-template-columns:1fr; }
  .bottom-grid {
    grid-template-columns: 1fr;
  }

  .call-row {
    grid-template-columns: 1fr 1fr;
  }

  .modal-call {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 650px) {
  .analytics-section { padding:15px; }
  .analytics-title-row { align-items:flex-start; flex-direction:column; }
  .dashboard-page {
    padding: 18px;
  }

  .dashboard-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .lifecycle-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .form-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .call-row {
    grid-template-columns: 1fr;
  }

  .modal-call {
    grid-template-columns: 1fr;
  }
}

/* Layout and modal usability fixes */
.dashboard-page .lifecycle-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; align-items: stretch; }
.dashboard-page .lifecycle-wrap { min-width: 0; position: relative; }
.dashboard-page .lifecycle-item { width: 100%; min-height: 150px; height: 100%; }
.dashboard-page .lifecycle-arrow { position: absolute; right: -14px; top: 50%; transform: translateY(-50%); z-index: 2; background: #fff; border-radius: 50%; }
.dashboard-page .modal.large-modal { max-height: calc(100dvh - 32px); overflow-x: hidden; overflow-y: auto; display: block; overscroll-behavior: contain; }
.dashboard-page .modal.large-modal form, .dashboard-page form.modal.large-modal { min-height: 0; }
.dashboard-page .modal.large-modal .form-grid { min-width: 0; }
.dashboard-page .modal.large-modal .modal-footer { position: sticky; bottom: 0; z-index: 3; background: #fff; padding-bottom: max(18px, env(safe-area-inset-bottom)); border-top: 1px solid #edf0f5; }
.dashboard-page .modal-call-list { display: grid; gap: 10px; }
.dashboard-page .modal-call { cursor: pointer; }
.dashboard-page .status-edit-field { display: flex; flex-direction: column; gap: 8px; }
.dashboard-page .status-edit-field select { width: 100%; border: 1px solid #dbe3ef; border-radius: 9px; padding: 10px 12px; color: #172b4d; background: #fff; }
@media (max-width: 1050px) { .dashboard-page .lifecycle-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } .dashboard-page .lifecycle-arrow { display: none; } }
@media (max-width: 640px) { .dashboard-page .lifecycle-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
/* New Service Call: keep the complete form scrollable inside the viewport. */
.dashboard-page .modal-backdrop { align-items: flex-start; overflow-y: auto; }
.dashboard-page .modal-backdrop > form.modal.large-modal { margin: auto; max-height: calc(100dvh - 32px); overflow-y: auto; overflow-x: hidden; }
.dashboard-page .modal.large-modal .form-group { min-width: 0; }
`;
