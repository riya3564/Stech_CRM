
import { useEffect, useState } from "react";
import api from "../../services/api";

const css = {
  page: { padding: 24, color: "#1f2937" },
  title: { margin: "0 0 6px", fontSize: 26 },
  subtitle: { color: "#6b7280", marginBottom: 22 },
  tabs: { display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 18 },
  tab: {
    border: "1px solid #d1d5db",
    padding: "10px 16px",
    borderRadius: 7,
    cursor: "pointer",
    background: "#fff",
    color: "#374151",
    fontWeight: 600,
  },
  activeTab: {
    background: "#2563eb",
    color: "#fff",
    borderColor: "#2563eb",
  },
  stats: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: 14,
    marginBottom: 20,
  },
  stat: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 9,
    padding: 17,
  },
  label: { color: "#6b7280", fontSize: 13, marginBottom: 8 },
  number: { fontSize: 25, fontWeight: 700 },
  toolbar: { display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 16 },
  input: {
    boxSizing: "border-box",
    padding: 11,
    border: "1px solid #d1d5db",
    borderRadius: 7,
    fontSize: 14,
    minWidth: 180,
    flex: 1,
  },
  button: {
    background: "#2563eb",
    color: "#fff",
    border: 0,
    borderRadius: 7,
    padding: "11px 16px",
    cursor: "pointer",
    fontWeight: 600,
  },
  panel: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 10,
    overflow: "hidden",
  },
  wrap: { overflowX: "auto" },
  table: { width: "100%", minWidth: 720, borderCollapse: "collapse" },
  th: {
    textAlign: "left",
    background: "#f9fafb",
    color: "#6b7280",
    padding: 13,
    fontSize: 12,
    borderBottom: "1px solid #e5e7eb",
  },
  td: {
    padding: 13,
    fontSize: 13,
    borderBottom: "1px solid #f3f4f6",
  },
  field: { display: "grid", gap: 6, marginBottom: 14 },
  fieldLabel: { fontSize: 13, fontWeight: 600 },
  message: { padding: 16, fontSize: 14 },
};

function listFrom(response, keys = []) {
  const data = response?.data ?? response;
  if (Array.isArray(data)) return data;

  for (const key of keys) {
    if (Array.isArray(data?.[key])) return data[key];
  }

  if (Array.isArray(data?.data)) return data.data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function getError(err) {
  return (
    err?.response?.data?.message ||
    err?.response?.data?.error ||
    "Request failed. Backend/API ko check karna hoga."
  );
}

function Status({ value }) {
  const status = value || "Not specified";
  const text = String(status);
  const lower = text.toLowerCase();
  const done =
    lower.includes("received") ||
    lower.includes("complete") ||
    lower.includes("approved") ||
    lower.includes("available");
  const failed =
    lower.includes("reject") ||
    lower.includes("cancel") ||
    lower.includes("fail");

  return (
    <span
      style={{
        display: "inline-block",
        padding: "5px 9px",
        borderRadius: 20,
        fontSize: 12,
        fontWeight: 600,
        background: done ? "#dcfce7" : failed ? "#fee2e2" : "#dbeafe",
        color: done ? "#166534" : failed ? "#991b1b" : "#1d4ed8",
      }}
    >
      {text}
    </span>
  );
}

export default function Parts() {
  const [tab, setTab] = useState("requirements");
  const [parts, setParts] = useState([]);
  const [requirements, setRequirements] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [form, setForm] = useState({
    part_code: "",
    part_name: "",
    description: "",
    category_id: "",
    brand_id: "",
    product_type_id: "",
  });

  async function loadData() {
    setLoading(true);
    setError("");
    setNotice("");

    const results = await Promise.allSettled([
      api.get("/parts"),
      api.get("/part-requirements"),
    ]);

    if (results[0].status === "fulfilled") {
      setParts(
        listFrom(results[0].value, ["parts", "items", "results"])
      );
    } else {
      setError("Parts list load nahi hui: " + getError(results[0].reason));
    }

    if (results[1].status === "fulfilled") {
      setRequirements(
        listFrom(results[1].value, ["part_requirements", "requirements", "items"])
      );
    } else {
      setError((previous) =>
        previous
          ? previous + " | Part requirements: " + getError(results[1].reason)
          : "Part requirements load nahi hui: " + getError(results[1].reason)
      );
    }

    setLoading(false);
  }

  useEffect(() => {
    loadData();
  }, []);

  function changeForm(event) {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  }

  async function createPart(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");

    const payload = {
      part_code: form.part_code.trim(),
      part_name: form.part_name.trim(),
      description: form.description.trim(),
      category_id: Number(form.category_id),
    };

    if (form.brand_id.trim()) payload.brand_id = Number(form.brand_id);
    if (form.product_type_id.trim()) {
      payload.product_type_id = Number(form.product_type_id);
    }

    if (
      !payload.part_code ||
      !payload.part_name ||
      !Number.isInteger(payload.category_id) ||
      payload.category_id <= 0
    ) {
      setError("Part code, part name aur valid category ID bharna zaroori hai.");
      setSaving(false);
      return;
    }

    try {
      await api.post("/parts", payload);
      setNotice("Part master record successfully create ho gaya.");
      setForm({
        part_code: "",
        part_name: "",
        description: "",
        category_id: "",
        brand_id: "",
        product_type_id: "",
      });
      await loadData();
    } catch (err) {
      setError(getError(err));
    } finally {
      setSaving(false);
    }
  }

  const visibleParts = parts.filter((part) => {
    const term = search.toLowerCase().trim();
    if (!term) return true;

    return [
      part.part_code,
      part.part_name,
      part.description,
      part.brand_name,
      part.category_name,
      part.product_type_name,
      part.status,
    ].some(
      (value) =>
        value !== undefined &&
        value !== null &&
        String(value).toLowerCase().includes(term)
    );
  });

  const visibleRequirements = requirements.filter((item) => {
    const term = search.toLowerCase().trim();
    if (!term) return true;

    return [
      item.requirement_number,
      item.service_call_id,
      item.complaint_id,
      item.part_name,
      item.part_code,
      item.required_reason,
      item.status,
      item.remarks,
    ].some(
      (value) =>
        value !== undefined &&
        value !== null &&
        String(value).toLowerCase().includes(term)
    );
  });

  const pendingCount = requirements.filter((item) =>
    ["pending", "checking", "requested"].includes(
      String(item.status || "").toLowerCase()
    )
  ).length;

  const receivedCount = requirements.filter((item) =>
    String(item.status || "").toLowerCase().includes("received")
  ).length;

  return (
    <div style={css.page}>
      <h1 style={css.title}>Parts & Part Requirements</h1>
      <div style={css.subtitle}>
        Service-level part records and requests linked to service calls
      </div>

      <div style={css.stats}>
        <div style={css.stat}>
          <div style={css.label}>Parts Master</div>
          <div style={css.number}>{parts.length}</div>
        </div>
        <div style={css.stat}>
          <div style={css.label}>Part Requirements</div>
          <div style={css.number}>{requirements.length}</div>
        </div>
        <div style={css.stat}>
          <div style={css.label}>Pending / Checking</div>
          <div style={css.number}>{pendingCount}</div>
        </div>
        <div style={css.stat}>
          <div style={css.label}>Received Requirements</div>
          <div style={css.number}>{receivedCount}</div>
        </div>
      </div>

      <div style={css.tabs}>
        <button
          type="button"
          style={{ ...css.tab, ...(tab === "requirements" ? css.activeTab : {}) }}
          onClick={() => {
            setTab("requirements");
            setSearch("");
            setNotice("");
          }}
        >
          Part Requirements
        </button>
        <button
          type="button"
          style={{ ...css.tab, ...(tab === "parts" ? css.activeTab : {}) }}
          onClick={() => {
            setTab("parts");
            setSearch("");
            setNotice("");
          }}
        >
          Parts Master
        </button>
        <button
          type="button"
          style={{ ...css.tab, ...(tab === "add" ? css.activeTab : {}) }}
          onClick={() => {
            setTab("add");
            setSearch("");
            setNotice("");
          }}
        >
          + Add Part
        </button>
      </div>

      {error && (
        <div
          role="alert"
          style={{
            ...css.message,
            background: "#fef2f2",
            color: "#991b1b",
            border: "1px solid #fecaca",
            borderRadius: 8,
            marginBottom: 15,
          }}
        >
          {error}
        </div>
      )}

      {notice && (
        <div
          role="status"
          style={{
            ...css.message,
            background: "#f0fdf4",
            color: "#166534",
            border: "1px solid #bbf7d0",
            borderRadius: 8,
            marginBottom: 15,
          }}
        >
          {notice}
        </div>
      )}

      {tab === "add" ? (
        <div style={{ ...css.panel, padding: 22, maxWidth: 700 }}>
          <h2 style={{ marginTop: 0, fontSize: 19 }}>Add Part Master Record</h2>
          <p style={{ color: "#6b7280", fontSize: 13 }}>
            Category ID backend ke existing product category record se lena.
          </p>

          <form onSubmit={createPart}>
            <div style={css.field}>
              <label style={css.fieldLabel} htmlFor="part_code">Part Code *</label>
              <input
                id="part_code"
                name="part_code"
                style={css.input}
                value={form.part_code}
                onChange={changeForm}
                required
              />
            </div>

            <div style={css.field}>
              <label style={css.fieldLabel} htmlFor="part_name">Part Name *</label>
              <input
                id="part_name"
                name="part_name"
                style={css.input}
                value={form.part_name}
                onChange={changeForm}
                required
              />
            </div>

            <div style={css.field}>
              <label style={css.fieldLabel} htmlFor="category_id">Category ID *</label>
              <input
                id="category_id"
                name="category_id"
                type="number"
                min="1"
                style={css.input}
                value={form.category_id}
                onChange={changeForm}
                required
              />
            </div>

            <div style={css.field}>
              <label style={css.fieldLabel} htmlFor="brand_id">Brand ID (optional)</label>
              <input
                id="brand_id"
                name="brand_id"
                type="number"
                min="1"
                style={css.input}
                value={form.brand_id}
                onChange={changeForm}
              />
            </div>

            <div style={css.field}>
              <label style={css.fieldLabel} htmlFor="product_type_id">
                Product Type ID (optional)
              </label>
              <input
                id="product_type_id"
                name="product_type_id"
                type="number"
                min="1"
                style={css.input}
                value={form.product_type_id}
                onChange={changeForm}
              />
            </div>

            <div style={css.field}>
              <label style={css.fieldLabel} htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                style={{ ...css.input, minHeight: 85, resize: "vertical" }}
                value={form.description}
                onChange={changeForm}
              />
            </div>

            <button type="submit" style={css.button} disabled={saving}>
              {saving ? "Saving..." : "Save Part"}
            </button>
          </form>
        </div>
      ) : (
        <>
          <div style={css.toolbar}>
            <input
              style={css.input}
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder={
                tab === "parts"
                  ? "Search part code, name, category..."
                  : "Search complaint, part, requirement status..."
              }
              aria-label="Search records"
            />
            <button
              type="button"
              style={css.button}
              onClick={loadData}
              disabled={loading}
            >
              {loading ? "Loading..." : "Refresh"}
            </button>
          </div>

          <div style={css.panel}>
            {loading ? (
              <div style={css.message}>Loading records...</div>
            ) : tab === "parts" ? (
              visibleParts.length === 0 ? (
                <div style={css.message}>No part master records found.</div>
              ) : (
                <div style={css.wrap}>
                  <table style={css.table}>
                    <thead>
                      <tr>
                        <th style={css.th}>Part Code</th>
                        <th style={css.th}>Part Name</th>
                        <th style={css.th}>Category</th>
                        <th style={css.th}>Brand</th>
                        <th style={css.th}>Product Type</th>
                        <th style={css.th}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {visibleParts.map((part, index) => (
                        <tr key={part.id ?? part.part_code ?? index}>
                          <td style={css.td}>{part.part_code || "—"}</td>
                          <td style={css.td}>
                            <strong>{part.part_name || "—"}</strong>
                            {part.description && (
                              <div style={{ color: "#6b7280", marginTop: 4 }}>
                                {part.description}
                              </div>
                            )}
                          </td>
                          <td style={css.td}>
                            {part.category_name || part.category_id || "—"}
                          </td>
                          <td style={css.td}>
                            {part.brand_name || part.brand_id || "—"}
                          </td>
                          <td style={css.td}>
                            {part.product_type_name || part.product_type_id || "—"}
                          </td>
                          <td style={css.td}>
                            <Status value={part.status} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            ) : visibleRequirements.length === 0 ? (
              <div style={css.message}>
                No part requirements found.
                <div style={{ color: "#6b7280", marginTop: 6 }}>
                  Requirement tabhi aayegi jab backend mein linked service-call
                  requirement record create hoga.
                </div>
              </div>
            ) : (
              <div style={css.wrap}>
                <table style={css.table}>
                  <thead>
                    <tr>
                      <th style={css.th}>Requirement</th>
                      <th style={css.th}>Complaint / Call</th>
                      <th style={css.th}>Part</th>
                      <th style={css.th}>Quantity</th>
                      <th style={css.th}>Reason</th>
                      <th style={css.th}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleRequirements.map((item, index) => (
                      <tr key={item.id ?? item.requirement_number ?? index}>
                        <td style={css.td}>
                          <strong>{item.requirement_number || `#${item.id ?? "—"}`}</strong>
                        </td>
                        <td style={css.td}>
                          {item.complaint_id || item.service_call_id || "—"}
                          <div style={{ color: "#6b7280", marginTop: 4 }}>
                            Visit ID: {item.visit_id ?? "—"}
                          </div>
                        </td>
                        <td style={css.td}>
                          <strong>{item.part_name || item.part?.part_name || "—"}</strong>
                          <div style={{ color: "#6b7280", marginTop: 4 }}>
                            {item.part_code || item.part?.part_code || ""}
                          </div>
                        </td>
                        <td style={css.td}>{item.quantity ?? "—"}</td>
                        <td style={css.td}>
                          {item.required_reason || item.remarks || "—"}
                        </td>
                        <td style={css.td}>
                          <Status value={item.status} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
