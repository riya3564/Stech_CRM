import { useEffect, useState } from "react";
import {
  Pencil,
  Plus,
  RefreshCw,
  Search,
  X,
} from "lucide-react";
import api from "../../services/api";

const EMPTY_FORM = {
  name: "",
  code: "",
  status: "Active",
};

function getName(item) {
  return (
    item.name ||
    item.category_name ||
    item.categoryName ||
    item.title ||
    ""
  );
}

function getCode(item) {
  return (
    item.code ||
    item.category_code ||
    item.categoryCode ||
    ""
  );
}

function getStatus(item) {
  if (item.status) return item.status;

  if (item.is_active !== undefined) {
    return item.is_active ? "Active" : "Inactive";
  }

  return "Active";
}

export default function ProductCategories() {
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const loadCategories = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/product-categories");

      const data = response.data;

      if (Array.isArray(data)) {
        setCategories(data);
      } else if (Array.isArray(data?.categories)) {
        setCategories(data.categories);
      } else if (Array.isArray(data?.data)) {
        setCategories(data.data);
      } else {
        setCategories([]);
      }
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.message ||
          err.response?.data?.msg ||
          "Unable to load product categories."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  const filtered = categories.filter((item) => {
    const value = search.trim().toLowerCase();

    if (!value) return true;

    return [
      getName(item),
      getCode(item),
      getStatus(item),
    ]
      .filter(Boolean)
      .some((field) =>
        String(field).toLowerCase().includes(value)
      );
  });

  const openAdd = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setError("");
    setModalOpen(true);
  };

  const openEdit = (item) => {
    setEditing(item);

    setForm({
      name: getName(item),
      code: getCode(item),
      status: getStatus(item),
    });

    setError("");
    setModalOpen(true);
  };

  const closeModal = () => {
    if (saving) return;

    setModalOpen(false);
    setEditing(null);
    setForm(EMPTY_FORM);
    setError("");
  };

  const handleChange = (event) => {
    setForm((previous) => ({
      ...previous,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!form.name.trim()) {
      setError("Category name is required.");
      return;
    }

    try {
      setSaving(true);
      setError("");

      const payload = {
        name: form.name.trim(),
        code: form.code.trim(),
        status: form.status,
      };

      if (editing) {
        await api.put(
          `/product-categories/${editing.id}`,
          payload
        );
      } else {
        await api.post(
          "/product-categories",
          payload
        );
      }

      closeModal();
      await loadCategories();
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.message ||
          err.response?.data?.msg ||
          "Unable to save category."
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Product Categories
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Manage product categories
          </p>
        </div>

        <button
          onClick={openAdd}
          className="inline-flex items-center gap-2 rounded-xl bg-[#173b67] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#102e52]"
        >
          <Plus size={18} />
          Add Category
        </button>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
          <div className="relative w-full sm:max-w-md">
            <Search
              size={17}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />

            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search categories..."
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm outline-none focus:border-[#173b67]"
            />
          </div>

          <button
            onClick={loadCategories}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50"
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
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          {error}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-left">
          <thead className="border-b border-slate-200 bg-slate-50">
            <tr>
              <th className="px-5 py-4 text-xs font-semibold uppercase text-slate-500">
                Category
              </th>

              <th className="px-5 py-4 text-xs font-semibold uppercase text-slate-500">
                Code
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
            {loading ? (
              <tr>
                <td
                  colSpan="4"
                  className="px-5 py-12 text-center text-sm text-slate-500"
                >
                  Loading categories...
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td
                  colSpan="4"
                  className="px-5 py-12 text-center text-sm text-slate-500"
                >
                  No categories found.
                </td>
              </tr>
            ) : (
              filtered.map((item) => {
                const name = getName(item);
                const code = getCode(item);
                const status = getStatus(item);

                return (
                  <tr
                    key={item.id}
                    className="hover:bg-slate-50"
                  >
                    <td className="px-5 py-4 font-semibold text-slate-800">
                      {name || "—"}
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-600">
                      {code || "—"}
                    </td>

                    <td className="px-5 py-4">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                          status === "Active"
                            ? "bg-emerald-50 text-emerald-700"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {status}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-right">
                      <button
                        onClick={() => openEdit(item)}
                        className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#173b67] hover:bg-[#eaf2fb]"
                      >
                        <Pencil size={15} />
                        Edit
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        <div className="border-t border-slate-100 px-5 py-3 text-xs text-slate-400">
          Showing {filtered.length} of {categories.length} categories
        </div>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
          <div className="w-full max-w-lg rounded-2xl bg-white shadow-2xl">

            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900">
                  {editing ? "Edit Category" : "Add Category"}
                </h2>
              </div>

              <button onClick={closeModal}>
                <X size={19} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6">

              {error && (
                <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                  {error}
                </div>
              )}

              <div className="space-y-5">

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Category Name *
                  </label>

                  <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    required
                    placeholder="Television"
                    className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-[#173b67]"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Category Code
                  </label>

                  <input
                    name="code"
                    value={form.code}
                    onChange={handleChange}
                    placeholder="TV"
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
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none"
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>

              </div>

              <div className="mt-7 flex justify-end gap-3 border-t pt-5">
                <button
                  type="button"
                  onClick={closeModal}
                  className="rounded-xl border px-5 py-2.5 text-sm text-slate-600"
                >
                  Cancel
                </button>

                <button
                  disabled={saving}
                  className="rounded-xl bg-[#173b67] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                >
                  {saving
                    ? "Saving..."
                    : editing
                    ? "Update Category"
                    : "Create Category"}
                </button>
              </div>

            </form>
          </div>
        </div>
      )}
    </div>
  );
}