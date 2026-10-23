import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
Package,
Tags,
Boxes,
Layers3,
RefreshCw,
ArrowRight,
AlertCircle,
ChevronRight,
} from "lucide-react";
import api from "../../services/api";

const getRows = (response) => {
const body = response?.data ?? response;

if (Array.isArray(body)) return body;
if (Array.isArray(body?.items)) return body.items;
if (Array.isArray(body?.data)) return body.data;
if (Array.isArray(body?.results)) return body.results;
if (Array.isArray(body?.value)) return body.value;

return [];
};

const getErrorMessage = (error) =>
error?.response?.data?.message ||
error?.response?.data?.error ||
error?.message ||
"Unable to load product data.";

const sections = [
{
title: "Brands",
description: "View, add and edit product brands.",
path: "/products/brands",
apiPath: "/brands",
icon: Tags,
color: "#2563eb",
background: "#eff6ff",
key: "brands",
},
{
title: "Product Categories",
description: "Manage categories such as TV, AC and refrigerator.",
path: "/products/categories",
apiPath: "/product-categories",
icon: Boxes,
color: "#7c3aed",
background: "#f5f3ff",
key: "categories",
},
{
title: "Product Types",
description: "Manage types linked to product categories.",
path: "/products/types",
apiPath: "/product-types",
icon: Layers3,
color: "#0f766e",
background: "#f0fdfa",
key: "types",
},
{
title: "Product Models",
description: "Manage models, brands, categories and product types.",
path: "/products/models",
apiPath: "/product-models",
icon: Package,
color: "#c2410c",
background: "#fff7ed",
key: "models",
},
];

const cardStyle = {
background: "#fff",
border: "1px solid #e5eaf1",
borderRadius: "14px",
boxShadow: "0 2px 8px rgba(16,24,40,0.025)",
};

export default function Products() {
const navigate = useNavigate();

const [counts, setCounts] = useState({
brands: null,
categories: null,
types: null,
models: null,
});

const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

const loadData = async () => {
setLoading(true);
setError("");

const results = await Promise.allSettled(
  sections.map((section) => api.get(section.apiPath))
);

const nextCounts = {
  brands: null,
  categories: null,
  types: null,
  models: null,
};

const failed = [];

results.forEach((result, index) => {
  const section = sections[index];

  if (result.status === "fulfilled") {
    nextCounts[section.key] = getRows(result.value).length;
  } else {
    failed.push(
      `${section.apiPath}: ${getErrorMessage(result.reason)}`
    );
    console.error(
      `Failed to load ${section.title}:`,
      result.reason
    );
  }
});

setCounts(nextCounts);

if (failed.length) {
  setError(failed.join(" | "));
}

setLoading(false);

};

useEffect(() => {
loadData();
}, []);

const openSection = (path) => {
navigate(path);
};

return (
<main
style={{
minHeight: "100%",
padding: "26px",
background: "#f5f8fc",
color: "#172033",
boxSizing: "border-box",
}}
>
<header
style={{
display: "flex",
justifyContent: "space-between",
alignItems: "center",
flexWrap: "wrap",
gap: "16px",
marginBottom: "26px",
}}
>
<div>
<div
style={{
display: "flex",
alignItems: "center",
gap: "10px",
marginBottom: "7px",
}}
>
<Package size={25} color="#2563eb" />
<h1
style={{
margin: 0,
fontSize: "27px",
fontWeight: 750,
letterSpacing: "-0.5px",
}}
>
Product Management
</h1>
</div>

      <p style={{ margin: 0, color: "#667085", fontSize: "14px" }}>
        Manage the product catalogue and product hierarchy.
      </p>
    </div>

    <button
      type="button"
      onClick={loadData}
      disabled={loading}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "8px",
        padding: "10px 14px",
        border: "1px solid #dce3ed",
        borderRadius: "9px",
        background: "#fff",
        color: "#344054",
        cursor: loading ? "wait" : "pointer",
        fontWeight: 600,
      }}
    >
      <RefreshCw size={16} />
      {loading ? "Loading..." : "Refresh"}
    </button>
  </header>

  {error && (
    <div
      role="alert"
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: "10px",
        padding: "14px",
        marginBottom: "20px",
        border: "1px solid #fecdca",
        borderRadius: "10px",
        background: "#fef3f2",
        color: "#b42318",
        fontSize: "13px",
        lineHeight: 1.6,
        overflowWrap: "anywhere",
      }}
    >
      <AlertCircle size={18} style={{ flexShrink: 0 }} />
      <div>
        <strong>Some product data could not be loaded.</strong>
        <div style={{ marginTop: "4px" }}>{error}</div>
      </div>
    </div>
  )}

  <section
    aria-label="Product summary"
    style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(205px, 1fr))",
      gap: "16px",
      marginBottom: "28px",
    }}
  >
    {sections.map((section) => {
      const Icon = section.icon;
      const value = counts[section.key];

      return (
        <button
          type="button"
          key={section.key}
          onClick={() => openSection(section.path)}
          style={{
            ...cardStyle,
            padding: "20px",
            textAlign: "left",
            cursor: "pointer",
            color: "#172033",
            transition: "border-color 0.15s, box-shadow 0.15s",
          }}
          onMouseOver={(event) => {
            event.currentTarget.style.borderColor = "#93b4f8";
            event.currentTarget.style.boxShadow =
              "0 5px 16px rgba(16,24,40,0.07)";
          }}
          onMouseOut={(event) => {
            event.currentTarget.style.borderColor = "#e5eaf1";
            event.currentTarget.style.boxShadow =
              "0 2px 8px rgba(16,24,40,0.025)";
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "18px",
            }}
          >
            <span
              style={{
                width: "44px",
                height: "44px",
                display: "grid",
                placeItems: "center",
                borderRadius: "12px",
                background: section.background,
                color: section.color,
              }}
            >
              <Icon size={22} />
            </span>
            <ChevronRight size={19} color="#98a2b3" />
          </div>

          <div
            style={{
              fontSize: "13px",
              color: "#667085",
              marginBottom: "7px",
            }}
          >
            {section.title}
          </div>

          <div style={{ fontSize: "28px", fontWeight: 750 }}>
            {loading ? "—" : value === null ? "Unavailable" : value}
          </div>

          <div
            style={{
              fontSize: "12px",
              color: "#667085",
              marginTop: "5px",
            }}
          >
            {value === 1 ? "record" : "records"}
          </div>
        </button>
      );
    })}
  </section>

  <section style={{ ...cardStyle, overflow: "hidden" }}>
    <div
      style={{
        padding: "20px",
        borderBottom: "1px solid #edf0f5",
      }}
    >
      <h2 style={{ margin: 0, fontSize: "17px", fontWeight: 750 }}>
        Product Catalogue
      </h2>

      <p
        style={{
          margin: "6px 0 0",
          color: "#667085",
          fontSize: "13px",
        }}
      >
        Open a master page to view existing records and manage entries.
      </p>
    </div>

    {sections.map((section, index) => {
      const Icon = section.icon;

      return (
        <button
          type="button"
          key={section.key}
          onClick={() => openSection(section.path)}
          style={{
            display: "flex",
            alignItems: "center",
            width: "100%",
            gap: "15px",
            padding: "19px 20px",
            textAlign: "left",
            border: 0,
            borderBottom:
              index === sections.length - 1
                ? 0
                : "1px solid #edf0f5",
            background: "#fff",
            cursor: "pointer",
            color: "#172033",
          }}
          onMouseOver={(event) => {
            event.currentTarget.style.background = "#f8fafc";
          }}
          onMouseOut={(event) => {
            event.currentTarget.style.background = "#fff";
          }}
        >
          <span
            style={{
              width: "42px",
              height: "42px",
              flexShrink: 0,
              display: "grid",
              placeItems: "center",
              borderRadius: "11px",
              background: section.background,
              color: section.color,
            }}
          >
            <Icon size={20} />
          </span>

          <span style={{ flex: 1, minWidth: 0 }}>
            <span
              style={{
                display: "block",
                fontWeight: 700,
                fontSize: "14px",
              }}
            >
              {section.title}
            </span>

            <span
              style={{
                display: "block",
                marginTop: "5px",
                color: "#667085",
                fontSize: "12px",
                lineHeight: 1.5,
              }}
            >
              {section.description}
            </span>

            <span
              style={{
                display: "block",
                marginTop: "7px",
                color: "#2563eb",
                fontSize: "12px",
                fontWeight: 650,
              }}
            >
              {loading
                ? "Open section"
                : counts[section.key] === null
                  ? "Open section · data unavailable"
                  : `View ${counts[section.key]} records`}
            </span>
          </span>

          <ArrowRight size={18} color="#667085" />
        </button>
      );
    })}
  </section>
</main>

);
}