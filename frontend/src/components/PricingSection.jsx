import { ArrowUpRight } from "lucide-react";

export default function PricingSection({ pricing = [] }) {
  return (
    <section className="pricing-section section-pad" data-testid="pricing-section">
      <div className="section-heading"><div><p className="eyebrow">Starting points</p><h2>Clear ranges for meaningful work.</h2></div></div>
      <div className="public-pricing-grid">
        {pricing.map((item, index) => (
          <article data-testid={`public-pricing-${index}`} key={item.name}>
            <span>{item.name}</span><strong>₹{Number(item.starting_at).toLocaleString()}+</strong><p>{item.note}</p><a data-testid={`pricing-contact-${index}`} href="#contact">Discuss scope <ArrowUpRight size={15} /></a>
          </article>
        ))}
      </div>
    </section>
  );
}