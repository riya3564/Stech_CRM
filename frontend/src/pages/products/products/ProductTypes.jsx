import { useEffect, useState } from "react";
import {
Plus,
Search,
RefreshCw,
Pencil,
X,
Layers3,
} from "lucide-react";
import api from "../../services/api";

const EMPTY_FORM = {
name: "",
code: "",
category_id: "",
status: "Active",
};

function getRows(response) {
const data = response?.data ?? response;

if (Array.isArray(data)) return data;
if (Array.isArray(data?.items)) return data.items;
if (Array.isArray(data?.product_types)) return data.product_types;
if (Array.isArray(data?.types)) return data.types;
if (Array.isArray(data?.data)) return data.data;
if (Array.isArray(data?.results)) return data.results;

return [];
}

function getId(item) {
return item?.id ?? item?.product_type_id ?? item?.type_id ?? "";
}

function getName(item) {
return (
item?.name ??
item?.product_type_name ??
item?.type_name ??
item?.title ??
""
);
}

function getCode(item) {
return item?.code ?? item?.product_type_code ?? item?.type_code ?? "";
}

function getCategoryId(item) {
return (
item?.category_id ??
item?.product_category_id ??
item?.category?.id ??
""
);
}

function getCategoryName(item, categories) {
const directName =
item?.category_name ??
item?.product_category_name ??
item?.category?.name;

if (directName) return directName;

const category = categories.find(
(entry) => String(getId(entry)) === String(getCategoryId(item))
);

return category ? getName(category) : "—";
}

function getStatus(item) {
if (item?.status) return item.status;

if (item?.is_active !== undefined) {
return item.is_active ? "Active" : "Inactive";
}

if (item?.active !== undefined) {
return item.active ? "Active" : "Inactive";
}

return "Active";
}

function ProductTypes() {
const [types, setTypes] = useState([]);
const [categories, setCategories] = useState([]);
const [form, setForm] = useState(EMPTY_FORM);
const [search, setSearch] = useState("");
const [loading, setLoading] = useState(true);
const [saving, setSaving] = useState(false);
const [error, setError] = useState("");
const [modalOpen, setModalOpen] = useState(false);
const [editingType, setEditingType] = useState(null);

const loadData = async () => {
setLoading(true);
setError("");

try {
  const [typeResponse, categoryResponse] = await Promise.all([
    api.get("/product-types"),
    api.get("/product-categories"),
  ]);

  setTypes(getRows(typeResponse));
  setCategories(getRows(categoryResponse));
} catch (err) {
  console.error("Product types loading error:", err);
  setError(
    err.response?.data?.message ||
      err.response?.data?.msg ||
      "Unable to load product types or categories."
  );
} finally {
  setLoading(false);
}

};

useEffect(() => {
loadData();
}, []);

const filteredTypes = types.filter((item) => {
const term = search.trim().toLowerCase();

if (!term) return true;

return [
  getName(item),
  getCode(item),
  getCategoryName(item, categories),
  getStatus(item),
].some((value) => String(value).toLowerCase().includes(term));

});

const openAddModal = () => {
setEditingType(null);
setForm(EMPTY_FORM);
setError("");
setModalOpen(true);
};

const openEditModal = (item) => {
setEditingType(item);
setForm({
name: getName(item),
code: getCode(item),
category_id: String(getCategoryId(item) || ""),
status: getStatus(item),
});
setError("");
setModalOpen(true);
};

const closeModal = () => {
if (saving) return;

setModalOpen(false);
setEditingType(null);
setForm(EMPTY_FORM);
setError("");

};

const handleChange = (event) => {
const { name, value } = event.target;

setForm((previous) => ({
  ...previous,
  [name]: value,
}));

};

const handleSubmit = async (event) => {
event.preventDefault();

if (!form.name.trim()) {
  setError("Product type name is required.");
  return;
}

if (!form.category_id) {
  setError("Please select a product category.");
  return;
}

setSaving(true);
setError("");

const payload = {
  name: form.name.trim(),
  code: form.code.trim(),
  category_id: Number(form.category_id),
  status: form.status,
};

try {
  if (editingType) {
    const id = getId(editingType);

    if (!id) {
      throw new Error("Product type ID is missing; cannot update.");
    }

    await api.put(`/product-types/${id}`, payload);
  } else {
    await api.post("/product-types", payload);
  }

  setModalOpen(false);
  setEditingType(null);
  setForm(EMPTY_FORM);

  await loadData();
} catch (err) {
  console.error("Product type save error:", err);
  setError(
    err.response?.data?.message ||
      err.response?.data?.msg ||
      err.message ||
      "Unable to save product type. Please check the backend API."
  );
} finally {
  setSaving(false);
}

};

return (
<div className="space-y-6">
<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
<div>
<div className="flex items-center gap-2">
<Layers3 size={24} className="text-teal-700" />
<h1 className="text-2xl font-bold text-slate-900">
Product Types
</h1>
</div>
<p className="mt-1 text-sm text-slate-500">
Manage product types linked to product categories.
</p>
</div>

    <button
      type="button"
      onClick={openAddModal}
      className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#173b67] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#102e52]"
    >
      <Plus size={18} />
      Add Product Type
    </button>
  </div>

  <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="relative w-full sm:max-w-md">
        <Search
          size={17}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
        />
        <input
          type="text"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search product types..."
          className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm outline-none focus:border-[#173b67] focus:bg-white"
        />
      </div>

      <button
        type="button"
        onClick={loadData}
        disabled={loading}
        className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-50"
      >
        <RefreshCw
          size={16}
          className={loading ? "animate-spin" : ""}
        />
        Refresh
      </button>
    </div>
  </div>

  {error && !modalOpen && (
    <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {error}
    </div>
  )}

  <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] text-left">
        <thead className="border-b border-slate-200 bg-slate-50">
          <tr>
            <th className="px-5 py-4 text-xs font-semibold uppercase text-slate-500">
              Product Type
            </th>
            <th className="px-5 py-4 text-xs font-semibold uppercase text-slate-500">
              Code
            </th>
            <th className="px-5 py-4 text-xs font-semibold uppercase text-slate-500">
              Category
            </th>
            <th className="px-5 py-4 text-xs font-semibold uppercase text-slate-500">
              Status
            </th>
            <th className="px-5 py-4 text-right text-xs font-semibold uppercase text-slate-500">
              Action
            </th>
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-100">
          {loading && (
            <tr>
              <td colSpan={5} className="px-5 py-12 text-center text-sm text-slate-500">
                Loading product types...
              </td>
            </tr>
          )}

          {!loading && filteredTypes.length === 0 && (
            <tr>
              <td colSpan={5} className="px-5 py-12 text-center text-sm text-slate-500">
                No product types found.
              </td>
            </tr>
          )}

          {!loading &&
            filteredTypes.map((item, index) => {
              const name = getName(item);
              const status = getStatus(item);

              return (
                <tr
                  key={getId(item) || `${name}-${index}`}
                  className="hover:bg-slate-50/70"
                >
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50 font-bold text-teal-700">
                        {(name || "T").charAt(0).toUpperCase()}
                      </div>
                      <span className="font-semibold text-slate-800">
                        {name || "—"}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-sm text-slate-600">
                    {getCode(item) || "—"}
                  </td>
                  <td className="px-5 py-4 text-sm text-slate-600">
                    {getCategoryName(item, categories)}
                  </td>
                  <td className="px-5 py-4">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
                        status.toLowerCase() === "active"
                          ? "bg-emerald-50 text-emerald-700"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {status}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-right">
                    <button
                      type="button"
                      onClick={() => openEditModal(item)}
                      className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-[#173b67] hover:bg-[#eaf2fb]"
                    >
                      <Pencil size={15} />
                      Edit
                    </button>
                  </td>
                </tr>
              );
            })}
        </tbody>
      </table>
    </div>

    <div className="border-t border-slate-100 px-5 py-3 text-xs text-slate-400">
      Showing {filteredTypes.length} of {types.length} product types
    </div>
  </div>

  {modalOpen && (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4 py-6">
      <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white shadow-2xl">
        <div className="sticky top-0 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              {editingType ? "Edit Product Type" : "Add Product Type"}
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Link the type to its product category.
            </p>
          </div>
          <button
            type="button"
            onClick={closeModal}
            disabled={saving}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
            aria-label="Close"
          >
            <X size={19} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Product Category *
              </label>
              <select
                name="category_id"
                value={form.category_id}
                onChange={handleChange}
                required
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none focus:border-[#173b67]"
              >
                <option value="">Select category</option>
                {categories.map((category, index) => (
                  <option
                    key={getId(category) || index}
                    value={getId(category)}
                  >
                    {getName(category)}
                  </option>
                ))}
              </select>
              {categories.length === 0 && (
                <p className="mt-1 text-xs text-amber-700">
                  No categories loaded. Check that Product Categories API is working.
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Product Type Name *
              </label>
              <input
                name="name"
                value={form.name}
                onChange={handleChange}
                required
                placeholder="e.g. LED TV"
                className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-[#173b67]"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Product Type Code
              </label>
              <input
                name="code"
                value={form.code}
                onChange={handleChange}
                placeholder="e.g. LED-TV"
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
          </div>

          <div className="mt-7 flex justify-end gap-3 border-t border-slate-100 pt-5">
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
              disabled={saving || categories.length === 0}
              className="rounded-xl bg-[#173b67] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#102e52] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saving
                ? "Saving..."
                : editingType
                ? "Update Product Type"
                : "Create Product Type"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )}
</div>

);
}
export default ProductTypes;