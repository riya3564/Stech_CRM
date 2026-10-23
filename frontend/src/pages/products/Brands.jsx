import { useEffect, useState } from "react";
import { Plus, Search, RefreshCw, X } from "lucide-react";
import api from "../../services/api";

const EMPTY_FORM = {
brand_name: "",
brand_code: "",
description: "",
status: "Active",
};

function Brands() {
const [brands, setBrands] = useState([]);
const [form, setForm] = useState(EMPTY_FORM);
const [search, setSearch] = useState("");
const [loading, setLoading] = useState(true);
const [saving, setSaving] = useState(false);
const [modalOpen, setModalOpen] = useState(false);
const [error, setError] = useState("");
const [success, setSuccess] = useState("");

async function loadBrands() {
setLoading(true);
setError("");

try {
  const response = await api.get("/brands");
  const data = response.data;

  setBrands(
    Array.isArray(data)
      ? data
      : Array.isArray(data?.brands)
      ? data.brands
      : Array.isArray(data?.data)
      ? data.data
      : []
  );
} catch (err) {
  setError(
    err.response?.data?.message ||
      "Unable to load brands. Please check login and backend."
  );
} finally {
  setLoading(false);
}

}

useEffect(() => {
loadBrands();
}, []);

function openAddModal() {
setForm(EMPTY_FORM);
setError("");
setSuccess("");
setModalOpen(true);
}

function closeModal() {
if (saving) return;
setModalOpen(false);
setForm(EMPTY_FORM);
setError("");
}

function handleChange(event) {
const { name, value } = event.target;
setForm((previous) => ({ ...previous, [name]: value }));
}

async function handleSubmit(event) {
event.preventDefault();
setError("");
setSuccess("");

const brand_name = form.brand_name.trim();
const brand_code = form.brand_code.trim();

if (!brand_name || !brand_code) {
  setError("Brand Name and Brand Code are both required.");
  return;
}

try {
  setSaving(true);

  const payload = {
    brand_name,
    brand_code,
    description: form.description.trim(),
    status: form.status,
  };

  const response = await api.post("/brands", payload);

  setModalOpen(false);
  setForm(EMPTY_FORM);
  setSuccess(
    response.data?.message || "Brand created successfully."
  );

  await loadBrands();
} catch (err) {
  setError(
    err.response?.data?.message ||
      err.response?.data?.msg ||
      (err.response?.status === 403
        ? "Only Super Admin can create brands. Please check your account role."
        : "Unable to save brand. Please try again.")
  );
} finally {
  setSaving(false);
}

}

const filteredBrands = brands.filter((brand) => {
const query = search.trim().toLowerCase();

return (
  !query ||
  [
    brand.brand_name,
    brand.brand_code,
    brand.description,
    brand.status,
  ].some((value) =>
    String(value || "").toLowerCase().includes(query)
  )
);

});

return (
<div className="space-y-6">
<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
<div>
<h1 className="text-2xl font-bold text-slate-900">Brands</h1>
<p className="mt-1 text-sm text-slate-500">
Manage product brand master data.
</p>
</div>

    <button
      type="button"
      onClick={openAddModal}
      className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#173b67] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#102e52]"
    >
      <Plus size={18} /> Add Brand
    </button>
  </div>

  {success && (
    <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
      {success}
    </div>
  )}

  {error && !modalOpen && (
    <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {error}
    </div>
  )}

  <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row">
    <div className="relative flex-1">
      <Search
        size={17}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
      />
      <input
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder="Search by brand name or code..."
        className="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm outline-none focus:border-[#173b67]"
      />
    </div>

    <button
      type="button"
      onClick={loadBrands}
      disabled={loading}
      className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
    >
      <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
      Refresh
    </button>
  </div>

  <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
    <div className="overflow-x-auto">
      <table className="w-full min-w-[650px] text-left">
        <thead className="border-b bg-slate-50">
          <tr>
            {["Brand Name", "Brand Code", "Description", "Status"].map(
              (heading) => (
                <th
                  key={heading}
                  className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  {heading}
                </th>
              )
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {loading ? (
            <tr>
              <td colSpan={4} className="px-5 py-12 text-center text-sm text-slate-500">
                Loading brands...
              </td>
            </tr>
          ) : filteredBrands.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-5 py-12 text-center text-sm text-slate-500">
                No brands found.
              </td>
            </tr>
          ) : (
            filteredBrands.map((brand) => (
              <tr key={brand.id} className="hover:bg-slate-50">
                <td className="px-5 py-4 text-sm font-semibold text-slate-800">
                  {brand.brand_name || "—"}
                </td>
                <td className="px-5 py-4 text-sm text-slate-600">
                  {brand.brand_code || "—"}
                </td>
                <td className="px-5 py-4 text-sm text-slate-600">
                  {brand.description || "—"}
                </td>
                <td className="px-5 py-4">
                  <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                    {brand.status || "Active"}
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>

    <div className="border-t border-slate-100 px-5 py-3 text-xs text-slate-500">
      Showing {filteredBrands.length} of {brands.length} brands
    </div>
  </div>

  {modalOpen && (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 px-4 py-6">
      <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Add Brand</h2>
            <p className="mt-1 text-xs text-slate-500">
              Enter the brand details below.
            </p>
          </div>
          <button
            type="button"
            onClick={closeModal}
            disabled={saving}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
          >
            <X size={19} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 p-6">
          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Brand Name *
            </label>
            <input
              name="brand_name"
              value={form.brand_name}
              onChange={handleChange}
              required
              placeholder="e.g. Samsung"
              className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-[#173b67]"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Brand Code *
            </label>
            <input
              name="brand_code"
              value={form.brand_code}
              onChange={handleChange}
              required
              placeholder="e.g. SAM"
              className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-[#173b67]"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Description
            </label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              rows={3}
              placeholder="Optional description"
              className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-[#173b67]"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Status
            </label>
            <select
              name="status"
              value={form.status}
              onChange={handleChange}
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none focus:border-[#173b67]"
            >
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 border-t pt-5">
            <button
              type="button"
              onClick={closeModal}
              disabled={saving}
              className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-xl bg-[#173b67] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#102e52] disabled:opacity-60"
            >
              {saving ? "Saving..." : "Save Brand"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )}
</div>

);
}

export default Brands;