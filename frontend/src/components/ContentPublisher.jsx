import { PenLine } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { api, getErrorMessage } from "@/lib/api";

export default function ContentPublisher() {
  const [kind, setKind] = useState("feed");

  async function publish(event) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget).entries());
    try {
      await api.post(kind === "feed" ? "/admin/feed" : "/admin/blog", values);
      toast.success(`${kind === "feed" ? "Update" : "Article"} published.`);
      event.currentTarget.reset();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  return (
    <section className="admin-editor" data-testid="content-publisher">
      <div className="panel-heading"><div><p className="eyebrow">Studio publishing</p><h3>Write an update</h3></div><PenLine size={18} /></div>
      <div className="form-tabs">
        <button className={kind === "feed" ? "active" : ""} data-testid="publish-feed-tab" onClick={() => setKind("feed")} type="button">Latest update</button>
        <button className={kind === "blog" ? "active" : ""} data-testid="publish-blog-tab" onClick={() => setKind("blog")} type="button">Blog article</button>
      </div>
      <form className="editor-form" data-testid="content-publisher-form" onSubmit={publish}>
        <label>Title<input data-testid="publisher-title-input" name="title" required /></label>
        <label>Category<input data-testid="publisher-category-input" defaultValue={kind === "feed" ? "Studio note" : "Business Growth"} name="category" required /></label>
        <label>Summary<textarea data-testid="publisher-excerpt-input" minLength="10" name="excerpt" required /></label>
        <button className="button button-primary" data-testid="publisher-submit-button" type="submit">Publish {kind === "feed" ? "update" : "article"}</button>
      </form>
    </section>
  );
}