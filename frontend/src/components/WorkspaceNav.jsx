import { ArrowLeft, LayoutDashboard, LogOut, UserRound } from "lucide-react";
import { Link } from "react-router-dom";

import { useAuth } from "@/components/AuthContext";

export default function WorkspaceNav({ title, subtitle }) {
  const { logout, user } = useAuth();

  async function handleLogout() {
    await logout();
    window.location.assign("/");
  }

  return (
    <header className="workspace-nav" data-testid="workspace-navigation">
      <Link className="workspace-back" data-testid="workspace-home-link" to="/">
        <ArrowLeft size={17} /> Qwebliq
      </Link>
      <div className="workspace-title"><span data-testid="workspace-label">{subtitle}</span><h1 data-testid="workspace-title">{title}</h1></div>
      <div className="workspace-actions"><span className="workspace-user" data-testid="workspace-user"><UserRound size={15} /> {user?.name}</span><button data-testid="workspace-logout-button" onClick={handleLogout} type="button"><LogOut size={16} /> Sign out</button></div>
    </header>
  );
}