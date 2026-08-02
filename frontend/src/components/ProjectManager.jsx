import { ImageUp, Plus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { api, getErrorMessage } from "@/lib/api";

export default function ProjectManager() {
  const [uploading, setUploading] = useState(false);
  const [coverImage, setCoverImage] = useState("");

  async function uploadFile(event) {
    const [file] = event.target.files;
    if (!file) return;
    setUploading(true);
    const data = new FormData();
    data.append("file", file);
    try {
      const response = await api.post("/admin/media", data);
      setCoverImage(`${process.env.REACT_APP_BACKEND_URL}${response.data.url}`);
      toast.success("Media is ready for your portfolio project.");
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setUploading(false);
    }
  }

  async function createProject(event) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget).entries());
    try {
      await api.post("/admin/projects", { ...values, cover_image: coverImage });
      toast.success("Project published to the portfolio.");
      event.currentTarget.reset();
      setCoverImage("");
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  return (
    <section className="admin-editor" data-testid="portfolio-manager">
      <div className="panel-heading"><div><p className="eyebrow">Portfolio manager</p><h3>Publish a new project</h3></div></div>
      <form className="editor-form" data-testid="portfolio-project-form" onSubmit={createProject}>
        <label>Project title<input data-testid="portfolio-title-input" name="title" required /></label>
        <label>Industry<input data-testid="portfolio-industry-input" name="industry" required /></label>
        <label>Year<input data-testid="portfolio-year-input" defaultValue="2026" name="year" required /></label>
        <label>Live website URL<input data-testid="portfolio-url-input" name="live_url" type="url" /></label>
        <label>Project summary<textarea data-testid="portfolio-summary-input" minLength="10" name="summary" required /></label>
        <label>Cover image or video<input accept="image/jpeg,image/png,image/webp,image/gif,video/mp4" data-testid="portfolio-media-upload-input" onChange={uploadFile} type="file" /></label>
        <span className="media-status" data-testid="portfolio-media-status">{uploading ? "Uploading media…" : coverImage ? "Media attached" : "No media attached"}</span>
        <button className="button button-primary" data-testid="portfolio-publish-button" disabled={uploading} type="submit"><Plus size={16} /> Publish project</button>
      </form>
    </section>
  );
}