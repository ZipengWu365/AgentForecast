import React from "react";

const trustItems = [
  { label: "Open-source trust", value: "MIT + citation", copy: "Bright, legible, and built for scientific credibility." },
  { label: "Research velocity", value: "One command", copy: "Move from raw series to publishable outputs without glue code." },
  { label: "Cross-disciplinary fit", value: "Medicine to markets", copy: "Same product language across labs, benchmarks, and operations." },
  { label: "Agent-ready", value: "Structured JSON", copy: "Stable fields make tooling and automation straightforward." },
];

const featureCards = [
  {
    title: "White-first scientific UI",
    copy: "High readability, warm sunlight accents, and restrained blue keep the interface optimistic without looking soft.",
  },
  {
    title: "Productized research workflows",
    copy: "TSLab is framed like a premium technical product, not a loose collection of demos and plots.",
  },
  {
    title: "Ecosystem consistency",
    copy: "The same brand system can stretch across docs, README visuals, demos, dashboards, and benchmark pages.",
  },
  {
    title: "Designed for first 10 seconds",
    copy: "The hierarchy makes value obvious immediately: what it does, why it matters, and how to try it.",
  },
];

const workflow = [
  { step: "1. Load data", copy: "Bring a CSV, dataset id, or benchmark slice into the same product surface." },
  { step: "2. Compare or route", copy: "Pick a backend explicitly or let the system choose a sane default for the task." },
  { step: "3. Publish artifacts", copy: "Generate charts, cards, markdown, JSON, and reproducible outputs in one flow." },
];

const ecosystemRepos = [
  { name: "TSLab Core", role: "time series representation", accent: "sun" },
  { name: "TSLab Bench", role: "benchmark dashboards", accent: "science" },
  { name: "TSLab Symbolic", role: "symbolic regression and interpretable discovery", accent: "sun" },
  { name: "TSLab Agents", role: "agent-driven research tools", accent: "science" },
];

const demoCards = [
  { title: "Gold Forecaster Arena", label: "Markets", metric: "4 backends compared" },
  { title: "River Flood Risk Watch", label: "Climate", metric: "Daily public brief" },
  { title: "ICU Bed Stress", label: "Medicine", metric: "Streaming alert card" },
];

export default function TSLabLanding() {
  return (
    <div className="min-h-screen bg-white text-ink">
      <div className="bg-[radial-gradient(circle_at_top_left,rgba(255,244,194,0.7),transparent_28%),radial-gradient(circle_at_top_right,rgba(47,107,255,0.08),transparent_22%),#ffffff]">
        <header className="sticky top-0 z-20 border-b border-shell-border/90 bg-white/85 backdrop-blur-xl">
          <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-5 py-4 lg:px-8">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-sun to-sun-warm font-semibold text-ink shadow-soft">
                TS
              </div>
              <div>
                <div className="text-sm font-semibold tracking-tight">TSLab</div>
                <div className="text-xs text-ink-muted">Sunny scientific open source</div>
              </div>
            </div>
            <nav className="hidden items-center gap-5 text-sm text-ink-muted md:flex">
              <a href="#features" className="transition hover:text-ink">Features</a>
              <a href="#workflow" className="transition hover:text-ink">Workflow</a>
              <a href="#demos" className="transition hover:text-ink">Demos</a>
              <a href="#ecosystem" className="transition hover:text-ink">Ecosystem</a>
            </nav>
            <a
              href="#quickstart"
              className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-sun to-sun-warm px-4 py-2 text-sm font-semibold text-ink shadow-soft transition hover:-translate-y-0.5"
            >
              Try quickstart
            </a>
          </div>
        </header>

        <main className="mx-auto flex w-full max-w-7xl flex-col gap-7 px-5 py-8 lg:px-8 lg:py-10">
          <section className="grid gap-6 rounded-[28px] border border-shell-border/90 bg-sunrise-panel p-6 shadow-panel lg:grid-cols-[1.2fr,0.9fr] lg:p-8">
            <div>
              <div className="mb-4 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink-muted">
                <span className="h-2.5 w-2.5 rounded-full bg-sun shadow-[0_0_0_6px_rgba(255,200,61,0.18)]" />
                Research software, productized
              </div>
              <h1 className="max-w-[11ch] text-[clamp(2.75rem,6vw,5rem)] font-semibold leading-[0.96] tracking-[-0.045em] text-ink">
                Bright tools for serious technical work.
              </h1>
              <p className="mt-5 max-w-3xl text-[1.06rem] leading-7 text-ink-muted">
                TSLab is the white-background design language for your GitHub ecosystem: optimistic, scientifically strong,
                premium, and easy to scan. It is built for cross-disciplinary users who want research clarity, modern product
                polish, and agent-friendly workflows without dark-AI theater.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <a
                  href="#ecosystem"
                  className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-sun to-sun-warm px-5 py-3 font-semibold text-ink shadow-soft transition hover:-translate-y-0.5"
                >
                  Explore ecosystem
                </a>
                <a
                  href="#demos"
                  className="inline-flex items-center justify-center rounded-full border border-shell-border bg-white px-5 py-3 font-semibold text-ink transition hover:-translate-y-0.5 hover:border-shell-strong"
                >
                  View demo patterns
                </a>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <span className="rounded-full border border-sun/30 bg-sun-soft px-3 py-1.5 text-sm font-medium text-[#805400]">
                  white-background-first
                </span>
                <span className="rounded-full border border-shell-border bg-white px-3 py-1.5 text-sm font-medium text-ink-muted">
                  scientific confidence
                </span>
                <span className="rounded-full border border-science/15 bg-science-soft px-3 py-1.5 text-sm font-medium text-science">
                  agent-friendly outputs
                </span>
              </div>
            </div>

            <div className="rounded-[22px] border border-shell-border bg-white p-5 shadow-soft">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold tracking-tight text-ink">Launch snapshot</div>
                  <div className="text-sm text-ink-muted">How the ecosystem should feel in one glance.</div>
                </div>
                <span className="rounded-full border border-shell-border bg-shell-soft px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-ink-muted">
                  Public beta
                </span>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                {trustItems.slice(0, 4).map((item) => (
                  <div key={item.label} className="rounded-2xl border border-shell-border bg-shell-soft p-4">
                    <div className="text-sm text-ink-muted">{item.label}</div>
                    <div className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-ink">{item.value}</div>
                    <p className="mt-2 text-sm leading-6 text-ink-muted">{item.copy}</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 rounded-2xl border border-science/10 bg-[#F8FBFF] p-4 font-mono text-sm leading-6 text-[#17305E]">
                <div>pnpm install</div>
                <div>pnpm dev</div>
                <div className="mt-2 text-ink-muted">
                  Ship a white-first technical landing page with cards, quickstart, charts, and ecosystem links.
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {trustItems.map((item) => (
              <article key={item.label} className="rounded-[20px] border border-shell-border bg-shell-soft p-5 shadow-soft">
                <div className="text-sm text-ink-muted">{item.label}</div>
                <div className="mt-3 text-[1.7rem] font-semibold tracking-[-0.045em] text-ink">{item.value}</div>
                <p className="mt-2 text-sm leading-6 text-ink-muted">{item.copy}</p>
              </article>
            ))}
          </section>

          <section id="features" className="rounded-[28px] border border-shell-border bg-white p-6 shadow-soft lg:p-8">
            <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="mb-3 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink-muted">
                  <span className="h-2.5 w-2.5 rounded-full bg-sun" />
                  Core design logic
                </div>
                <h2 className="text-[clamp(2rem,3.5vw,2.8rem)] font-semibold tracking-[-0.045em] text-ink">
                  White, warm, technical, and immediately legible.
                </h2>
              </div>
              <p className="max-w-2xl text-[1.02rem] leading-7 text-ink-muted">
                The system is intentionally not dark, not cyberpunk, and not over-decorated. It should feel like a modern research lab
                with a product mindset: clean hierarchy, premium spacing, and a clear path from curiosity to action.
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {featureCards.map((card) => (
                <article key={card.title} className="rounded-2xl border border-shell-border bg-shell-soft p-5">
                  <h3 className="text-lg font-semibold tracking-[-0.03em] text-ink">{card.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-ink-muted">{card.copy}</p>
                </article>
              ))}
            </div>
          </section>

          <section id="workflow" className="grid gap-6 rounded-[28px] border border-shell-border bg-white p-6 shadow-soft lg:grid-cols-[1fr,0.95fr] lg:p-8">
            <div>
              <div className="mb-3 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink-muted">
                <span className="h-2.5 w-2.5 rounded-full bg-science" />
                Information architecture
              </div>
              <h2 className="text-[clamp(2rem,3.5vw,2.8rem)] font-semibold tracking-[-0.045em] text-ink">
                Explain the repo in 10 seconds, then earn depth.
              </h2>
              <p className="mt-4 max-w-2xl text-[1.02rem] leading-7 text-ink-muted">
                The page structure should move from hero to trust, then to workflow and proof. Technical users do not want decorative
                storytelling. They want fast comprehension, then evidence, then copy-paste action.
              </p>
              <div className="mt-6 grid gap-4 md:grid-cols-3">
                {workflow.map((item) => (
                  <article key={item.step} className="rounded-2xl border border-shell-border bg-shell-soft p-4">
                    <div className="text-base font-semibold tracking-[-0.03em] text-ink">{item.step}</div>
                    <p className="mt-2 text-sm leading-6 text-ink-muted">{item.copy}</p>
                  </article>
                ))}
              </div>
            </div>
            <div id="quickstart" className="rounded-[22px] border border-shell-border bg-shell-soft p-5">
              <div className="text-sm font-semibold uppercase tracking-[0.16em] text-ink-muted">Quickstart section</div>
              <div className="mt-4 rounded-2xl border border-science/10 bg-[#F8FBFF] p-4 font-mono text-sm leading-7 text-[#17305E]">
                <div>pip install tslib</div>
                <div>tslab demo --outdir outputs</div>
                <div>tslab compare gold.csv --backends ridge,xgboost,nhits</div>
              </div>
              <div className="mt-4 rounded-2xl border border-shell-border bg-white p-4">
                <div className="text-sm font-semibold text-ink">Code block style</div>
                <p className="mt-2 text-sm leading-6 text-ink-muted">
                  Use JetBrains Mono, soft blue panels, and just enough border contrast. Keep the CTA outside the code block.
                </p>
              </div>
            </div>
          </section>

          <section id="demos" className="rounded-[28px] border border-shell-border bg-white p-6 shadow-soft lg:p-8">
            <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="mb-3 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink-muted">
                  <span className="h-2.5 w-2.5 rounded-full bg-sun" />
                  Demo / screenshots
                </div>
                <h2 className="text-[clamp(2rem,3.5vw,2.8rem)] font-semibold tracking-[-0.045em] text-ink">
                  Demonstrate real outputs, not abstract claims.
                </h2>
              </div>
              <p className="max-w-2xl text-[1.02rem] leading-7 text-ink-muted">
                Each demo card should show one compelling output, one label, and one crisp metric. This is where trust becomes shareability.
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              {demoCards.map((card) => (
                <article key={card.title} className="overflow-hidden rounded-[22px] border border-shell-border bg-shell-soft shadow-soft transition hover:-translate-y-1 hover:shadow-panel">
                  <div className="h-40 bg-[linear-gradient(145deg,rgba(255,244,194,0.85),rgba(47,107,255,0.06))]" />
                  <div className="space-y-3 p-5">
                    <div className="flex items-center justify-between gap-3">
                      <span className="rounded-full border border-shell-border bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-ink-muted">
                        {card.label}
                      </span>
                      <span className="text-sm font-medium text-ink-muted">{card.metric}</span>
                    </div>
                    <h3 className="text-xl font-semibold tracking-[-0.035em] text-ink">{card.title}</h3>
                    <p className="text-sm leading-6 text-ink-muted">
                      Use bold visual evidence with clean card framing. Keep the preview simple enough to scan in a feed.
                    </p>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section id="ecosystem" className="rounded-[28px] border border-shell-border bg-white p-6 shadow-soft lg:p-8">
            <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="mb-3 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink-muted">
                  <span className="h-2.5 w-2.5 rounded-full bg-science" />
                  Ecosystem block
                </div>
                <h2 className="text-[clamp(2rem,3.5vw,2.8rem)] font-semibold tracking-[-0.045em] text-ink">
                  Multiple repos, one recognizable technical brand.
                </h2>
              </div>
              <p className="max-w-2xl text-[1.02rem] leading-7 text-ink-muted">
                This section is the ecosystem bridge. Keep it cleaner and flatter than the hero so it reads like a map of serious tools.
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {ecosystemRepos.map((repo) => {
                const accentClasses =
                  repo.accent === "sun"
                    ? "border-sun/35 bg-sun-soft text-[#805400]"
                    : "border-science/15 bg-science-soft text-science";
                return (
                  <article key={repo.name} className="rounded-2xl border border-shell-border bg-shell-soft p-5">
                    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] ${accentClasses}`}>
                      {repo.role}
                    </span>
                    <h3 className="mt-4 text-lg font-semibold tracking-[-0.03em] text-ink">{repo.name}</h3>
                    <p className="mt-2 text-sm leading-6 text-ink-muted">
                      Same design language, different technical purpose. The consistency should feel deliberate, not templated.
                    </p>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="rounded-[28px] border border-shell-border bg-white p-6 shadow-soft lg:p-8">
            <div className="flex flex-col gap-5 rounded-[24px] border border-shell-border bg-[linear-gradient(145deg,#FFFDF5,#FFFFFF)] p-6 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="mb-3 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink-muted">
                  <span className="h-2.5 w-2.5 rounded-full bg-sun" />
                  Final CTA
                </div>
                <h2 className="text-[clamp(1.9rem,3vw,2.5rem)] font-semibold tracking-[-0.045em] text-ink">
                  Build one bright research brand, not a pile of unrelated repo pages.
                </h2>
                <p className="mt-3 max-w-2xl text-[1.02rem] leading-7 text-ink-muted">
                  Keep the visuals clear, the claims honest, and the first-run path obvious. That combination will do more for open-source growth
                  than another decorative hero effect.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <a
                  href="#quickstart"
                  className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-sun to-sun-warm px-5 py-3 font-semibold text-ink shadow-soft transition hover:-translate-y-0.5"
                >
                  Use this template
                </a>
                <a
                  href="#ecosystem"
                  className="inline-flex items-center justify-center rounded-full border border-shell-border bg-white px-5 py-3 font-semibold text-ink transition hover:-translate-y-0.5 hover:border-shell-strong"
                >
                  Map the ecosystem
                </a>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
