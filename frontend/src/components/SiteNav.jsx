import { ArrowUpRight, Menu, Moon, Sun, X } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

export default function SiteNav({ isLight, onThemeToggle }) {
  const [open, setOpen] = useState(false);
  const links = [
    ["Services", "#services"],
    ["Work", "#work"],
    ["Insights", "#insights"],
    ["Contact", "#contact"],
  ];

  const closeMenu = () => setOpen(false);

  return (
    <header className="site-nav" data-testid="site-navigation">
      <a className="brand-mark" data-testid="home-brand-link" href="#top">
        <img
          alt="Qwebliq logo"
          className="brand-logo-image"
          data-testid="header-qwebliq-logo"
          src="https://customer-assets-lxgj4vgw.emergentagent.net/job_qwebliq-staging/artifacts/7s1or5s3_6b96f71e-538c-4696-85b3-c0fca5ab82be.png"
        />
        QWEBLIQ
      </a>
      <nav className={open ? "nav-links nav-open" : "nav-links"} data-testid="primary-navigation">
        {links.map(([label, href]) => (
          <a data-testid={`nav-${label.toLowerCase()}-link`} href={href} key={label} onClick={closeMenu}>
            {label}
          </a>
        ))}
        <Link data-testid="nav-dashboard-link" to="/login" onClick={closeMenu}>
          Workspace
        </Link>
      </nav>
      <div className="nav-actions">
        <button
          aria-label="Toggle theme"
          className="icon-button"
          data-testid="theme-toggle-button"
          onClick={onThemeToggle}
          type="button"
        >
          {isLight ? <Moon size={17} /> : <Sun size={17} />}
        </button>
        <a className="nav-cta" data-testid="nav-start-project-link" href="#contact">
          Start a project <ArrowUpRight size={16} />
        </a>
        <button
          aria-label="Toggle menu"
          className="menu-button"
          data-testid="mobile-menu-button"
          onClick={() => setOpen((value) => !value)}
          type="button"
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
    </header>
  );
}