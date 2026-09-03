import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import Financials from "./pages/Financials";
import Documents from "./pages/Documents";
import AIAnalysis from "./pages/AIAnalysis";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/financials" element={<Financials />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/ai-analysis" element={<AIAnalysis />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}