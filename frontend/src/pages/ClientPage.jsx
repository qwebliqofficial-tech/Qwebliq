import { CheckCircle2, Clock3, Download, MessageSquare, Upload } from "lucide-react";
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "@/components/AuthContext";
import WorkspaceNav from "@/components/WorkspaceNav";
import { api } from "@/lib/api";

export default function ClientPage() {
  const { user, isLoading } = useAuth();
  const [data, setData] = useState({ projects: [], message: "" });

  useEffect(() => {
    if (user?.role === "client") {
      api.get("/client/projects").then((response) => setData(response.data));
    }
  }, [user]);

  if (!isLoading && user?.role !== "client") {
    return <Navigate to="/login" replace />;
  }

  return (
    <main className="workspace client-workspace" data-testid="client-page">
      <WorkspaceNav subtitle="Client portal" title="Your project space" />
      <section className="workspace-content">
        <div className="workspace-intro"><div><p className="eyebrow">Current engagement</p><h2 data-testid="client-greeting">Everything important, in one clear place.</h2></div><span data-testid="client-project-count">{data.projects.length} active project</span></div>
        {data.projects.map((project, index) => <article className="client-project" data-testid={`client-project-${index}`} key={project.name}><div><p className="eyebrow">{project.status}</p><h3>{project.name}</h3><p data-testid={`client-project-next-step-${index}`}>{project.next_step}</p></div><div className="progress-wrap"><span>{project.progress}% complete</span><div className="progress-track"><i style={{ width: `${project.progress}%` }} /></div></div></article>)}
        <div className="client-actions"><article data-testid="client-timeline-card"><Clock3 size={21} /><h3>Timeline</h3><p>Milestones and decision points stay visible as the work advances.</p></article><article data-testid="client-files-card"><Download size={21} /><h3>Project files</h3><p>Approved assets, handover material, and final documents will appear here.</p></article><article data-testid="client-approvals-card"><CheckCircle2 size={21} /><h3>Approvals</h3><p>Review and approve key creative decisions without losing the context.</p></article></div>
        <div className="client-tool-row"><button data-testid="client-upload-button" type="button"><Upload size={16} /> Upload requirement</button><button data-testid="client-message-button" type="button"><MessageSquare size={16} /> Message Qwebliq</button></div>
        <p className="portal-note" data-testid="client-portal-note">{data.message}</p>
      </section>
    </main>
  );
}