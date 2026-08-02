import { BarChart3, FilePlus2, Inbox, Plus, Radio, UsersRound } from "lucide-react";
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { toast } from "sonner";

import { useAuth } from "@/components/AuthContext";
import WorkspaceNav from "@/components/WorkspaceNav";
import { api, getErrorMessage } from "@/lib/api";

const metricIcons = [Inbox, BarChart3, UsersRound, Radio];

export default function AdminPage() {
  const { user, isLoading } = useAuth();
  const [overview, setOverview] = useState({ metrics: [], recent_inquiries: [] });
  const [activeForm, setActiveForm] = useState("feed");

  useEffect(() => {
    if (user?.role === "admin") {
      api.get("/admin/overview").then((response) => setOverview(response.data)).catch(() => toast.error("Dashboard data is unavailable."));
    }
  }, [user]);

  if (!isLoading && user?.role !== "admin") {
    return <Navigate to="/login" replace />;
  }

  async function publish(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const routes = { feed: "/admin/feed", blog: "/admin/blog", project: "/admin/projects", client: "/auth/clients" };
    const fields = Object.fromEntries(form.entries());
    try {
      await api.post(routes[activeForm], fields);
      toast.success(activeForm === "client" ? "Client access has been created." : "Saved to the Qwebliq platform.");
      event.currentTarget.reset();
      const response = await api.get("/admin/overview");
      setOverview(response.data);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  const formFields = {
    feed: ["title", "category", "excerpt"],
    blog: ["title", "category", "excerpt"],
    project: ["title", "industry", "summary", "live_url"],
    client: ["name", "email", "password"],
  };

  return (
    <main className="workspace" data-testid="admin-page">
      <WorkspaceNav subtitle="Administrator" title="Studio overview" />
      <section className="workspace-content">
        <div className="workspace-intro"><div><p className="eyebrow">Operating view</p><h2 data-testid="admin-greeting">A clear view of what is moving.</h2></div><span data-testid="admin-status">All systems ready</span></div>
        <div className="metric-grid" data-testid="admin-metrics">
          {overview.metrics.map((metric, index) => { const Icon = metricIcons[index] || BarChart3; return <article className="metric" data-testid={`admin-metric-${index}`} key={metric.label}><Icon size={18} /><span>{metric.label}</span><strong>{metric.value}</strong><small>{metric.trend}</small></article>; })}
        </div>
        <div className="admin-layout">
          <section className="panel leads-panel" data-testid="recent-inquiries-panel"><div className="panel-heading"><div><p className="eyebrow">Lead desk</p><h3>Recent inquiries</h3></div><Inbox size={19} /></div>{overview.recent_inquiries.length === 0 ? <p className="empty-state" data-testid="empty-inquiries">New project notes will appear here.</p> : overview.recent_inquiries.map((inquiry, index) => <article className="lead-row" data-testid={`inquiry-row-${index}`} key={`${inquiry.email}-${inquiry.created_at}`}><div><strong>{inquiry.name}</strong><span>{inquiry.company || inquiry.email}</span></div><p>{inquiry.message}</p><small>{inquiry.budget || "New inquiry"}</small></article>)}</section>
          <section className="panel publish-panel" data-testid="content-publisher-panel"><div className="panel-heading"><div><p className="eyebrow">Studio publishing</p><h3>Make an update</h3></div><FilePlus2 size={19} /></div><div className="form-tabs">{["feed", "blog", "project", "client"].map((kind) => <button className={activeForm === kind ? "active" : ""} data-testid={`publisher-${kind}-tab`} key={kind} onClick={() => setActiveForm(kind)} type="button">{kind}</button>)}</div><form data-testid="content-publisher-form" onSubmit={publish}>{formFields[activeForm].map((field) => field === "excerpt" || field === "summary" ? <textarea data-testid={`publisher-${field}-input`} key={field} minLength="10" name={field} placeholder={field.replace("_", " ")} required /> : <input data-testid={`publisher-${field}-input`} key={field} minLength={field === "password" ? "8" : "2"} name={field} placeholder={field.replace("_", " ")} required={field !== "live_url"} type={field === "email" ? "email" : field === "password" ? "password" : "text"} />)}<button className="button button-primary" data-testid="publisher-submit-button" type="submit"><Plus size={17} /> Save {activeForm}</button></form></section>
        </div>
      </section>
    </main>
  );
}