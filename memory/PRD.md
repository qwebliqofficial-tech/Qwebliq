## Qwebliq LLP — Product Record

### Original problem statement
Build a premium, future-forward digital agency platform for Qwebliq LLP that presents its
services and work, captures inquiries, and provides scalable admin and client workspaces.

### Architecture decisions
- React application with responsive public, admin, and client routes.
- FastAPI and MongoDB back end with modular public, authentication, and dashboard routers.
- JWT access and refresh cookies with admin/client roles, protected workspace APIs, password
  hashing, rate limiting, and an administrator-created client access flow.
- Content is stored in MongoDB for portfolio projects, feed posts, blog posts, inquiries, and
  newsletter subscribers. Public contact details remain intentionally editable until supplied.

### User personas
- Prospective client: explores capabilities, work, project estimate, FAQ, and inquiry form.
- Qwebliq administrator: manages content, leads, portfolio entries, feed updates, blog posts,
  and client access.
- Qwebliq client: sees an organised project space with status, timeline, files, and approvals.

### Core requirements (static)
- Premium black, white, electric-blue visual direction with restrained violet accents.
- General, accurate presentation of Tripura Darpan as a regional-media digital presence project.
- Public agency website, inquiry capture, cost calculator, FAQ search, newsletter, and feed.
- Admin dashboard and client dashboard foundations with secure authentication.

### Implemented — 2026-08-02
- Premium responsive public experience with animated hero, services, portfolio, proof points,
  calculator, latest updates, searchable FAQ, inquiry capture, and newsletter subscription.
- MongoDB-backed public content and lead flows; seeded Tripura Darpan content with a general
  description and live site link.
- Secure admin login, overview metrics, inquiry visibility, and forms to publish feed, blog,
  portfolio, and client accounts.
- Client portal route with project status, timeline, files, approvals, and communication actions.
- Dark/light preference, mobile navigation, responsive layouts, interaction test IDs, and
  accessibility-minded focus and reduced-motion styles.
- Added Smaranjit Saha (Co-Founder & Creative Director) and Diganta Bhowmik
  (Co-Founder & Technical Director) as the leadership team.
- Added Qwebliq’s supplied logo, Instagram profile, two direct phone routes, email contact, and
  WhatsApp project-conversation shortcut.

### Prioritized backlog
#### P0
- Add Qwebliq’s street address, business hours, and Google Maps destination when available.
- Replace temporary administrator credentials with owner-supplied credentials.

#### P1
- Attach clients to real projects, milestones, invoices, uploads, approvals, and files.
- Add full editing, deletion, scheduling, categories, and media management to CMS areas.
- Add exact Tripura Darpan services, outcomes, case-study gallery, and client quote when approved.

#### P2
- Integrate email delivery, media storage, analytics, meeting scheduling, live chat, and
  multi-language support.
- Build pricing controls, testimonials moderation, advanced SEO settings, and social interactions.

### Next tasks
1. Receive contact and administrator details.
2. Connect projects to clients and turn client portal actions into live workflows.
3. Add approved project case-study assets and real client feedback.
