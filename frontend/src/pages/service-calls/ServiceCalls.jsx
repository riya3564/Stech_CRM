
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity, AlertCircle, CalendarDays, CheckCircle2, Clock3,
  Eye, LoaderCircle, Package, RefreshCw, Search, UserRound, X,
} from "lucide-react";
import api from "../../services/api";

const BUCKETS = [
  { label: "All Calls", status: "All", icon: Activity },
  { label: "Open Calls", status: "Open", icon: Clock3 },
  { label: "Not Assigned", status: "Not Assigned", icon: UserRound },
  { label: "Assigned Calls", status: "Assigned", icon: CheckCircle2 },
  { label: "Appointment", status: "Appointment Scheduled", icon: CalendarDays },
  { label: "In Progress / WIP", status: "In Progress", icon: Activity },
  { label: "Part Required", status: "Part Required", icon: Package },
  { label: "Part Pending", status: "Part Pending", icon: Package },
  { label: "Part In Transit", status: "Part In Transit", icon: Package },
  { label: "Part Received", status: "Part Received", icon: Package },
  { label: "Part Issued", status: "Part Issued", icon: Package },
  { label: "Repair In Progress", status: "Repair In Progress", icon: Activity },
  { label: "Repair Completed", status: "Repair Completed", icon: CheckCircle2 },
  { label: "Testing", status: "Testing", icon: Activity },
  { label: "Customer Confirmation", status: "Customer Confirmation", icon: CheckCircle2 },
  { label: "DOA Approval", status: "DOA Approval", icon: AlertCircle },
  { label: "Request for Cancellation", status: "Request for Cancellation", icon: AlertCircle },
  { label: "Cancelled", status: "Cancelled", icon: AlertCircle },
  { label: "Closed", status: "Closed", icon: CheckCircle2 },
  { label: "Reopen", status: "Reopen", icon: RefreshCw },
];

const STATUS_OPTIONS = [
  "Open", "Not Assigned", "Assigned", "Appointment Scheduled",
  "In Progress", "Part Required", "Part Pending", "Part In Transit",
  "Part Received", "Part Issued", "Repair In Progress",
  "Repair Completed", "Testing", "Customer Confirmation",
  "DOA Approval", "Request for Cancellation", "Cancelled", "Closed",
  "Reopen",
];

const initialAppointment = {
  asc_id: "",
  engineer_id: "",
  appointment_date: "",
  appointment_time: "",
  appointment_point: "",
  remarks: "",
};

const initialCompletion = {
  symptom: "",
  faultCode: "",
  diagnosis: "",
  repairCode: "",
  repairDetails: "",
  testingResult: "",
  engineerRemarks: "",
  happyCode: "",
};

const initialWorkflowForm = {
  serial_number: "",
  invoice_number: "",
  reason: "",
  part_code: "",
  part_name: "",
  part_quantity: "1",
  diagnosis: "",
  repair_details: "",
  testing_result: "",
  customer_confirmation: "",
  cancellation_reason: "",
  reopen_reason: "",
  remarks: "",
};

const WORKFLOW_FIELDS = {
  Open: ["serial_number", "invoice_number", "remarks"],
  "Not Assigned": ["serial_number", "invoice_number", "remarks"],
  Assigned: ["serial_number", "invoice_number", "remarks"],
  "Appointment Scheduled": [
    "serial_number", "invoice_number", "remarks",
  ],
  "In Progress": ["serial_number", "invoice_number", "remarks"],
  "Part Required": [
    "serial_number", "invoice_number", "part_code",
    "part_name", "part_quantity", "reason",
  ],
  "Part Pending": [
    "serial_number", "invoice_number", "part_code",
    "part_name", "part_quantity", "reason",
  ],
  "Part In Transit": [
    "serial_number", "invoice_number", "part_code",
    "part_name", "part_quantity", "remarks",
  ],
  "Part Received": [
    "serial_number", "invoice_number", "part_code",
    "part_name", "part_quantity", "remarks",
  ],
  "Part Issued": [
    "serial_number", "invoice_number", "part_code",
    "part_name", "part_quantity", "remarks",
  ],
  "Repair In Progress": [
    "serial_number", "invoice_number", "diagnosis",
    "repair_details", "remarks",
  ],
  "Repair Completed": [
    "serial_number", "invoice_number", "diagnosis",
    "repair_details", "remarks",
  ],
  Testing: [
    "serial_number", "invoice_number", "testing_result", "remarks",
  ],
  "Customer Confirmation": [
    "serial_number", "invoice_number", "customer_confirmation", "remarks",
  ],
  "DOA Approval": [
    "serial_number", "invoice_number", "reason", "remarks",
  ],
  "Request for Cancellation": [
    "serial_number", "invoice_number", "cancellation_reason",
  ],
  Cancelled: [
    "serial_number", "invoice_number", "cancellation_reason",
  ],
  Closed: [
    "serial_number", "invoice_number", "customer_confirmation", "remarks",
  ],
  Reopen: [
    "serial_number", "invoice_number", "reopen_reason",
  ],
};

const WORKFLOW_LABELS = {
  serial_number: "Serial Number",
  invoice_number: "Invoice Number",
  reason: "Reason",
  part_code: "Part Code",
  part_name: "Part Name",
  part_quantity: "Part Quantity",
  diagnosis: "Diagnosis",
  repair_details: "Repair Details",
  testing_result: "Testing Result",
  customer_confirmation: "Customer Confirmation",
  cancellation_reason: "Cancellation Reason",
  reopen_reason: "Reopen Reason",
  remarks: "Remarks",
};

const WORKFLOW_TEXTAREAS = [
  "reason",
  "diagnosis",
  "repair_details",
  "customer_confirmation",
  "cancellation_reason",
  "reopen_reason",
  "remarks",
];

const styles = {
  page: { padding: "26px 4%", minHeight: "100%", background: "#f6f8fb", color: "#172b4d", fontFamily: "Inter, Segoe UI, Arial, sans-serif" },
  heading: { display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 14, marginBottom: 22 },
  title: { fontSize: 28, fontWeight: 750, margin: 0, color: "#14233b" },
  subtitle: { margin: "7px 0 0", color: "#65758b", fontSize: 14 },
  button: { border: "1px solid #d5deea", background: "#fff", borderRadius: 8, padding: "10px 13px", cursor: "pointer", display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 7, color: "#253b5b", fontWeight: 650, fontSize: 13 },
  primary: { border: "1px solid #175ce5", background: "#175ce5", color: "#fff" },
  danger: { border: "1px solid #fecaca", background: "#fff1f2", color: "#b91c1c" },
  buckets: { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(145px,1fr))", gap: 11, marginBottom: 20 },
  bucket: { background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10, padding: 14, minHeight: 85, textAlign: "left", cursor: "pointer", color: "#253b5b" },
  toolbar: { display: "flex", gap: 12, flexWrap: "wrap", background: "#fff", padding: 13, border: "1px solid #e2e8f0", borderRadius: 10, marginBottom: 14 },
  searchWrap: { display: "flex", alignItems: "center", gap: 9, border: "1px solid #d5deea", borderRadius: 8, padding: "0 11px", flex: "1 1 300px", minWidth: 180, background: "#fff" },
  input: { width: "100%", minWidth: 0, padding: "10px 11px", border: "1px solid #d5deea", borderRadius: 7, outline: "none", color: "#172b4d", background: "#fff", boxSizing: "border-box", fontSize: 13 },
  tableWrap: { overflowX: "auto", background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10 },
  table: { borderCollapse: "collapse", width: "100%", minWidth: 850, fontSize: 13 },
  th: { textAlign: "left", padding: "13px 14px", background: "#f8fafc", color: "#62748b", fontSize: 11, fontWeight: 750, borderBottom: "1px solid #e5eaf1", whiteSpace: "nowrap" },
  td: { padding: "13px 14px", borderBottom: "1px solid #edf0f5", verticalAlign: "middle" },
  overlay: { position: "fixed", inset: 0, zIndex: 1000, background: "rgba(15,28,48,.5)", display: "flex", alignItems: "center", justifyContent: "center", padding: 14 },
  modal: { width: "min(850px,100%)", maxHeight: "92vh", overflowY: "auto", background: "#fff", borderRadius: 12, boxShadow: "0 18px 60px rgba(0,0,0,.18)" },
  modalHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, padding: "17px 21px", borderBottom: "1px solid #e7ebf2", position: "sticky", top: 0, background: "#fff", zIndex: 2 },
  modalBody: { padding: 21 },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 14 },
  label: { display: "block", fontSize: 12, color: "#53657d", fontWeight: 700, marginBottom: 6 },
  message: { padding: "11px 13px", borderRadius: 8, background: "#fff7ed", color: "#9a3412", marginBottom: 14, fontSize: 13 },
  section: { border: "1px solid #e2e8f0", borderRadius: 10, padding: 16, marginTop: 18 },
};

function getArray(data) {
  if (Array.isArray(data)) return data;
  return data?.items || data?.results || data?.value || data?.data || [];
}

function firstValue(object, keys, fallback = "") {
  for (const key of keys) {
    const value = object?.[key];
    if (value !== undefined && value !== null && value !== "") return value;
  }
  return fallback;
}

function callId(call) {
  return firstValue(call, ["id", "service_call_id", "serviceCallId"]);
}

function callNumber(call) {
  return firstValue(call, ["call_id", "call_number", "complaint_id", "complaint_number"], `Call #${callId(call) || "-"}`);
}

function callStatus(call) {
  return String(firstValue(call, ["status", "call_status", "current_status"], "Open"));
}

function customerName(call) {
  return firstValue(call, ["customer_name"], call?.customer?.customer_name || call?.customer?.name || "—");
}

function productName(call) {
  return firstValue(call, ["product_model_name", "product_name", "model_name"], call?.product_model?.model_name || "—");
}

function engineerName(call) {
  return firstValue(call, ["engineer_name", "assigned_engineer_name"], call?.engineer?.engineer_name || (call?.engineer_id ? `Engineer #${call.engineer_id}` : "Unassigned"));
}

function dateText(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function matchesBucket(call, bucket) {
  const wanted = String(bucket || "All").toLowerCase();
  const status = callStatus(call).toLowerCase();
  const hasEngineer = Boolean(call.engineer_id || call.assigned_engineer_id);

  if (wanted === "all") return true;
  if (wanted === "reopen") return status === "closed";
  if (wanted === "not assigned") return !hasEngineer && ["open", "new", "not assigned", "unassigned"].includes(status);
  if (wanted === "open") return ["open", "new", "not assigned", "unassigned"].includes(status);
  if (wanted === "assigned") return status === "assigned" || (hasEngineer && ["open", "new"].includes(status));
  if (wanted === "appointment scheduled") return ["appointment scheduled", "appointment confirmed", "appointment"].includes(status);
  if (wanted === "in progress") return ["in progress", "wip", "work in progress"].includes(status);
  if (wanted === "part required") return status === "part required";
  if (wanted === "part pending") return ["part pending", "part order pending"].includes(status);
  if (wanted === "part in transit") return ["part in transit", "part intransit", "part ordered", "part dispatched"].includes(status);
  if (wanted === "part received") return status === "part received";
  if (wanted === "part issued") return status === "part issued";
  if (wanted === "repair in progress") return status === "repair in progress";
  if (wanted === "repair completed") return ["repair completed", "repair complete", "repaired"].includes(status);
  if (wanted === "testing") return ["testing", "testing pending", "test pending", "test failed", "test passed"].includes(status);
  if (wanted === "customer confirmation") return status.includes("customer confirmation") || status === "awaiting customer confirmation";
  if (wanted === "cancelled") return ["cancelled", "canceled", "call cancelled"].includes(status);
  return status === wanted;
}

export default function ServiceCalls() {
  const [calls, setCalls] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [ascCentres, setAscCentres] = useState([]);
  const [engineers, setEngineers] = useState([]);
  const [activeBucket, setActiveBucket] = useState("All");
  const [search, setSearch] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [selectedCall, setSelectedCall] = useState(null);
  const [saving, setSaving] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [editStatus, setEditStatus] = useState("");
  const [editRemarks, setEditRemarks] = useState("");
  const [appointmentOpen, setAppointmentOpen] = useState(false);
  const [appointmentForm, setAppointmentForm] = useState(initialAppointment);
  const [completionOpen, setCompletionOpen] = useState(false);
  const [completion, setCompletion] = useState(initialCompletion);
  const [completionFiles, setCompletionFiles] = useState([]);
  const [action, setAction] = useState("Part Required");

  const [workflowForm, setWorkflowForm] = useState(initialWorkflowForm);
  const [workflowFormOpen, setWorkflowFormOpen] = useState(false);

  const loadCalls = useCallback(async (showSpinner = true) => {
    try {
      if (showSpinner) setLoading(true);
      else setRefreshing(true);
      setError("");

      const [callsResult, appointmentsResult, ascResult, engineersResult] = await Promise.allSettled([
        api.get("/service-calls"),
        api.get("/appointments"),
        api.get("/asc"),
        api.get("/engineers"),
      ]);

      if (callsResult.status === "rejected") throw callsResult.reason;

      setCalls(getArray(callsResult.value.data));
      setAppointments(appointmentsResult.status === "fulfilled" ? getArray(appointmentsResult.value.data) : []);
      setAscCentres(ascResult.status === "fulfilled" ? getArray(ascResult.value.data) : []);
      setEngineers(engineersResult.status === "fulfilled" ? getArray(engineersResult.value.data) : []);
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || "Service calls load nahi ho paaye.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { loadCalls(); }, [loadCalls]);

  const counts = useMemo(() => {
    const result = { All: calls.length };

    BUCKETS.forEach((bucket) => {
      if (bucket.status !== "All") {
        result[bucket.status] = calls.filter((call) => matchesBucket(call, bucket.status)).length;
      }
    });

    return result;
  }, [calls]);

  const visibleCalls = useMemo(() => {
    const query = search.trim().toLowerCase();

    return calls.filter((call) => {
      const priority = String(firstValue(call, ["priority"], "Normal"));
      const searchable = [
        callNumber(call),
        callId(call),
        customerName(call),
        firstValue(call, ["customer_phone", "mobile", "phone", "phone_number"]),
        firstValue(call, ["customer_number", "customer_code"]),
        productName(call),
        firstValue(call, ["serial_number", "serial_no"]),
        firstValue(call, ["invoice_number", "invoice_no", "invoiceNumber"]),
        engineerName(call),
        callStatus(call),
      ].join(" ").toLowerCase();

      return matchesBucket(call, activeBucket) &&
        (priorityFilter === "All" || priority.toLowerCase() === priorityFilter.toLowerCase()) &&
        (!query || searchable.includes(query));
    });
  }, [calls, activeBucket, search, priorityFilter]);

  async function openDetails(call) {
    setSelectedCall(call);
    setMessage("");
    setEditStatus(callStatus(call));
    setEditRemarks("");
    setAppointmentOpen(false);
    setCompletionOpen(false);
    setWorkflowFormOpen(false);

    setWorkflowForm({
      ...initialWorkflowForm,
      serial_number: firstValue(call, ["serial_number", "serial_no"]),
      invoice_number: firstValue(call, ["invoice_number", "invoice_no", "invoiceNumber"]),
    });

    setDetailLoading(true);

    try {
      const id = callId(call);

      if (id) {
        const response = await api.get(`/service-calls/${id}`);
        const payload = response.data?.data ?? response.data?.service_call ?? response.data;
        const detail = Array.isArray(payload) ? payload[0] : payload;

        if (detail && typeof detail === "object") {
          setSelectedCall((previous) => ({ ...previous, ...detail }));
          setEditStatus(callStatus(detail));

          setWorkflowForm((previous) => ({
            ...previous,
            serial_number: firstValue(detail, ["serial_number", "serial_no"], previous.serial_number),
            invoice_number: firstValue(detail, ["invoice_number", "invoice_no", "invoiceNumber"], previous.invoice_number),
          }));
        }
      }
    } catch {
      // List data remains available if the detail endpoint is unavailable.
    } finally {
      setDetailLoading(false);
    }
  }

  async function scheduleAppointment(event) {
    event.preventDefault();
    if (!selectedCall) return;

    const id = callId(selectedCall);
    if (!id) return setMessage("Service Call ID nahi mila.");

    if (
      !appointmentForm.asc_id ||
      !appointmentForm.engineer_id ||
      !appointmentForm.appointment_date ||
      !appointmentForm.appointment_point.trim()
    ) {
      return setMessage("ASC, Engineer, Appointment Date aur Appointment Point required hain.");
    }

    try {
      setSaving(true);
      setMessage("");

      const response = await api.post("/appointments", {
        service_call_id: Number(id),
        asc_id: Number(appointmentForm.asc_id),
        engineer_id: Number(appointmentForm.engineer_id),
        appointment_date: appointmentForm.appointment_date,
        appointment_time: appointmentForm.appointment_time || null,
        appointment_point: appointmentForm.appointment_point.trim(),
        remarks: appointmentForm.remarks.trim(),
      });

      setMessage(response.data?.message || "Appointment scheduled successfully.");
      setAppointmentOpen(false);
      setAppointmentForm(initialAppointment);

      await loadCalls(false);

      setSelectedCall((previous) => previous ? {
        ...previous,
        status: response.data?.service_call?.status || "Appointment Scheduled",
        appointment_date: response.data?.appointment?.appointment_date || appointmentForm.appointment_date,
        appointment_time: response.data?.appointment?.appointment_time || appointmentForm.appointment_time,
      } : previous);

      setEditStatus("Appointment Scheduled");
    } catch (err) {
      setMessage(err?.response?.data?.message || "Appointment schedule nahi hui.");
    } finally {
      setSaving(false);
    }
  }

  async function assignEngineer() {
    if (!selectedCall) return;

    const id = callId(selectedCall);
    const rawId = window.prompt("Engineer ID enter karo:");

    if (rawId === null) return;

    const engineerId = Number(rawId);

    if (!Number.isInteger(engineerId) || engineerId <= 0) {
      return setMessage("Valid numeric Engineer ID enter karo.");
    }

    try {
      setSaving(true);
      setMessage("");

      const response = await api.post(`/asc-assignments/service-calls/${id}/assign-engineer`, {
        engineer_id: engineerId,
        remarks: editRemarks.trim() || "Assigned to engineer",
      });

      setMessage(response.data?.message || "Engineer assigned successfully.");

      await loadCalls(false);

      setSelectedCall((previous) => previous ? {
        ...previous,
        engineer_id: engineerId,
        status: response.data?.service_call?.status || "Assigned",
      } : previous);

      setEditStatus("Assigned");
    } catch (err) {
      setMessage(err?.response?.data?.message || "Engineer assign nahi hua. Confirm karo ki ASC assigned hai aur engineer usi ASC ka active engineer hai.");
    } finally {
      setSaving(false);
    }
  }

  async function saveStatus() {
    if (!selectedCall) return;

    const id = callId(selectedCall);

    if (!workflowForm.serial_number.trim() || !workflowForm.invoice_number.trim()) {
      setWorkflowFormOpen(true);
      return setMessage("Status update karne ke liye Serial Number aur Invoice Number mandatory hain.");
    }

    try {
      setSaving(true);
      setMessage("");

      const payload = {
        status: editStatus === "Reopen" ? "Open" : editStatus,
        workflow_action: editStatus === "Reopen" ? "Reopen" : "Update",
        serial_number: workflowForm.serial_number.trim(),
        invoice_number: workflowForm.invoice_number.trim(),
        remarks: editRemarks.trim(),
      };

      const response = await api.post(`/service-calls/${id}/status`, payload);

      setMessage(response.data?.message || "Status update request successful.");

      await loadCalls(false);

      setSelectedCall((previous) => previous ? {
        ...previous,
        status: payload.status,
        serial_number: payload.serial_number,
        invoice_number: payload.invoice_number,
      } : previous);
    } catch (err) {
      setMessage(err?.response?.data?.message || "Status update nahi hua. Backend route aur database fields check karo.");
    } finally {
      setSaving(false);
    }
  }

  async function saveWorkflowForm(event) {
    event.preventDefault();

    if (!selectedCall) return;

    const id = callId(selectedCall);

    if (!id) return setMessage("Service Call ID nahi mila.");

    if (!workflowForm.serial_number.trim() || !workflowForm.invoice_number.trim()) {
      return setMessage("Serial Number aur Invoice Number mandatory hain.");
    }

    const requiredByStatus = {
      "Part Required": ["part_code", "part_name", "part_quantity", "reason"],
      "Part Pending": ["part_code", "part_name", "part_quantity", "reason"],
      "Part In Transit": ["part_code", "part_name", "part_quantity"],
      "Part Received": ["part_code", "part_name", "part_quantity"],
      "Part Issued": ["part_code", "part_name", "part_quantity"],
      "Repair In Progress": ["diagnosis", "repair_details"],
      "Repair Completed": ["diagnosis", "repair_details"],
      Testing: ["testing_result"],
      "Customer Confirmation": ["customer_confirmation"],
      "DOA Approval": ["reason"],
      "Request for Cancellation": ["cancellation_reason"],
      Cancelled: ["cancellation_reason"],
      Closed: ["customer_confirmation"],
      Reopen: ["reopen_reason"],
    };

    const required = requiredByStatus[editStatus] || ["remarks"];

    const missing = required.filter(
      (field) => !String(workflowForm[field] ?? "").trim()
    );

    if (missing.length) {
      return setMessage(
        `Required fields fill karo: ${missing.map((field) => WORKFLOW_LABELS[field] || field).join(", ")}`
      );
    }

    const payload = {
      ...workflowForm,
      serial_number: workflowForm.serial_number.trim(),
      invoice_number: workflowForm.invoice_number.trim(),
      status: editStatus === "Reopen" ? "Open" : editStatus,
      workflow_action: editStatus === "Reopen" ? "Reopen" : "Update",
      remarks: workflowForm.remarks.trim(),
    };

    try {
      setSaving(true);
      setMessage("");

      const response = await api.post(`/service-calls/${id}/status`, payload);

      setMessage(
        response.data?.message ||
        (editStatus === "Reopen" ? "Reopen request submitted." : `${editStatus} form submit ho gaya.`)
      );

      setSelectedCall((previous) => previous ? {
        ...previous,
        status: payload.status,
        serial_number: payload.serial_number,
        invoice_number: payload.invoice_number,
      } : previous);

      setWorkflowFormOpen(false);
      await loadCalls(false);
    } catch (err) {
      setMessage(
        err?.response?.data?.message ||
        "Form save nahi hua. Backend ko ye workflow fields support karne honge."
      );
    } finally {
      setSaving(false);
    }
  }

  async function runWorkflowAction(nextAction) {
    if (!selectedCall) return;

    const id = callId(selectedCall);

    if (["cancel", "cancelled", "revisit"].includes(nextAction.toLowerCase()) && !editRemarks.trim()) {
      return setMessage("Is action ke liye remarks required hain.");
    }

    try {
      setSaving(true);
      setMessage("");

      const response = await api.post(`/asc-assignments/service-calls/${id}/update`, {
        action: nextAction,
        remarks: editRemarks.trim(),
      });

      setMessage(response.data?.message || `${nextAction} action successful.`);

      await loadCalls(false);

      if (["Part Required", "Part Pending"].includes(nextAction)) {
        setSelectedCall((previous) => previous ? { ...previous, status: "Part Pending" } : previous);
        setEditStatus("Part Pending");
      }
    } catch (err) {
      setMessage(err?.response?.data?.message || `${nextAction} action complete nahi hua.`);
    } finally {
      setSaving(false);
    }
  }

  function validateCompletion() {
    const required = [
      ["diagnosis", "Diagnosis"],
      ["repairDetails", "Repair Details"],
      ["testingResult", "Testing Result"],
      ["engineerRemarks", "Engineer Remarks"],
      ["happyCode", "Happy Code / Customer Confirmation"],
    ];

    const missing = required.filter(([key]) => !String(completion[key] || "").trim());

    if (missing.length) {
      return setMessage(`Please fill: ${missing.map(([, label]) => label).join(", ")}`);
    }

    if (!completionFiles.length) {
      return setMessage("Required service photos/documents select karo.");
    }

    setMessage("Form validate ho gaya. Diagnosis, photos aur customer confirmation permanently save karne ke liye backend endpoint support zaroori hai. Call close nahi ki gayi.");
  }

  const activeAppointment = appointments.find((item) =>
    Number(item.service_call_id) === Number(callId(selectedCall)) &&
    ["Scheduled", "Confirmed", "In Progress"].includes(item.status)
  );

  const workflowFields = WORKFLOW_FIELDS[editStatus] || [
    "serial_number", "invoice_number", "remarks",
  ];

  function updateWorkflowField(field, value) {
    setWorkflowForm((previous) => ({ ...previous, [field]: value }));
  }

  function renderWorkflowField(field) {
    const label = WORKFLOW_LABELS[field] || field;
    const required = true;
    const isTextarea = WORKFLOW_TEXTAREAS.includes(field);

    return (
      <div key={field}>
        <label style={styles.label}>
          {label} <span style={{ color: "#dc2626" }}>*</span>
        </label>

        {field === "testing_result" ? (
          <select
            required
            style={styles.input}
            value={workflowForm[field]}
            onChange={(event) => updateWorkflowField(field, event.target.value)}
          >
            <option value="">Select Testing Result</option>
            <option value="PASS">PASS</option>
            <option value="FAIL">FAIL</option>
            <option value="PENDING">PENDING</option>
          </select>
        ) : field === "part_quantity" ? (
          <input
            required
            min="1"
            type="number"
            style={styles.input}
            value={workflowForm[field]}
            onChange={(event) => updateWorkflowField(field, event.target.value)}
          />
        ) : isTextarea ? (
          <textarea
            required={required}
            rows={3}
            style={{ ...styles.input, resize: "vertical" }}
            value={workflowForm[field]}
            onChange={(event) => updateWorkflowField(field, event.target.value)}
          />
        ) : (
          <input
            required={required}
            style={styles.input}
            value={workflowForm[field]}
            onChange={(event) => updateWorkflowField(field, event.target.value)}
            placeholder={`Enter ${label}`}
          />
        )}
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <div style={styles.heading}>
        <div>
          <h1 style={styles.title}>Service Calls</h1>
          <p style={styles.subtitle}>Customer complaints, assignments, appointments and service status.</p>
        </div>

        <button
          type="button"
          style={styles.button}
          onClick={() => loadCalls(false)}
          disabled={refreshing}
        >
          <RefreshCw size={16} /> {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error && <div style={styles.message}>{error}</div>}

      <div style={styles.buckets}>
        {BUCKETS.map((bucket) => {
          const Icon = bucket.icon;
          const active = activeBucket === bucket.status;

          return (
            <button
              type="button"
              key={bucket.status}
              onClick={() => setActiveBucket(bucket.status)}
              style={{
                ...styles.bucket,
                borderColor: active ? "#2563eb" : "#e2e8f0",
                boxShadow: active ? "0 0 0 1px #2563eb" : "none",
                background: active ? "#f1f6ff" : "#fff",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <Icon size={16} color={active ? "#175ce5" : "#64748b"} />
                <span style={{ fontSize: 12, fontWeight: 650 }}>{bucket.label}</span>
              </div>
              <div style={{ fontSize: 24, fontWeight: 750 }}>
                {loading ? "—" : counts[bucket.status] ?? 0}
              </div>
            </button>
          );
        })}
      </div>

      <div style={styles.toolbar}>
        <div style={styles.searchWrap}>
          <Search size={17} color="#8797ad" />
          <input
            aria-label="Search service calls"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search call, customer, mobile, serial number, product..."
            style={{ border: 0, outline: 0, padding: "11px 0", width: "100%", minWidth: 0 }}
          />
        </div>

        <select
          aria-label="Filter by priority"
          value={priorityFilter}
          onChange={(event) => setPriorityFilter(event.target.value)}
          style={{ ...styles.input, width: 160 }}
        >
          <option value="All">All Priority</option>
          <option value="Normal">Normal</option>
          <option value="High">High</option>
          <option value="Urgent">Urgent</option>
          <option value="Low">Low</option>
        </select>
      </div>

      <div style={{ marginBottom: 12, color: "#64748b", fontSize: 12 }}>
        Showing {visibleCalls.length} of {calls.length} calls
        {activeBucket !== "All" ? ` · ${activeBucket}` : ""}
      </div>

      <div style={styles.tableWrap}>
        <table style={styles.table}>
          <thead>
            <tr>
              {["CALL ID", "CUSTOMER / MOBILE", "PRODUCT / SERIAL", "ENGINEER", "STATUS", "PRIORITY", "CREATED", "ACTION"].map((heading) => (
                <th style={styles.th} key={heading}>{heading}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td colSpan={8} style={{ ...styles.td, textAlign: "center", padding: 35 }}>
                  <LoaderCircle size={18} /> Loading service calls...
                </td>
              </tr>
            ) : visibleCalls.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ ...styles.td, textAlign: "center", padding: 35, color: "#64748b" }}>
                  Is bucket mein koi service call nahi mili.
                </td>
              </tr>
            ) : visibleCalls.map((call, index) => {
              const status = callStatus(call);

              const badgeColor = status.toLowerCase().includes("cancel")
                ? { background: "#fee2e2", color: "#b91c1c" }
                : status.toLowerCase().includes("part")
                ? { background: "#fff7ed", color: "#c2410c" }
                : ["closed", "repair completed", "part received"].includes(status.toLowerCase())
                ? { background: "#dcfce7", color: "#166534" }
                : ["assigned", "in progress"].includes(status.toLowerCase())
                ? { background: "#dbeafe", color: "#1d4ed8" }
                : { background: "#f1f5f9", color: "#475569" };

              return (
                <tr key={callId(call) ?? index}>
                  <td style={styles.td}>
                    <strong>{callNumber(call)}</strong>
                    <div style={{ fontSize: 11, color: "#73839a", marginTop: 4 }}>
                      {firstValue(call, ["complaint_id", "reference_number"], "")}
                    </div>
                  </td>

                  <td style={styles.td}>
                    <strong>{customerName(call)}</strong>
                    <div style={{ fontSize: 11, color: "#73839a", marginTop: 4 }}>
                      {firstValue(call, ["customer_phone", "mobile", "phone", "customer_code"], "—")}
                    </div>
                  </td>

                  <td style={styles.td}>
                    {productName(call)}
                    <div style={{ fontSize: 11, color: "#73839a", marginTop: 4 }}>
                      {firstValue(call, ["serial_number", "serial_no"], "")}
                    </div>
                    <div style={{ fontSize: 11, color: "#73839a", marginTop: 4 }}>
                      Invoice: {firstValue(call, ["invoice_number", "invoice_no", "invoiceNumber"], "—")}
                    </div>
                  </td>

                  <td style={styles.td}>{engineerName(call)}</td>

                  <td style={styles.td}>
                    <span style={{
                      ...badgeColor,
                      display: "inline-block",
                      borderRadius: 20,
                      padding: "5px 9px",
                      fontSize: 11,
                      fontWeight: 700,
                      whiteSpace: "nowrap",
                    }}>
                      {status}
                    </span>
                  </td>

                  <td style={styles.td}>{firstValue(call, ["priority"], "Normal")}</td>

                  <td style={styles.td}>
                    {dateText(firstValue(call, ["created_at", "created_on", "call_date", "registered_at"]))}
                  </td>

                  <td style={styles.td}>
                    <button type="button" style={styles.button} onClick={() => openDetails(call)}>
                      <Eye size={14} /> Open
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {selectedCall && (
        <div
          style={styles.overlay}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !saving) {
              setSelectedCall(null);
            }
          }}
        >
          <div style={styles.modal} role="dialog" aria-modal="true" aria-label="Service call details">
            <div style={styles.modalHeader}>
              <div>
                <h2 style={{ margin: 0, fontSize: 19 }}>Service Call Details</h2>
                <p style={{ margin: "5px 0 0", color: "#64748b", fontSize: 12 }}>
                  {callNumber(selectedCall)} · Complaint ID: {firstValue(selectedCall, ["complaint_id"], "—")}
                </p>
              </div>

              <button
                type="button"
                style={{ ...styles.button, padding: 7 }}
                onClick={() => setSelectedCall(null)}
                aria-label="Close details"
                disabled={saving}
              >
                <X size={17} />
              </button>
            </div>

            <div style={styles.modalBody}>
              {detailLoading && (
                <p style={{ color: "#64748b", fontSize: 12 }}>
                  <LoaderCircle size={14} /> Loading latest details...
                </p>
              )}

              {message && <div style={styles.message}>{message}</div>}

              <div style={styles.grid}>
                {[
                  ["Customer", customerName(selectedCall)],
                  ["Customer Mobile", firstValue(selectedCall, ["customer_phone", "mobile", "phone", "phone_number"], "—")],
                  ["Customer Number", firstValue(selectedCall, ["customer_number", "customer_code"], "—")],
                  ["Product", productName(selectedCall)],
                  ["Serial Number", firstValue(selectedCall, ["serial_number", "serial_no"], "—")],
                  ["Invoice Number", firstValue(selectedCall, ["invoice_number", "invoice_no", "invoiceNumber"], "—")],
                  ["Call Type", firstValue(selectedCall, ["call_type_name", "call_type"], "—")],
                  ["Symptom", firstValue(selectedCall, ["symptom_name", "symptom"], "—")],
                  ["Status", callStatus(selectedCall)],
                  ["Priority", firstValue(selectedCall, ["priority"], "Normal")],
                  ["Engineer", engineerName(selectedCall)],
                  ["ASC / Service Centre", firstValue(selectedCall, ["asc_name", "service_center_name"], selectedCall.asc_id ? `ASC #${selectedCall.asc_id}` : "—")],
                  ["Complaint Date", dateText(firstValue(selectedCall, ["registered_at", "created_at", "call_date"]))],
                  ["Appointment Date", dateText(firstValue(activeAppointment || selectedCall, ["appointment_date", "scheduled_date"]))],
                  ["Appointment Time", firstValue(activeAppointment || selectedCall, ["appointment_time"], "—")],
                  ["Appointment Point", firstValue(activeAppointment || selectedCall, ["appointment_point"], "—")],
                  ["SLA Due", dateText(firstValue(selectedCall, ["sla_due_at", "promise_date"]))],
                ].map(([label, value]) => (
                  <div key={label}>
                    <label style={styles.label}>{label}</label>
                    <div style={{
                      padding: "10px",
                      border: "1px solid #e5eaf1",
                      borderRadius: 7,
                      background: "#f8fafc",
                      fontSize: 13,
                      minHeight: 17,
                      overflowWrap: "anywhere",
                    }}>
                      {String(value ?? "—")}
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: 15 }}>
                <label style={styles.label}>Complaint Description</label>
                <div style={{
                  padding: 12,
                  border: "1px solid #e5eaf1",
                  borderRadius: 7,
                  minHeight: 42,
                  whiteSpace: "pre-wrap",
                  fontSize: 13,
                }}>
                  {firstValue(selectedCall, ["complaint_description", "description", "complaint_details", "remarks"], "No description provided.")}
                </div>
              </div>

              <section style={styles.section}>
                <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Call Actions</h3>

                <div style={styles.grid}>
                  <div>
                    <label style={styles.label}>Update Status</label>
                    <select
                      style={styles.input}
                      value={editStatus}
                      onChange={(event) => {
                        setEditStatus(event.target.value);
                        setMessage("");
                      }}
                    >
                      {!STATUS_OPTIONS.includes(editStatus) && editStatus && (
                        <option value={editStatus}>{editStatus}</option>
                      )}
                      {STATUS_OPTIONS.map((status) => (
                        <option key={status} value={status}>{status}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={styles.label}>Remarks</label>
                    <input
                      style={styles.input}
                      value={editRemarks}
                      onChange={(event) => setEditRemarks(event.target.value)}
                      placeholder="Enter remarks"
                    />
                  </div>
                </div>

                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
                  <button
                    type="button"
                    style={{ ...styles.button, ...styles.primary }}
                    disabled={saving}
                    onClick={saveStatus}
                  >
                    {saving ? "Saving..." : "Save Status"}
                  </button>

                  <button
                    type="button"
                    style={styles.button}
                    disabled={saving}
                    onClick={() => {
                      setMessage("");
                      setWorkflowForm((previous) => ({
                        ...previous,
                        serial_number: firstValue(selectedCall, ["serial_number", "serial_no"], previous.serial_number),
                        invoice_number: firstValue(selectedCall, ["invoice_number", "invoice_no", "invoiceNumber"], previous.invoice_number),
                        remarks: editRemarks,
                      }));
                      setWorkflowFormOpen((value) => !value);
                      setAppointmentOpen(false);
                      setCompletionOpen(false);
                    }}
                  >
                    <CheckCircle2 size={15} />
                    {workflowFormOpen ? "Hide Status Form" : "Open Status Form"}
                  </button>

                  {!selectedCall.engineer_id && (
                    <button
                      type="button"
                      style={styles.button}
                      disabled={saving}
                      onClick={assignEngineer}
                    >
                      <UserRound size={15} /> Assign Engineer
                    </button>
                  )}

                  <button
                    type="button"
                    style={styles.button}
                    disabled={saving}
                    onClick={() => {
                      setMessage("");
                      setAppointmentForm({
                        ...initialAppointment,
                        asc_id: String(selectedCall.asc_id || selectedCall.assigned_asc_id || ""),
                        engineer_id: String(selectedCall.engineer_id || ""),
                      });
                      setAppointmentOpen((value) => !value);
                      setCompletionOpen(false);
                      setWorkflowFormOpen(false);
                    }}
                  >
                    <CalendarDays size={15} />
                    {appointmentOpen ? "Hide Appointment" : "Schedule Appointment"}
                  </button>

                  <button
                    type="button"
                    style={styles.button}
                    disabled={saving}
                    onClick={() => {
                      setEditStatus("Part Required");
                      setWorkflowFormOpen(true);
                      setAppointmentOpen(false);
                      setCompletionOpen(false);
                      setWorkflowForm((previous) => ({
                        ...previous,
                        serial_number: firstValue(selectedCall, ["serial_number", "serial_no"], previous.serial_number),
                        invoice_number: firstValue(selectedCall, ["invoice_number", "invoice_no", "invoiceNumber"], previous.invoice_number),
                      }));
                      setMessage("");
                    }}
                  >
                    <Package size={15} /> Part Required
                  </button>

                  <button
                    type="button"
                    style={styles.button}
                    disabled={saving}
                    onClick={() => runWorkflowAction("Revisit")}
                  >
                    Revisit
                  </button>

                  <button
                    type="button"
                    style={{ ...styles.button, ...styles.danger }}
                    disabled={saving}
                    onClick={() => runWorkflowAction("cancel")}
                  >
                    Cancel Call
                  </button>

                  <button
                    type="button"
                    style={styles.button}
                    disabled={saving}
                    onClick={() => {
                      setCompletionOpen((value) => !value);
                      setAppointmentOpen(false);
                      setWorkflowFormOpen(false);
                    }}
                  >
                    Completion Form
                  </button>
                </div>
              </section>

              {workflowFormOpen && (
                <section style={{ ...styles.section, borderColor: "#bfdbfe", background: "#f8fbff" }}>
                  <h3 style={{ margin: "0 0 7px", fontSize: 16 }}>
                    {editStatus === "Reopen" ? "Reopen Service Call Form" : `${editStatus} Form`}
                  </h3>

                  <p style={{ margin: "0 0 14px", color: "#64748b", fontSize: 12 }}>
                    Serial Number aur Invoice Number mandatory hain. Selected status ke required fields bhi fill karo.
                  </p>

                  <form onSubmit={saveWorkflowForm}>
                    <div style={styles.grid}>
                      {workflowFields.map((field) => renderWorkflowField(field))}
                    </div>

                    <div style={{ display: "flex", justifyContent: "flex-end", gap: 9, marginTop: 16 }}>
                      <button
                        type="button"
                        style={styles.button}
                        disabled={saving}
                        onClick={() => setWorkflowFormOpen(false)}
                      >
                        Cancel
                      </button>

                      <button
                        type="submit"
                        style={{ ...styles.button, ...styles.primary }}
                        disabled={saving}
                      >
                        {saving ? "Saving..." : "Save Workflow Form"}
                      </button>
                    </div>
                  </form>
                </section>
              )}

              {appointmentOpen && (
                <section style={{ ...styles.section, borderColor: "#bfdbfe", background: "#f8fbff" }}>
                  <h3 style={{ margin: "0 0 5px", fontSize: 16 }}>Schedule Service Appointment</h3>
                  <p style={{ margin: "0 0 15px", color: "#64748b", fontSize: 12 }}>
                    Required fields are checked before sending to the appointments API.
                  </p>

                  <form onSubmit={scheduleAppointment}>
                    <div style={styles.grid}>
                      <div>
                        <label style={styles.label}>Service Centre / ASC *</label>
                        <select
                          required
                          style={styles.input}
                          value={appointmentForm.asc_id}
                          onChange={(event) => {
                            const ascId = event.target.value;
                            setAppointmentForm((previous) => ({
                              ...previous,
                              asc_id: ascId,
                              engineer_id: "",
                            }));
                          }}
                        >
                          <option value="">Select ASC</option>
                          {ascCentres.map((asc) => (
                            <option key={asc.id} value={asc.id}>
                              {asc.asc_name || asc.name || asc.asc_code || `ASC #${asc.id}`}
                              {asc.status ? ` (${asc.status})` : ""}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label style={styles.label}>Engineer *</label>
                        <select
                          required
                          style={styles.input}
                          value={appointmentForm.engineer_id}
                          onChange={(event) => setAppointmentForm((previous) => ({
                            ...previous,
                            engineer_id: event.target.value,
                          }))}
                        >
                          <option value="">Select engineer</option>
                          {engineers
                            .filter((engineer) =>
                              String(engineer.asc_id) === String(appointmentForm.asc_id) &&
                              (!engineer.status || engineer.status === "Active")
                            )
                            .map((engineer) => (
                              <option key={engineer.id} value={engineer.id}>
                                {engineer.engineer_name || engineer.name || engineer.engineer_code || `Engineer #${engineer.id}`}
                              </option>
                            ))}
                        </select>

                        {appointmentForm.asc_id &&
                          engineers.filter((engineer) =>
                            String(engineer.asc_id) === String(appointmentForm.asc_id) &&
                            (!engineer.status || engineer.status === "Active")
                          ).length === 0 && (
                            <p style={{ color: "#b45309", fontSize: 12 }}>
                              No active engineers were returned for this ASC.
                            </p>
                          )}
                      </div>

                      <div>
                        <label style={styles.label}>Appointment Date *</label>
                        <input
                          required
                          type="date"
                          min={new Date().toISOString().slice(0, 10)}
                          style={styles.input}
                          value={appointmentForm.appointment_date}
                          onChange={(event) => setAppointmentForm((previous) => ({
                            ...previous,
                            appointment_date: event.target.value,
                          }))}
                        />
                      </div>

                      <div>
                        <label style={styles.label}>Appointment Time</label>
                        <input
                          type="time"
                          style={styles.input}
                          value={appointmentForm.appointment_time}
                          onChange={(event) => setAppointmentForm((previous) => ({
                            ...previous,
                            appointment_time: event.target.value,
                          }))}
                        />
                      </div>

                      <div>
                        <label style={styles.label}>Appointment Point / Address *</label>
                        <input
                          required
                          style={styles.input}
                          value={appointmentForm.appointment_point}
                          onChange={(event) => setAppointmentForm((previous) => ({
                            ...previous,
                            appointment_point: event.target.value,
                          }))}
                          placeholder="Customer address / visit point"
                        />
                      </div>

                      <div>
                        <label style={styles.label}>Appointment Remarks</label>
                        <input
                          style={styles.input}
                          value={appointmentForm.remarks}
                          onChange={(event) => setAppointmentForm((previous) => ({
                            ...previous,
                            remarks: event.target.value,
                          }))}
                          placeholder="Visit instructions or remarks"
                        />
                      </div>
                    </div>

                    <div style={{ display: "flex", gap: 9, justifyContent: "flex-end", marginTop: 16 }}>
                      <button
                        type="button"
                        style={styles.button}
                        onClick={() => setAppointmentOpen(false)}
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        style={{ ...styles.button, ...styles.primary }}
                        disabled={saving}
                      >
                        {saving ? "Saving..." : "Save Appointment"}
                      </button>
                    </div>
                  </form>
                </section>
              )}

              {completionOpen && (
                <section style={{ ...styles.section, borderColor: "#bfdbfe", background: "#f8fbff" }}>
                  <h3 style={{ margin: "0 0 7px", fontSize: 16 }}>Service Completion Form</h3>
                  <p style={{ margin: "0 0 14px", color: "#64748b", fontSize: 12 }}>
                    Form validates the required information and attachments; it does not falsely close the call.
                  </p>

                  <div style={styles.grid}>
                    {[
                      ["symptom", "Observed Symptom"],
                      ["faultCode", "Fault Code"],
                      ["diagnosis", "Diagnosis *"],
                      ["repairCode", "Repair Code"],
                      ["repairDetails", "Repair Details *"],
                      ["testingResult", "Testing Result *"],
                      ["engineerRemarks", "Engineer Remarks *"],
                      ["happyCode", "Happy Code / Confirmation *"],
                    ].map(([key, label]) => (
                      <div key={key}>
                        <label style={styles.label}>{label}</label>

                        {["repairDetails", "engineerRemarks"].includes(key) ? (
                          <textarea
                            rows={3}
                            style={{ ...styles.input, resize: "vertical" }}
                            value={completion[key]}
                            onChange={(event) => setCompletion((previous) => ({
                              ...previous,
                              [key]: event.target.value,
                            }))}
                          />
                        ) : key === "testingResult" ? (
                          <select
                            style={styles.input}
                            value={completion[key]}
                            onChange={(event) => setCompletion((previous) => ({
                              ...previous,
                              [key]: event.target.value,
                            }))}
                          >
                            <option value="">Select result</option>
                            <option value="PASS">PASS</option>
                            <option value="FAIL">FAIL</option>
                            <option value="PENDING">PENDING</option>
                          </select>
                        ) : (
                          <input
                            style={styles.input}
                            value={completion[key]}
                            onChange={(event) => setCompletion((previous) => ({
                              ...previous,
                              [key]: event.target.value,
                            }))}
                          />
                        )}
                      </div>
                    ))}

                    <div style={{ gridColumn: "1 / -1" }}>
                      <label style={styles.label}>Service Photos / Documents *</label>
                      <input
                        type="file"
                        multiple
                        accept="image/*,.pdf"
                        style={styles.input}
                        onChange={(event) => setCompletionFiles(Array.from(event.target.files || []))}
                      />
                      {completionFiles.map((file, index) => (
                        <div key={`${file.name}-${index}`} style={{ fontSize: 12, marginTop: 5 }}>
                          {file.name}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 14 }}>
                    <button
                      type="button"
                      style={{ ...styles.button, ...styles.primary }}
                      onClick={validateCompletion}
                    >
                      Validate Form
                    </button>
                  </div>
                </section>
              )}

              {["Part Pending", "Part Required"].includes(callStatus(selectedCall)) && (
                <div style={{ ...styles.message, marginTop: 16 }}>
                  Part workflow: part requirement, quantity and reason are collected in the status-specific form. Actual inventory/order/receipt records must be saved by the backend workflow.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
