import { ArrowUpRight, Check, Code2, Layers3, Search, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import HeroScene from "@/components/HeroScene";
import FoundersSection from "@/components/FoundersSection";
import ContactSection from "@/components/ContactSection";
import PricingSection from "@/components/PricingSection";
import SiteNav from "@/components/SiteNav";
import { api, getErrorMessage } from "@/lib/api";

const icons = [Layers3, Sparkles, Code2, Search];

export default function HomePage() {
  const [content, setContent] = useState({ services: [], projects: [], blogs: [], feed: [], faqs: [] });
  const [isLight, setIsLight] = useState(false);
  const [faqQuery, setFaqQuery] = useState("");
  const [estimate, setEstimate] = useState("");
  const [newsletterEmail, setNewsletterEmail] = useState("");

  useEffect(() => {
    api.get("/site").then((response) => setContent(response.data)).catch(() => toast.error("Content is loading soon."));
  }, []);

  const visibleFaqs = useMemo(
    () => content.faqs.filter((faq) => faq.q.toLowerCase().includes(faqQuery.toLowerCase())),
    [content.faqs, faqQuery],
  );

  async function calculate(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const response = await api.post("/calculator", {
        project_type: form.get("project_type"),
        timeline: form.get("timeline"),
        pages: Number(form.get("pages")),
      });
      setEstimate(response.data.label);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  async function sendInquiry(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const response = await api.post("/inquiries", Object.fromEntries(form.entries()));
      toast.success(response.data.message);
      event.currentTarget.reset();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  async function subscribe(event) {
    event.preventDefault();
    try {
      const response = await api.post("/newsletter", { email: newsletterEmail });
      toast.success(response.data.message);
      setNewsletterEmail("");
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  return (
    <main className={isLight ? "site-shell light" : "site-shell"} data-testid="home-page">
      <SiteNav isLight={isLight} onThemeToggle={() => setIsLight((value) => !value)} />
      <HeroScene hero={content.settings?.hero} />
      <section className="intro-section section-pad" data-testid="studio-introduction">
        <p className="eyebrow">The Qwebliq approach</p>
        <div className="intro-grid">
          <h2 data-testid="intro-heading">The digital layer of your business should feel inevitable.</h2>
          <p data-testid="intro-description">
            We combine sharp creative direction with dependable systems — so every expression
            of your brand has a reason to exist and somewhere to grow.
          </p>
        </div>
      </section>
      <section className="services-section section-pad" id="services" data-testid="services-section">
        <div className="section-heading"><p className="eyebrow">Capabilities</p><h2>Work that makes the next move easier.</h2></div>
        <div className="service-grid">
          {content.services.map((service, index) => {
            const Icon = icons[index] || Sparkles;
            return <article className="service-card" data-testid={`service-card-${index}`} key={service.name}><Icon size={22} /><h3>{service.name}</h3><p>{service.detail}</p><ArrowUpRight size={18} /></article>;
          })}
        </div>
      </section>
      <section className="work-section section-pad" id="work" data-testid="work-section">
        <div className="section-heading work-heading"><div><p className="eyebrow">Selected work</p><h2>Built to be remembered. Engineered to keep moving.</h2></div><span data-testid="work-count">01 / {String(content.projects.length).padStart(2, "0")}</span></div>
        {content.projects.map((project) => <article className="feature-project" data-testid={`project-${project.slug || project.title}`} key={project.title}><div className="project-image"><img alt={`${project.title} project preview`} data-testid={`project-image-${project.slug || "item"}`} src={project.cover_image} /></div><div className="project-details"><p className="eyebrow">{project.industry} / {project.year}</p><h3>{project.title}</h3><p>{project.summary}</p><div className="project-tags">{project.technologies?.map((technology) => <span data-testid={`technology-${technology}`} key={technology}>{technology}</span>)}</div><a className="text-link" data-testid={`project-live-${project.slug || "item"}`} href={project.live_url} rel="noreferrer" target="_blank">Visit live website <ArrowUpRight size={16} /></a></div></article>)}
      </section>
      <FoundersSection founders={content.settings?.founders} />
      <section className="proof-section section-pad" data-testid="proof-section">
        <div className="section-heading"><p className="eyebrow">Why Qwebliq</p><h2>Designed around the business, not a pre-built template.</h2></div>
        <div className="comparison-grid"><div className="comparison-side"><span>Common approach</span>{["Template-first", "Generic design", "Unclear ownership", "Slow iteration"].map((item) => <p data-testid={`comparison-other-${item}`} key={item}>× {item}</p>)}</div><div className="comparison-side qwebliq-side"><span>Qwebliq LLP</span>{["Fully custom", "Business-focused", "SEO ready", "Dedicated support"].map((item) => <p data-testid={`comparison-qwebliq-${item}`} key={item}><Check size={16} /> {item}</p>)}</div></div>
      </section>
      <PricingSection pricing={content.settings?.pricing} />
      <section className="calculator-section section-pad" data-testid="calculator-section"><div><p className="eyebrow">Project planner</p><h2>A useful starting point, not a fixed quote.</h2><p>Choose a few signals and get a clear opening range for your conversation with us.</p></div><form className="calculator-form" data-testid="project-calculator-form" onSubmit={calculate}><label>Focus<select data-testid="calculator-project-type" defaultValue="website" name="project_type"><option value="website">Growth website</option><option value="ecommerce">E-commerce</option><option value="brand">Brand system</option><option value="growth">Growth programme</option><option value="social">Social media marketing</option></select></label><label>Timeline<select data-testid="calculator-timeline" defaultValue="standard" name="timeline"><option value="standard">Thoughtful pace</option><option value="accelerated">Accelerated</option></select></label><label>Pages<input data-testid="calculator-pages" defaultValue="6" max="50" min="1" name="pages" type="number" /></label><button className="button button-primary" data-testid="calculator-submit-button" type="submit">Calculate range <ArrowUpRight size={17} /></button>{estimate && <strong className="estimate" data-testid="calculator-result">{estimate}</strong>}</form></section>
      <section className="updates-section section-pad" id="insights" data-testid="updates-section"><div className="section-heading"><p className="eyebrow">Latest updates</p><h2>Notes from a studio in motion.</h2></div><div className="updates-grid">{content.feed.map((post, index) => <article className="update-card" data-testid={`feed-post-${index}`} key={`${post.id || post.title}-${post.date}-${index}`}><span>{post.tag} · {post.date}</span><h3>{post.title}</h3><p>{post.excerpt}</p></article>)}</div></section>
      <section className="faq-section section-pad" data-testid="faq-section"><div className="section-heading"><p className="eyebrow">Common ground</p><h2>Questions, answered clearly.</h2></div><input className="faq-search" data-testid="faq-search-input" onChange={(event) => setFaqQuery(event.target.value)} placeholder="Search questions" value={faqQuery} />{visibleFaqs.map((faq, index) => <details data-testid={`faq-item-${index}`} key={faq.q}><summary>{faq.q}</summary><p>{faq.a}</p></details>)}</section>
      <ContactSection contact={content.settings?.contact} onSubmit={sendInquiry} />
      <footer className="site-footer" data-testid="site-footer"><div className="footer-brand"><span>Q</span>WEBLIQ LLP <small>Crafted for Growth.</small></div><form className="newsletter" data-testid="newsletter-form" onSubmit={subscribe}><label htmlFor="newsletter-email">A thoughtful note from Qwebliq, occasionally.</label><div><input data-testid="newsletter-email-input" id="newsletter-email" onChange={(event) => setNewsletterEmail(event.target.value)} placeholder="Email address" required type="email" value={newsletterEmail} /><button data-testid="newsletter-submit-button" type="submit"><ArrowUpRight size={17} /></button></div></form><p data-testid="footer-copyright">© 2026 Qwebliq LLP. All rights reserved.</p></footer>
    </main>
  );
}