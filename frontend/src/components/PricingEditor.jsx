import { Save } from "lucide-react";
import { useEffect, useState } from "react";

const labels = {
  website: "Growth website",
  ecommerce: "E-commerce",
  brand: "Brand system",
  growth: "Growth programme",
  social: "Social media marketing",
};

export default function PricingEditor({ settings, onSave }) {
  const [prices, setPrices] = useState({});
  const [perPage, setPerPage] = useState(0);
  const [rushMultiplier, setRushMultiplier] = useState(1.25);

  useEffect(() => {
    const calculator = settings?.calculator;
    if (calculator) {
      setPrices(calculator.base_prices);
      setPerPage(calculator.per_page);
      setRushMultiplier(calculator.rush_multiplier);
    }
  }, [settings]);

  function updatePrice(key, value) {
    setPrices((current) => ({ ...current, [key]: Number(value) }));
  }

  function submit(event) {
    event.preventDefault();
    const currentPricing = settings.pricing || [];
    const managedPricing = Object.entries(prices).map(([key, startingAt]) => {
      const existing = currentPricing.find((item) => item.name === labels[key]);
      return {
        name: labels[key],
        starting_at: startingAt,
        note: existing?.note || "Custom scope available",
      };
    });
    const customPricing = currentPricing.filter(
      (item) => !Object.values(labels).includes(item.name),
    );
    const pricing = [...managedPricing, ...customPricing];
    onSave({
      ...settings,
      calculator: { base_prices: prices, per_page: perPage, rush_multiplier: rushMultiplier },
      pricing,
    });
  }

  return (
    <section className="admin-editor" data-testid="pricing-editor">
      <div className="panel-heading">
        <div><p className="eyebrow">Pricing controls</p><h3>Set calculator ranges</h3></div>
      </div>
      <form className="editor-form" data-testid="pricing-editor-form" onSubmit={submit}>
        <div className="price-grid">
          {Object.entries(labels).map(([key, label]) => (
            <label key={key}>{label}<input data-testid={`price-${key}-input`} min="0" onChange={(event) => updatePrice(key, event.target.value)} type="number" value={prices[key] || 0} /></label>
          ))}
        </div>
        <label>Additional price per page<input data-testid="price-per-page-input" min="0" onChange={(event) => setPerPage(Number(event.target.value))} type="number" value={perPage} /></label>
        <label>Accelerated timeline multiplier<input data-testid="rush-multiplier-input" min="1" onChange={(event) => setRushMultiplier(Number(event.target.value))} step="0.05" type="number" value={rushMultiplier} /></label>
        <button className="button button-primary" data-testid="save-pricing-button" type="submit"><Save size={16} /> Save pricing rules</button>
      </form>
    </section>
  );
}