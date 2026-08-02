import "@/App.css";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AuthProvider } from "@/components/AuthContext";
import AdminPage from "@/pages/AdminPage";
import ClientPage from "@/pages/ClientPage";
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<HomePage />} path="/" />
          <Route element={<LoginPage />} path="/login" />
          <Route element={<AdminPage />} path="/admin" />
          <Route element={<ClientPage />} path="/client" />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
