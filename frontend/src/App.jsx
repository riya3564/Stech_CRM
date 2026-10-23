import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";

import Login from "./pages/auth/Login";
import Dashboard from "./pages/dashboard/Dashboard";
import Customers from "./pages/customers/Customers";

import Products from "./pages/products/Products";
import Brands from "./pages/products/Brands";
import ProductCategories from "./pages/products/ProductCategories";
import ProductTypes from "./pages/products/ProductTypes";
import ProductModels from "./pages/products/ProductModels";

import ServiceCalls from "./pages/service-calls/ServiceCalls";
import Engineers from "./pages/engineers/Engineers";
import Appointments from "./pages/appointments/Appointments";
import Parts from "./pages/parts/Parts";
import Reports from "./pages/reports/Reports";
import STCopilot from "./pages/ai/AICopilot";

import "./index.css";

function App() {
return (
<BrowserRouter>
<Routes>
<Route path="/login" element={<Login />} />

    <Route element={<AppLayout />}>
      <Route
        path="/"
        element={<Navigate to="/dashboard" replace />}
      />

      <Route path="/dashboard" element={<Dashboard />} />

      <Route path="/customers" element={<Customers />} />

      {/* Product Management */}
      <Route path="/products" element={<Products />} />
      <Route path="/products/brands" element={<Brands />} />
      <Route
        path="/products/categories"
        element={<ProductCategories />}
      />
      <Route
        path="/products/types"
        element={<ProductTypes />}
      />
      <Route path="/products/models" element={<ProductModels />} />

      <Route path="/service-calls" element={<ServiceCalls />} />
      <Route path="/engineers" element={<Engineers />} />
      <Route path="/appointments" element={<Appointments />} />
      <Route path="/parts" element={<Parts />} />
      <Route path="/reports" element={<Reports />} />
      <Route path="/ai-copilot" element={<STCopilot />} />
    </Route>

    <Route
      path="*"
      element={<Navigate to="/dashboard" replace />}
    />
  </Routes>
</BrowserRouter>

);
}

export default App;