import { ArrowUpRight, LockKeyhole } from "lucide-react";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { useAuth } from "@/components/AuthContext";
import { api, getErrorMessage } from "@/lib/api";

export default function LoginPage() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (user) {
    return <Navigate to={user.role === "admin" ? "/admin" : "/client"} replace />;
  }

  async function signIn(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setIsSubmitting(true);
    try {
      const response = await api.post("/auth/login", Object.fromEntries(form.entries()));
      setUser(response.data);
      navigate(response.data.role === "admin" ? "/admin" : "/client");
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page" data-testid="login-page">
      <a className="brand-mark" data-testid="login-home-link" href="/"> <span>Q</span>WEBLIQ</a>
      <section className="login-panel" data-testid="login-panel">
        <div className="login-mark"><LockKeyhole size={22} /></div>
        <p className="eyebrow">Private workspace</p>
        <h1 data-testid="login-heading">Keep growth moving.</h1>
        <p data-testid="login-description">Access your Qwebliq workspace to manage the work that matters.</p>
        <form data-testid="login-form" onSubmit={signIn}>
          <label>Email<input autoComplete="email" data-testid="login-email-input" name="email" required type="email" /></label>
          <label>Password<input autoComplete="current-password" data-testid="login-password-input" minLength="8" name="password" required type="password" /></label>
          <button className="button button-primary" data-testid="login-submit-button" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in…" : "Enter workspace"} <ArrowUpRight size={17} />
          </button>
        </form>
      </section>
    </main>
  );
}