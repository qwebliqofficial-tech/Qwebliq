import { BarChart3, Inbox, Radio, UsersRound } from "lucide-react";
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { toast } from "sonner";

import PricingEditor from "@/components/PricingEditor";
import ProjectManager from "@/components/ProjectManager";
import WebsiteEditor from "@/components/WebsiteEditor";
import ContentPublisher from "@/components/ContentPublisher";
import TestDataCleanup from "@/components/TestDataCleanup";
import { useAuth } from "@/components/AuthContext";
import WorkspaceNav from "@/components/WorkspaceNav";
import { api, getErrorMessage } from "@/lib/api";

const metricIcons = [Inbox, BarChart3, UsersRound, Radio];

export default function AdminPage() {
  const { user, isLoading } = useAuth();
  const [overview, setOverview] = useState({ metrics: [], recent_inquiries: [] });
  const [settings, setSettings] = useState(null);

  useEffect(() => {
    if (user?.role === "admin") {
      Promise.all([api.get("/admin/overview"), api.get("/admin/site-settings")])
        .then(([overviewResponse, settingsResponse]) => {
          setOverview(overviewResponse.data);
          setSettings(settingsResponse.data.settings);
        })
        .catch(() => toast.error("Dashboard data is unavailable."));
    }
  }, [user]);

  if (!isLoading && user?.role !== "admin") {
    return <Navigate replace to="/login" />;
  }

  async function saveSettings(nextSettings) {
    try {
      const response = await api.put("/admin/site-settings", { settings: nextSettings });
      setSettings(response.data.settings);
      toast.success("Your public website changes are live.");
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  async function refreshOverview() {
    const response = await api.get("/admin/overview");
    setOverview(response.data);
  }

  return (
    <main className="workspace admin-control-center" data-testid="admin-page">
      <WorkspaceNav subtitle="Administrator" title="Qwebliq control center" />
      <section className="workspace-content">
        <div className="workspace-intro">
          <div><p className="eyebrow">Live website controls</p><h2 data-testid="admin-greeting">Shape your studio, in one place.</h2></div>
          <span data-testid="admin-status">Live editing enabled</span>
        </div>
        <div className="metric-grid" data-testid="admin-metrics">
          {overview.metrics.map((metric, index) => {
            const Icon = metricIcons[index] || BarChart3;
            return <article className="metric" data-testid={`admin-metric-${index}`} key={metric.label}><Icon size={18} /><span>{metric.label}</span><strong>{metric.value}</strong><small>{metric.trend}</small></article>;
          })}
        </div>
        <div className="admin-control-grid">
          <section className="panel leads-panel" data-testid="recent-inquiries-panel">
            <div className="panel-heading"><div><p className="eyebrow">Lead desk</p><h3>Recent inquiries</h3></div><div className="lead-actions"><TestDataCleanup onDeleted={refreshOverview} /><Inbox size={19} /></div></div>
            {overview.recent_inquiries.length === 0 ? <p className="empty-state" data-testid="empty-inquiries">New project notes will appear here.</p> : overview.recent_inquiries.map((inquiry, index) => <article className="lead-row" data-testid={`inquiry-row-${index}`} key={`${inquiry.email}-${inquiry.created_at}`}><div><strong>{inquiry.name}</strong><span>{inquiry.company || inquiry.email}</span></div><p>{inquiry.message}</p><small>{inquiry.budget || "New inquiry"}</small></article>)}
          </section>
          <ProjectManager />
          <ContentPublisher />
          {settings && <PricingEditor onSave={saveSettings} settings={settings} />}
          {settings && <WebsiteEditor onSave={saveSettings} settings={settings} />}
        </div>
      </section>
    </main>
  );
}