import { Save } from "lucide-react";
import { useEffect, useState } from "react";

function formatServices(services) {
  return services.map((service) => `${service.name} | ${service.detail}`).join("\n");
}

function parseServices(value) {
  return value.split("\n").map((line) => line.split("|").map((part) => part.trim())).filter(([name, detail]) => name && detail).map(([name, detail]) => ({ name, detail }));
}

export default function WebsiteEditor({ settings, onSave }) {
  const [draft, setDraft] = useState({
    headline: "", description: "", services: "", email: "", phoneOne: "", phoneTwo: "", instagram: "", founderOne: "", founderOneRole: "", founderTwo: "", founderTwoRole: "",
  });

  useEffect(() => {
    if (settings) {
      setDraft({
        headline: settings.hero?.headline || "",
        description: settings.hero?.description || "",
        services: formatServices(settings.services || []),
        email: settings.contact?.email || "",
        phoneOne: settings.contact?.phones?.[0] || "",
        phoneTwo: settings.contact?.phones?.[1] || "",
        instagram: settings.contact?.instagram || "",
        founderOne: settings.founders?.[0]?.name || "",
        founderOneRole: settings.founders?.[0]?.role || "",
        founderTwo: settings.founders?.[1]?.name || "",
        founderTwoRole: settings.founders?.[1]?.role || "",
      });
    }
  }, [settings]);

  function update(field, value) {
    setDraft((current) => ({ ...current, [field]: value }));
  }

  function submit(event) {
    event.preventDefault();
    onSave({
      ...settings,
      hero: { ...settings.hero, headline: draft.headline, description: draft.description },
      services: parseServices(draft.services),
      contact: {
        ...settings.contact,
        email: draft.email,
        phones: [draft.phoneOne, draft.phoneTwo].filter(Boolean),
        instagram: draft.instagram,
      },
      founders: [
        { ...settings.founders?.[0], name: draft.founderOne, role: draft.founderOneRole },
        { ...settings.founders?.[1], name: draft.founderTwo, role: draft.founderTwoRole },
      ],
    });
  }

  return (
    <section className="admin-editor" data-testid="website-editor">
      <div className="panel-heading">
        <div><p className="eyebrow">Website content</p><h3>Shape the public story</h3></div>
      </div>
      <form className="editor-form" data-testid="website-editor-form" onSubmit={submit}>
        <label>Hero headline<input data-testid="hero-headline-input" onChange={(event) => update("headline", event.target.value)} value={draft.headline} /></label>
        <label>Hero description<textarea data-testid="hero-description-input" onChange={(event) => update("description", event.target.value)} value={draft.description} /></label>
        <label>Service cards <small>One per line: Service name | service description</small><textarea data-testid="services-editor-input" onChange={(event) => update("services", event.target.value)} value={draft.services} /></label>
        <label>Public email<input data-testid="public-email-input" onChange={(event) => update("email", event.target.value)} type="email" value={draft.email} /></label>
        <label>Primary phone<input data-testid="public-phone-one-input" onChange={(event) => update("phoneOne", event.target.value)} value={draft.phoneOne} /></label>
        <label>Secondary phone<input data-testid="public-phone-two-input" onChange={(event) => update("phoneTwo", event.target.value)} value={draft.phoneTwo} /></label>
        <label>Instagram URL<input data-testid="public-instagram-input" onChange={(event) => update("instagram", event.target.value)} type="url" value={draft.instagram} /></label>
        <label>First co-founder<input data-testid="founder-one-name-input" onChange={(event) => update("founderOne", event.target.value)} value={draft.founderOne} /></label>
        <label>First co-founder role<input data-testid="founder-one-role-input" onChange={(event) => update("founderOneRole", event.target.value)} value={draft.founderOneRole} /></label>
        <label>Second co-founder<input data-testid="founder-two-name-input" onChange={(event) => update("founderTwo", event.target.value)} value={draft.founderTwo} /></label>
        <label>Second co-founder role<input data-testid="founder-two-role-input" onChange={(event) => update("founderTwoRole", event.target.value)} value={draft.founderTwoRole} /></label>
        <button className="button button-primary" data-testid="save-website-settings-button" type="submit"><Save size={16} /> Save website content</button>
      </form>
    </section>
  );
}