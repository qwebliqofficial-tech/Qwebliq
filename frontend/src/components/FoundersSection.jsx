const defaultFounders = [
  {
    name: "Smaranjit Saha",
    role: "Co-Founder & Creative Director",
    focus: ["Creative direction", "UI/UX", "Brand strategy"],
  },
  {
    name: "Diganta Bhowmik",
    role: "Co-Founder & Technical Director",
    focus: ["Development", "Architecture", "Scalable systems"],
  },
];

export default function FoundersSection({ founders = defaultFounders }) {
  return (
    <section className="founders-section section-pad" data-testid="founders-section">
      <div className="section-heading founders-heading">
        <div>
          <p className="eyebrow">Built with intention</p>
          <h2>Two disciplines. One digital standard.</h2>
        </div>
        <img
          alt="Qwebliq logo"
          className="founder-logo"
          data-testid="founders-qwebliq-logo"
          src="https://customer-assets-lxgj4vgw.emergentagent.net/job_qwebliq-staging/artifacts/7s1or5s3_6b96f71e-538c-4696-85b3-c0fca5ab82be.png"
        />
      </div>
      <div className="founders-grid">
        {founders.map((founder, index) => (
          <article className="founder-card" data-testid={`founder-card-${index}`} key={founder.name}>
            <span className="founder-number">0{index + 1}</span>
            <h3>{founder.name}</h3>
            <p>{founder.role}</p>
            <div className="founder-focus">
              {founder.focus.map((item) => (
                <span data-testid={`founder-${index}-focus-${item}`} key={item}>
                  {item}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}