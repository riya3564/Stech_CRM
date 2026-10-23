
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Users, Search, RefreshCw, Eye, X, Plus, LoaderCircle,
} from "lucide-react";
import api from "../../services/api";

const initialForm = {
  engineer_code: "",
  engineer_name: "",
  asc_id: "",
  phone: "",
  alternate_phone: "",
  aadhaar_number: "",
  email: "",
  address: "",
  landmark: "",
  locality: "",
  city: "",
  district: "",
  state: "",
  pin_code: "",
  specialization: "",
  service_area: "",
  joining_date: "",
  status: "Active",
};

const page = {
  padding: "28px 4%",
  minHeight: "100%",
  background: "#f6f8fb",
  color: "#172b4d",
  fontFamily: "Inter, Segoe UI, Arial, sans-serif",
};
const card = {
  background: "#fff",
  border: "1px solid #e2e8f0",
  borderRadius: 10,
  padding: 18,
};
const btn = {
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
  fontWeight: 600,
};
const primary = { ...btn, background: "#175ce5", color: "#fff", borderColor: "#175ce5" };
const input = {
  width: "100%",
  boxSizing: "border-box",
  padding: "10px 11px",
  border: "1px solid #d6deea",
  borderRadius: 7,
  fontSize: 14,
  background: "#fff",
  color: "#172b4d",
};
const labelStyle = {
  display: "block",
  fontSize: 13,
  fontWeight: 650,
  marginBottom: 6,
  color: "#344761",
};
const overlay = {
  position: "fixed",
  inset: 0,
  zIndex: 1000,
  background: "rgba(15,28,48,.48)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 16,
};
const modal = {
  width: "min(920px, 100%)",
  maxHeight: "92vh",
  overflowY: "auto",
  background: "#fff",
  borderRadius: 12,
  boxShadow: "0 18px 60px rgba(0,0,0,.2)",
};

function arr(data) {
  if (Array.isArray(data)) return data;
  return data?.items || data?.results || data?.data || data?.engineers || [];
}

function Field({ label, name, form, setForm, required = false, type = "text", placeholder = "" }) {
  return (
    <label style={{ display: "block" }}>
      <span style={labelStyle}>
        {label}{required ? " *" : ""}
      </span>
      <input
        style={input}
        name={name}
        type={type}
        value={form[name] ?? ""}
        required={required}
        placeholder={placeholder}
        maxLength={name === "aadhaar_number" ? 12 : undefined}
        onChange={(e) => setForm((old) => ({ ...old, [name]: e.target.value }))}
      />
    </label>
  );
}

function Section({ title, children }) {
  return (
    <section style={{ marginBottom: 22 }}>
      <h3 style={{
        fontSize: 15, margin: "0 0 14px", paddingBottom: 9,
        borderBottom: "1px solid #e8edf4", color: "#172b4d",
      }}>
        {title}
      </h3>
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
        gap: 14,
      }}>
        {children}
      </div>
    </section>
  );
}

export default function Engineers() {
  const [engineers, setEngineers] = useState([]);
  const [ascs, setAscs] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [engineerResponse, ascResponse] = await Promise.all([
        api.get("/engineers"),
        api.get("/asc"),
      ]);
      setEngineers(arr(engineerResponse.data));
      setAscs(arr(ascResponse.data));
    } catch (e) {
      setError(
        e?.response?.data?.message ||
        "Engineers ya service centers load nahi hue. Backend aur API check karo."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const activeAscs = ascs.filter((asc) => asc.status === "Active");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return engineers;
    return engineers.filter((e) =>
      [
        e.engineer_code, e.engineer_name, e.phone, e.email,
        e.specialization, e.asc_name, e.city, e.service_area,
      ].some((value) => String(value ?? "").toLowerCase().includes(q))
    );
  }, [engineers, search]);

  function openAddForm() {
    setError("");
    setSuccess("");
    setForm(initialForm);
    setShowForm(true);
  }

  async function saveEngineer(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!form.engineer_code.trim() || !form.engineer_name.trim() || !form.asc_id) {
      setError("Engineer Code, Engineer Name aur Service Center mandatory hain.");
      return;
    }
    if (!/^\d{10,15}$/.test(form.phone.replace(/\D/g, ""))) {
      setError("Valid mobile number enter karo (10–15 digits).");
      return;
    }
    if (form.alternate_phone && !/^\d{10,15}$/.test(form.alternate_phone.replace(/\D/g, ""))) {
      setError("Alternate mobile number valid nahi hai.");
      return;
    }
    if (form.aadhaar_number && !/^\d{12}$/.test(form.aadhaar_number)) {
      setError("Aadhaar number exactly 12 digits ka hona chahiye.");
      return;
    }
    if (form.pin_code && !/^\d{6}$/.test(form.pin_code)) {
      setError("PIN code exactly 6 digits ka hona chahiye.");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        ...form,
        engineer_code: form.engineer_code.trim(),
        engineer_name: form.engineer_name.trim(),
        asc_id: Number(form.asc_id),
        phone: form.phone.trim(),
        alternate_phone: form.alternate_phone.trim(),
        aadhaar_number: form.aadhaar_number.trim(),
        email: form.email.trim(),
        pin_code: form.pin_code.trim(),
      };

      const response = await api.post("/engineers", payload);
      setSuccess(response.data?.message || "Engineer successfully add ho gaya.");
      setShowForm(false);
      setForm(initialForm);
      await loadData();
    } catch (e) {
      setError(
        e?.response?.data?.message ||
        (e?.response?.data?.missing_fields
          ? `Missing fields: ${e.response.data.missing_fields.join(", ")}`
          : "Engineer save nahi hua. Backend error check karo.")
      );
    } finally {
      setSaving(false);
    }
  }

  const activeCount = engineers.filter((e) => e.status === "Active").length;

  return (
    <div style={page}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        flexWrap: "wrap", gap: 14, marginBottom: 24,
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 28, fontWeight: 750 }}>Engineers</h1>
          <p style={{ margin: "8px 0 0", color: "#65758b", fontSize: 14 }}>
            Engineer records, contact details aur service center manage karo.
          </p>
        </div>
        <div style={{ display: "flex", gap: 9, flexWrap: "wrap" }}>
          <button type="button" style={btn} onClick={loadData}>
            <RefreshCw size={16} /> Refresh
          </button>
          <button type="button" style={primary} onClick={openAddForm}>
            <Plus size={17} /> Add Engineer
          </button>
        </div>
      </div>

      {error && !showForm && (
        <div role="alert" style={{
          background: "#fff1f2", color: "#b42318", padding: 12,
          borderRadius: 8, marginBottom: 14,
        }}>{error}</div>
      )}
      {success && (
        <div role="status" style={{
          background: "#ecfdf3", color: "#067647", padding: 12,
          borderRadius: 8, marginBottom: 14,
        }}>{success}</div>
      )}

      <div style={{
        display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))",
        gap: 14, marginBottom: 18,
      }}>
        <div style={card}>
          <Users size={20} color="#175ce5" />
          <div style={{ marginTop: 12, color: "#65758b", fontSize: 13 }}>Total Engineers</div>
          <div style={{ fontSize: 28, fontWeight: 750, marginTop: 5 }}>
            {loading ? "—" : engineers.length}
          </div>
        </div>
        <div style={card}>
          <Users size={20} color="#16a34a" />
          <div style={{ marginTop: 12, color: "#65758b", fontSize: 13 }}>Active Engineers</div>
          <div style={{ fontSize: 28, fontWeight: 750, marginTop: 5 }}>
            {loading ? "—" : activeCount}
          </div>
        </div>
        <div style={card}>
          <Users size={20} color="#64748b" />
          <div style={{ marginTop: 12, color: "#65758b", fontSize: 13 }}>Service Centers</div>
          <div style={{ fontSize: 28, fontWeight: 750, marginTop: 5 }}>
            {loading ? "—" : activeAscs.length}
          </div>
        </div>
      </div>

      <div style={{
        display: "flex", alignItems: "center", gap: 10, background: "#fff",
        border: "1px solid #e2e8f0", borderRadius: 9, padding: "6px 12px",
        marginBottom: 14,
      }}>
        <Search size={18} color="#8797ad" />
        <input
          style={{ ...input, border: 0, outline: 0 }}
          placeholder="Search by engineer, code, phone, email, skill or ASC..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {search && <button style={btn} onClick={() => setSearch("")} type="button">Clear</button>}
      </div>

      <div style={{ color: "#64748b", fontSize: 13, marginBottom: 10 }}>
        Showing {filtered.length} of {engineers.length} engineers
      </div>

      <div style={{ overflowX: "auto", background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10 }}>
        <table style={{ width: "100%", minWidth: 800, borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {["ENGINEER", "CODE", "MOBILE", "SERVICE CENTER", "SKILLS", "STATUS", "ACTION"].map((heading) => (
                <th key={heading} style={{
                  textAlign: "left", padding: "14px 15px", background: "#f8fafc",
                  color: "#62748b", fontSize: 12, borderBottom: "1px solid #e5eaf1",
                  whiteSpace: "nowrap",
                }}>{heading}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} style={{ padding: 32, textAlign: "center" }}>
                <LoaderCircle size={17} /> Loading engineers...
              </td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={7} style={{ padding: 32, textAlign: "center", color: "#64748b" }}>
                {error ? "Data load nahi hua. Error message upar dekho." : "Koi engineer nahi mila."}
              </td></tr>
            ) : filtered.map((e) => (
              <tr key={e.id}>
                {[null].map((_, index) => (
                  <td key={index} style={{ padding: 14, borderBottom: "1px solid #edf0f5" }}>
                    <strong>{e.engineer_name}</strong>
                    <div style={{ fontSize: 12, color: "#71839b", marginTop: 4 }}>{e.email || "No email"}</div>
                  </td>
                ))}
                <td style={{ padding: 14, borderBottom: "1px solid #edf0f5" }}>{e.engineer_code}</td>
                <td style={{ padding: 14, borderBottom: "1px solid #edf0f5" }}>{e.phone || "—"}</td>
                <td style={{ padding: 14, borderBottom: "1px solid #edf0f5" }}>{e.asc_name || "—"}</td>
                <td style={{ padding: 14, borderBottom: "1px solid #edf0f5" }}>{e.specialization || "—"}</td>
                <td style={{ padding: 14, borderBottom: "1px solid #edf0f5" }}>
                  <span style={{
                    padding: "5px 9px", borderRadius: 20, fontSize: 12, fontWeight: 650,
                    background: e.status === "Active" ? "#dcfce7" : "#fee2e2",
                    color: e.status === "Active" ? "#166534" : "#b91c1c",
                  }}>{e.status || "Active"}</span>
                </td>
                <td style={{ padding: 14, borderBottom: "1px solid #edf0f5" }}>
                  <button type="button" style={btn} onClick={() => setSelected(e)}>
                    <Eye size={15} /> Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div style={overlay} onMouseDown={(e) => {
          if (e.target === e.currentTarget && !saving) setShowForm(false);
        }}>
          <div style={modal} role="dialog" aria-modal="true" aria-label="Add Engineer form">
            <div style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              padding: "18px 22px", borderBottom: "1px solid #e7ebf2",
              position: "sticky", top: 0, background: "#fff", zIndex: 2,
            }}>
              <div>
                <h2 style={{ margin: 0, fontSize: 21 }}>Add Engineer</h2>
                <p style={{ margin: "5px 0 0", color: "#64748b", fontSize: 13 }}>
                  Engineer ki complete details fill karo.
                </p>
              </div>
              <button type="button" style={btn} disabled={saving} onClick={() => setShowForm(false)}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={saveEngineer} style={{ padding: 22 }}>
              {error && <div role="alert" style={{
                background: "#fff1f2", color: "#b42318", padding: 12,
                borderRadius: 8, marginBottom: 18, fontSize: 14,
              }}>{error}</div>}

              <Section title="Basic Information">
                <Field label="Engineer Code" name="engineer_code" form={form} setForm={setForm} required placeholder="e.g. ENG-001" />
                <Field label="Engineer Name" name="engineer_name" form={form} setForm={setForm} required placeholder="Full name" />
                <label>
                  <span style={labelStyle}>Service Center (ASC) *</span>
                  <select
                    style={input}
                    required
                    value={form.asc_id}
                    onChange={(e) => setForm((old) => ({ ...old, asc_id: e.target.value }))}
                  >
                    <option value="">Select active service center</option>
                    {activeAscs.map((asc) => (
                      <option key={asc.id} value={asc.id}>
                        {asc.asc_code} — {asc.asc_name}
                      </option>
                    ))}
                  </select>
                  {activeAscs.length === 0 && (
                    <small style={{ color: "#b42318" }}>
                      Active ASC nahi mila. Pehle Service Center add/activate karo.
                    </small>
                  )}
                </label>
                <label>
                  <span style={labelStyle}>Status</span>
                  <select
                    style={input}
                    value={form.status}
                    onChange={(e) => setForm((old) => ({ ...old, status: e.target.value }))}
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </label>
                <Field label="Joining Date" name="joining_date" type="date" form={form} setForm={setForm} />
                <Field label="Specialization / Skills" name="specialization" form={form} setForm={setForm} placeholder="Repair, installation..." />
                <Field label="Service Area" name="service_area" form={form} setForm={setForm} placeholder="Area / region" />
              </Section>

              <Section title="Contact Information">
                <Field label="Mobile Number" name="phone" form={form} setForm={setForm} required placeholder="10-digit mobile number" />
                <Field label="Alternate Mobile" name="alternate_phone" form={form} setForm={setForm} placeholder="Optional" />
                <Field label="Email Address" name="email" type="email" form={form} setForm={setForm} placeholder="engineer@example.com" />
                <Field label="Aadhaar Number" name="aadhaar_number" form={form} setForm={setForm} placeholder="12 digits (optional)" />
              </Section>

              <Section title="Address Information">
                <Field label="Address" name="address" form={form} setForm={setForm} />
                <Field label="Landmark" name="landmark" form={form} setForm={setForm} />
                <Field label="Locality" name="locality" form={form} setForm={setForm} />
                <Field label="City" name="city" form={form} setForm={setForm} />
                <Field label="District" name="district" form={form} setForm={setForm} />
                <Field label="State" name="state" form={form} setForm={setForm} />
                <Field label="PIN Code" name="pin_code" form={form} setForm={setForm} placeholder="6 digits" />
              </Section>

              <p style={{ fontSize: 12, color: "#7a5260", lineHeight: 1.5 }}>
                Aadhaar sensitive information hai. Sirf zaroorat hone par enter karo;
                is form se Aadhaar API response mein return nahi hota.
              </p>

              <div style={{
                display: "flex", justifyContent: "flex-end", gap: 10,
                paddingTop: 14, borderTop: "1px solid #e7ebf2",
              }}>
                <button type="button" style={btn} disabled={saving} onClick={() => setShowForm(false)}>
                  Cancel
                </button>
                <button type="submit" style={primary} disabled={saving || activeAscs.length === 0}>
                  {saving ? <LoaderCircle size={16} /> : <Plus size={16} />}
                  {saving ? "Saving..." : "Save Engineer"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {selected && (
        <div style={overlay} onMouseDown={(e) => {
          if (e.target === e.currentTarget) setSelected(null);
        }}>
          <div style={{ ...modal, maxWidth: 620 }}>
            <div style={{
              display: "flex", justifyContent: "space-between", alignItems: "center",
              padding: 20, borderBottom: "1px solid #e7ebf2",
            }}>
              <div>
                <h2 style={{ margin: 0, fontSize: 20 }}>Engineer Details</h2>
                <p style={{ margin: "5px 0 0", color: "#64748b" }}>{selected.engineer_name}</p>
              </div>
              <button type="button" style={btn} onClick={() => setSelected(null)}><X size={18} /></button>
            </div>
            <div style={{ padding: 22 }}>
              {[
                ["Engineer Code", selected.engineer_code],
                ["Name", selected.engineer_name],
                ["Service Center", selected.asc_name],
                ["Mobile", selected.phone],
                ["Alternate Mobile", selected.alternate_phone],
                ["Email", selected.email],
                ["Address", selected.address],
                ["Landmark", selected.landmark],
                ["Locality", selected.locality],
                ["City", selected.city],
                ["District", selected.district],
                ["State", selected.state],
                ["PIN Code", selected.pin_code],
                ["Specialization", selected.specialization],
                ["Service Area", selected.service_area],
                ["Joining Date", selected.joining_date],
                ["Status", selected.status],
              ].map(([label, value]) => (
                <div key={label} style={{
                  display: "grid", gridTemplateColumns: "150px minmax(0,1fr)",
                  gap: 12, padding: "10px 0", borderBottom: "1px solid #edf0f5",
                  fontSize: 14,
                }}>
                  <span style={{ color: "#65758b", fontWeight: 600 }}>{label}</span>
                  <span style={{ overflowWrap: "anywhere" }}>{value || "—"}</span>
                </div>
              ))}
              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 18 }}>
                <button type="button" style={btn} onClick={() => setSelected(null)}>Close</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
