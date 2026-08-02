import { ArrowDown, ArrowUpRight, CirclePlay } from "lucide-react";
import { motion } from "framer-motion";

export default function HeroScene() {
  return (
    <section className="hero" id="top" data-testid="hero-section">
      <div className="hero-noise" />
      <div className="hero-aurora aurora-one" />
      <div className="hero-aurora aurora-two" />
      <div className="hero-content">
        <motion.p
          animate={{ opacity: 1, y: 0 }}
          className="eyebrow"
          data-testid="hero-eyebrow"
          initial={{ opacity: 0, y: 16 }}
          transition={{ duration: 0.5 }}
        >
          Qwebliq LLP <span /> Crafted for Growth
        </motion.p>
        <motion.h1
          animate={{ opacity: 1, y: 0 }}
          data-testid="hero-heading"
          initial={{ opacity: 0, y: 30 }}
          transition={{ delay: 0.08, duration: 0.65 }}
        >
          Building digital experiences that <em>move</em> businesses.
        </motion.h1>
        <motion.p
          animate={{ opacity: 1, y: 0 }}
          className="hero-copy"
          data-testid="hero-description"
          initial={{ opacity: 0, y: 20 }}
          transition={{ delay: 0.16, duration: 0.6 }}
        >
          Qwebliq creates premium websites, powerful brands, and digital strategies that
          help businesses stand out, generate leads, and increase sales.
        </motion.p>
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="hero-actions"
          initial={{ opacity: 0, y: 20 }}
          transition={{ delay: 0.24, duration: 0.6 }}
        >
          <a className="button button-primary" data-testid="hero-start-project-link" href="#contact">
            Start your project <ArrowUpRight size={17} />
          </a>
          <a className="button button-ghost" data-testid="hero-view-work-link" href="#work">
            <CirclePlay size={17} /> View selected work
          </a>
        </motion.div>
      </div>
      <motion.div
        animate={{ opacity: 1, y: 0, rotate: -7 }}
        className="browser browser-primary"
        data-testid="hero-website-preview"
        initial={{ opacity: 0, y: 80, rotate: -12 }}
        transition={{ delay: 0.3, duration: 0.9 }}
      >
        <div className="browser-bar"><i /><i /><i /><b>qwebliq / studio</b></div>
        <div className="browser-body">
          <span className="browser-label">DESIGNED TO PERFORM</span>
          <strong>Progress has a shape.</strong>
          <div className="browser-chart"><span /><span /><span /><span /><span /></div>
        </div>
      </motion.div>
      <div className="hero-bottom">
        <span data-testid="hero-scroll-label">Scroll to explore</span>
        <a aria-label="Scroll to services" data-testid="hero-scroll-button" href="#services"><ArrowDown size={18} /></a>
      </div>
    </section>
  );
}