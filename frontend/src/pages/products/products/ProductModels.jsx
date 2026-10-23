import { useEffect, useMemo, useState } from "react";
import {
  Plus,
  Search,
  RefreshCw,
  Pencil,
  X,
  Package,
  AlertCircle,
  CheckCircle2,
  LoaderCircle,
} from "lucide-react";
import api from "../../services/api";

const emptyForm = {
  name: "",
  code: "",
  brand_id: "",
  category_id: "",
  product_type_id: "",
  status: "Active",
};

const getRows = (response) => {
  const body = response?.data ?? response;

  if (Array.isArray(body)) return body;
  if (Array.isArray(body?.items)) return body.items;
  if (Array.isArray(body?.data)) return body.data;
  if (Array.isArray(body?.results)) return body.results;
  if (Array.isArray(body?.value)) return body.value;

  return [];
};

const getId = (item) =>
  item?.id ?? item?.product_model_id ?? item?.model_id ?? "";

const getName = (item) =>
  item?.name ??
  item?.model_name ??
  item?.brand_name ??
  item?.category_name ??
  item?.product_type_name ??
  item?.title ??
  "";

const getErrorMessage = (error) =>
  error?.response?.data?.message ||
  error?.response?.data?.error ||
  error?.message ||
  "Something went wrong. Please try again.";

const styles = {
  page: {
    padding: "24px",
    minHeight: "100%",
    background: "#f7f9fc",
    color: "#172033",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "14px",
    marginBottom: "22px",
  },
  title: {
    fontSize: "26px",
    fontWeight: 750,
    margin: "0 0 6px",
  },
  subtitle: {
    color: "#697586",
    fontSize: "13px",
    margin: 0,
  },
  button: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "7px",
    padding: "10px 13px",
    border: "1px solid #dce3ed",
    borderRadius: "8px",
    background: "#fff",
    color: "#344054",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
  },
  primary: {
    background: "#2563eb",
    borderColor: "#2563eb",
    color: "#fff",
  },
  card: {
    background: "#fff",
    border: "1px solid #e5eaf1",
    borderRadius: "12px",
    overflow: "hidden",
    marginBottom: "18px",
  },
  input: {
    boxSizing: "border-box",
    width: "100%",
    padding: "10px 12px",
    border: "1px solid #d7dfeb",
    borderRadius: "8px",
    background: "#fff",
    color: "#172033",
    fontSize: "13px",
  },
  label: {
    display: "block",
    marginBottom: "7px",
    fontSize: "13px",
    fontWeight: 650,
  },
  th: {
    padding: "13px 15px",
    background: "#f8fafc",
    color: "#667085",
    textAlign: "left",
    fontSize: "11px",
    textTransform: "uppercase",
    borderBottom: "1px solid #e9edf3",
    whiteSpace: "nowrap",
  },
  td: {
    padding: "14px 15px",
    borderBottom: "1px solid #eef1f5",
    fontSize: "13px",
    verticalAlign: "middle",
  },
  overlay: {
    position: "fixed",
    inset: 0,
    zIndex: 1000,
    background: "rgba(15,23,42,0.45)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "16px",
  },
  modal: {
    width: "100%",
    maxWidth: "650px",
    maxHeight: "90vh",
    overflowY: "auto",
    background: "#fff",
    borderRadius: "14px",
  },
};

export default function ProductModels() {
  const [models, setModels] = useState([]);
  const [brands, setBrands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [types, setTypes] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [pageError, setPageError] = useState("");
  const [notice, setNotice] = useState("");
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({ ...emptyForm });
  const [brandFilter, setBrandFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const loadData = async () => {
    setLoading(true);
    setPageError("");

    const results = await Promise.allSettled([
      api.get("/product-models"),
      api.get("/brands"),
      api.get("/product-categories"),
      api.get("/product-types"),
    ]);

    const labels = [
      "Product Models",
      "Brands",
      "Product Categories",
      "Product Types",
    ];

    const setters = [
      setModels,
      setBrands,
      setCategories,
      setTypes,
    ];

    const errors = [];

    results.forEach((result, index) => {
      if (result.status === "fulfilled") {
        setters[index](getRows(result.value));
      } else {
        errors.push(
          `${labels[index]}: ${getErrorMessage(result.reason)}`
        );
      }
    });

    if (errors.length) {
      setPageError(errors.join(" | "));
    }

    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const brandMap = useMemo(
    () =>
      new Map(
        brands.map((item) => [String(getId(item)), getName(item)])
      ),
    [brands]
  );

  const categoryMap = useMemo(
    () =>
      new Map(
        categories.map((item) => [
          String(getId(item)),
          getName(item),
        ])
      ),
    [categories]
  );

  const typeMap = useMemo(
    () =>
      new Map(
        types.map((item) => [String(getId(item)), getName(item)])
      ),
    [types]
  );

  const filteredTypes = useMemo(() => {
    if (!form.category_id) return types;

    return types.filter((item) => {
      const categoryId =
        item.category_id ??
        item.product_category_id ??
        item.category?.id ??
        "";

      return String(categoryId) === String(form.category_id);
    });
  }, [types, form.category_id]);

  const filteredModels = useMemo(() => {
    const term = search.trim().toLowerCase();

    return models.filter((model) => {
      const name = getName(model).toLowerCase();
      const code = String(
        model.code ??
          model.model_code ??
          model.product_model_code ??
          ""
      ).toLowerCase();

      const brandId = model.brand_id ?? model.brand?.id ?? "";
      const categoryId =
        model.category_id ??
        model.product_category_id ??
        model.category?.id ??
        "";

      const brandName =
        model.brand_name ??
        model.brand?.name ??
        brandMap.get(String(brandId)) ??
        "";

      const categoryName =
        model.category_name ??
        model.category?.name ??
        categoryMap.get(String(categoryId)) ??
        "";

      const matchesSearch =
        !term ||
        name.includes(term) ||
        code.includes(term) ||
        brandName.toLowerCase().includes(term) ||
        categoryName.toLowerCase().includes(term);

      const matchesBrand =
        brandFilter === "all" ||
        String(brandId) === brandFilter;

      const matchesCategory =
        categoryFilter === "all" ||
        String(categoryId) === categoryFilter;

      return matchesSearch && matchesBrand && matchesCategory;
    });
  }, [
    models,
    search,
    brandFilter,
    categoryFilter,
    brandMap,
    categoryMap,
  ]);

  const updateForm = (field, value) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
      ...(field === "category_id" ? { product_type_id: "" } : {}),
    }));
  };

  const openCreate = () => {
    setEditingId(null);
    setForm({ ...emptyForm });
    setPageError("");
    setNotice("");
    setModalOpen(true);
  };

  const openEdit = (model) => {
    setEditingId(getId(model));

    setForm({
      name: getName(model),
      code:
        model.code ??
        model.model_code ??
        model.product_model_code ??
        "",
      brand_id: String(model.brand_id ?? model.brand?.id ?? ""),
      category_id: String(
        model.category_id ??
          model.product_category_id ??
          model.category?.id ??
          ""
      ),
      product_type_id: String(
        model.product_type_id ?? model.product_type?.id ?? ""
      ),
      status:
        model.status ??
        (model.is_active === false ? "Inactive" : "Active"),
    });

    setPageError("");
    setNotice("");
    setModalOpen(true);
  };

  const saveModel = async (event) => {
    event.preventDefault();
    setSaving(true);
    setPageError("");
    setNotice("");

    const payload = {
      name: form.name.trim(),
      code: form.code.trim(),
      brand_id: Number(form.brand_id),
      category_id: Number(form.category_id),
      product_type_id: Number(form.product_type_id),
      status: form.status,
    };

    try {
      if (editingId !== null && editingId !== undefined && editingId !== "") {
        await api.put(`/product-models/${editingId}`, payload);
        setNotice("Product model updated successfully.");
      } else {
        await api.post("/product-models", payload);
        setNotice("Product model added successfully.");
      }

      setModalOpen(false);
      setForm({ ...emptyForm });
      await loadData();
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setSaving(false);
    }
  };

  const selectStyle = {
    ...styles.input,
    cursor: "pointer",
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Product Models</h1>
          <p style={styles.subtitle}>
            Manage models and link them to brands, categories and product types.
          </p>
        </div>

        <div style={{ display: "flex", gap: "9px", flexWrap: "wrap" }}>
          <button
            type="button"
            style={styles.button}
            onClick={loadData}
            disabled={loading}
          >
            <RefreshCw size={15} />
            Refresh
          </button>

          <button
            type="button"
            style={{ ...styles.button, ...styles.primary }}
            onClick={openCreate}
          >
            <Plus size={16} />
            Add Product Model
          </button>
        </div>
      </div>

      {notice && (
        <div
          role="status"
          style={{
            padding: "12px",
            marginBottom: "15px",
            borderRadius: "8px",
            background: "#ecfdf3",
            color: "#067647",
          }}
        >
          <CheckCircle2 size={16} style={{ verticalAlign: "middle" }} />{" "}
          {notice}
        </div>
      )}

      {pageError && (
        <div
          role="alert"
          style={{
            padding: "12px",
            marginBottom: "15px",
            borderRadius: "8px",
            border: "1px solid #fecdca",
            background: "#fef3f2",
            color: "#b42318",
            fontSize: "13px",
            overflowWrap: "anywhere",
          }}
        >
          <AlertCircle size={16} style={{ verticalAlign: "middle" }} />{" "}
          {pageError}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
          gap: "14px",
          marginBottom: "20px",
        }}
      >
        {[
          ["Total Models", models.length],
          ["Brands Available", brands.length],
          ["Categories Available", categories.length],
          ["Product Types Available", types.length],
        ].map(([label, value]) => (
          <div
            key={label}
            style={{
              ...styles.card,
              padding: "18px",
              display: "flex",
              gap: "12px",
              alignItems: "center",
            }}
          >
            <Package size={24} color="#2563eb" />
            <div>
              <div style={{ color: "#667085", fontSize: "12px" }}>
                {label}
              </div>
              <div style={{ fontSize: "23px", fontWeight: 750 }}>
                {loading ? "—" : value}
              </div>
            </div>
          </div>
        ))}
      </div>

      <section style={styles.card}>
        <div
          style={{
            padding: "16px 18px",
            borderBottom: "1px solid #edf0f5",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "12px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <strong>Product Model Registry</strong>
            <div style={{ color: "#667085", fontSize: "12px", marginTop: "5px" }}>
              {loading
                ? "Loading records..."
                : `${filteredModels.length} of ${models.length} models`}
            </div>
          </div>

          <div
            style={{
              display: "flex",
              gap: "8px",
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            <Search size={17} color="#98a2b3" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search model, code, brand..."
              aria-label="Search product models"
              style={{ ...styles.input, width: "220px" }}
            />

            <select
              value={brandFilter}
              onChange={(event) => setBrandFilter(event.target.value)}
              style={{ ...selectStyle, width: "auto" }}
              aria-label="Filter by brand"
            >
              <option value="all">All Brands</option>
              {brands.map((brand) => (
                <option key={getId(brand)} value={String(getId(brand))}>
                  {getName(brand) || `Brand #${getId(brand)}`}
                </option>
              ))}
            </select>

            <select
              value={categoryFilter}
              onChange={(event) => setCategoryFilter(event.target.value)}
              style={{ ...selectStyle, width: "auto" }}
              aria-label="Filter by category"
            >
              <option value="all">All Categories</option>
              {categories.map((category) => (
                <option
                  key={getId(category)}
                  value={String(getId(category))}
                >
                  {getName(category) || `Category #${getId(category)}`}
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: "45px", textAlign: "center" }}>
            <LoaderCircle size={25} />
            <p>Loading product master data...</p>
          </div>
        ) : filteredModels.length === 0 ? (
          <div style={{ padding: "45px", textAlign: "center" }}>
            <Package size={30} color="#98a2b3" />
            <p style={{ fontWeight: 700 }}>
              {models.length === 0
                ? "No product models found"
                : "No matching models"}
            </p>
            <p style={{ color: "#667085", fontSize: "13px" }}>
              Add a product model or change your search and filters.
            </p>
            <button
              type="button"
              onClick={openCreate}
              style={{ ...styles.button, ...styles.primary }}
            >
              <Plus size={15} /> Add Product Model
            </button>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {[
                    "Model",
                    "Model Code",
                    "Brand",
                    "Category",
                    "Product Type",
                    "Status",
                    "Action",
                  ].map((heading) => (
                    <th key={heading} style={styles.th}>
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {filteredModels.map((model, index) => {
                  const id = getId(model);
                  const brandId = model.brand_id ?? model.brand?.id ?? "";
                  const categoryId =
                    model.category_id ??
                    model.product_category_id ??
                    model.category?.id ??
                    "";
                  const typeId =
                    model.product_type_id ?? model.product_type?.id ?? "";

                  const brandName =
                    model.brand_name ??
                    model.brand?.name ??
                    brandMap.get(String(brandId)) ??
                    "—";

                  const categoryName =
                    model.category_name ??
                    model.category?.name ??
                    categoryMap.get(String(categoryId)) ??
                    "—";

                  const typeName =
                    model.product_type_name ??
                    model.product_type?.name ??
                    typeMap.get(String(typeId)) ??
                    "—";

                  const status =
                    model.status ??
                    (model.is_active === false ? "Inactive" : "Active");

                  const active = String(status).toLowerCase() === "active";

                  return (
                    <tr key={id || `model-${index}`}>
                      <td style={styles.td}>
                        <strong>{getName(model) || "Unnamed model"}</strong>
                        <div style={{ fontSize: "11px", color: "#98a2b3", marginTop: "4px" }}>
                          ID: {id || "—"}
                        </div>
                      </td>
                      <td style={styles.td}>
                        {model.code ??
                          model.model_code ??
                          model.product_model_code ??
                          "—"}
                      </td>
                      <td style={styles.td}>{brandName}</td>
                      <td style={styles.td}>{categoryName}</td>
                      <td style={styles.td}>{typeName}</td>
                      <td style={styles.td}>
                        <span
                          style={{
                            padding: "5px 9px",
                            borderRadius: "20px",
                            fontSize: "11px",
                            fontWeight: 700,
                            background: active ? "#ecfdf3" : "#f2f4f7",
                            color: active ? "#027a48" : "#475467",
                          }}
                        >
                          {status}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <button
                          type="button"
                          onClick={() => openEdit(model)}
                          style={styles.button}
                        >
                          <Pencil size={13} /> Edit
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {modalOpen && (
        <div
          style={styles.overlay}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !saving) {
              setModalOpen(false);
            }
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="model-form-title"
            style={styles.modal}
          >
            <div
              style={{
                padding: "18px 22px",
                borderBottom: "1px solid #edf0f5",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <h2 id="model-form-title" style={{ margin: 0, fontSize: "19px" }}>
                  {editingId !== null ? "Edit Product Model" : "Add Product Model"}
                </h2>
                <p style={{ color: "#667085", fontSize: "12px", marginBottom: 0 }}>
                  Enter the model details and select its product hierarchy.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setModalOpen(false)}
                disabled={saving}
                aria-label="Close form"
                style={{ border: 0, background: "transparent", cursor: "pointer" }}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={saveModel}>
              <div
                style={{
                  padding: "22px",
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: "17px",
                }}
              >
                <div>
                  <label style={styles.label} htmlFor="model-name">Model Name *</label>
                  <input
                    id="model-name"
                    style={styles.input}
                    value={form.name}
                    onChange={(event) => updateForm("name", event.target.value)}
                    placeholder="Enter model name"
                    required
                    maxLength={150}
                  />
                </div>

                <div>
                  <label style={styles.label} htmlFor="model-code">Model Code *</label>
                  <input
                    id="model-code"
                    style={styles.input}
                    value={form.code}
                    onChange={(event) => updateForm("code", event.target.value)}
                    placeholder="Enter model code"
                    required
                    maxLength={100}
                  />
                </div>

                <div>
                  <label style={styles.label} htmlFor="model-brand">Brand *</label>
                  <select
                    id="model-brand"
                    style={selectStyle}
                    value={form.brand_id}
                    onChange={(event) => updateForm("brand_id", event.target.value)}
                    required
                  >
                    <option value="">Select Brand</option>
                    {brands.map((brand) => (
                      <option key={getId(brand)} value={String(getId(brand))}>
                        {getName(brand) || `Brand #${getId(brand)}`}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={styles.label} htmlFor="model-category">
                    Product Category *
                  </label>
                  <select
                    id="model-category"
                    style={selectStyle}
                    value={form.category_id}
                    onChange={(event) => updateForm("category_id", event.target.value)}
                    required
                  >
                    <option value="">Select Category</option>
                    {categories.map((category) => (
                      <option
                        key={getId(category)}
                        value={String(getId(category))}
                      >
                        {getName(category) || `Category #${getId(category)}`}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={styles.label} htmlFor="model-type">Product Type *</label>
                  <select
                    id="model-type"
                    style={selectStyle}
                    value={form.product_type_id}
                    onChange={(event) => updateForm("product_type_id", event.target.value)}
                    required
                  >
                    <option value="">Select Product Type</option>
                    {filteredTypes.map((type) => (
                      <option key={getId(type)} value={String(getId(type))}>
                        {getName(type) || `Type #${getId(type)}`}
                      </option>
                    ))}
                  </select>
                  {form.category_id && filteredTypes.length === 0 && (
                    <small style={{ color: "#b54708" }}>
                      No product types found for this category.
                    </small>
                  )}
                </div>

                <div>
                  <label style={styles.label} htmlFor="model-status">Status</label>
                  <select
                    id="model-status"
                    style={selectStyle}
                    value={form.status}
                    onChange={(event) => updateForm("status", event.target.value)}
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>
              </div>

              <div
                style={{
                  padding: "16px 22px",
                  borderTop: "1px solid #edf0f5",
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                }}
              >
                <button
                  type="button"
                  style={styles.button}
                  disabled={saving}
                  onClick={() => setModalOpen(false)}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={saving || !brands.length || !categories.length || !types.length}
                  style={{
                    ...styles.button,
                    ...styles.primary,
                    opacity: saving ? 0.65 : 1,
                  }}
                >
                  {saving ? (
                    <>
                      <LoaderCircle size={15} />
                      Saving...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 size={15} />
                      {editingId !== null ? "Save Changes" : "Create Model"}
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}