import { ArrowUpRight, Instagram, Mail, Phone } from "lucide-react";

const fallbackContact = {
  phones: ["+91 97740 90507", "+91 93628 23252"],
  email: "qwebliqofficial@gmail.com",
  instagram: "https://www.instagram.com/qwebliq",
};

export default function ContactSection({ contact = fallbackContact, onSubmit }) {
  const phones = contact.phones?.length ? contact.phones : fallbackContact.phones;
  const email = contact.email || fallbackContact.email;
  const whatsappNumber = phones[0].replace(/\D/g, "");

  return (
    <section className="contact-section section-pad" data-testid="contact-section" id="contact">
      <div className="contact-copy">
        <p className="eyebrow">Start a conversation</p>
        <h2>Let’s make your next digital chapter feel unmistakably yours.</h2>
        <div className="contact-routes" data-testid="contact-details">
          {phones.map((phone, index) => <a data-testid={`contact-phone-${index}-link`} href={`tel:${phone.replace(/\s/g, "")}`} key={phone}><Phone size={15} /> {phone}</a>)}
          <a data-testid="contact-email-link" href={`mailto:${email}`}><Mail size={15} /> {email}</a>
          <a data-testid="contact-instagram-link" href={contact.instagram || fallbackContact.instagram} rel="noreferrer" target="_blank"><Instagram size={15} /> @qwebliq</a>
        </div>
        <a className="whatsapp-link" data-testid="whatsapp-contact-link" href={`https://wa.me/${whatsappNumber}?text=Hello%20Qwebliq%2C%20I%20would%20like%20to%20discuss%20a%20project.`} rel="noreferrer" target="_blank">WhatsApp Qwebliq <ArrowUpRight size={16} /></a>
      </div>
      <form className="inquiry-form" data-testid="inquiry-form" onSubmit={onSubmit}>
        <input data-testid="inquiry-name-input" name="name" placeholder="Your name" required />
        <input data-testid="inquiry-email-input" name="email" placeholder="Email address" required type="email" />
        <input data-testid="inquiry-company-input" name="company" placeholder="Company or organisation" />
        <select data-testid="inquiry-budget-select" name="budget"><option value="">Indicative investment</option><option>₹50k–₹1L</option><option>₹1L–₹3L</option><option>₹3L+</option></select>
        <textarea data-testid="inquiry-message-input" minLength="10" name="message" placeholder="Tell us what you’re building" required />
        <button className="button button-primary" data-testid="inquiry-submit-button" type="submit">Send project note <ArrowUpRight size={17} /></button>
      </form>
    </section>
  );
}