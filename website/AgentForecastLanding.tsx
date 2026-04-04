import React from "react";

const surfaces = [
  {
    title: "Pack surface",
    copy: "One small API for local forecasting, backend comparison, and publishable outputs.",
  },
  {
    title: "Research surface",
    copy: "Strict backend resolution through OnlineForecaster for benchmark-safe backtests.",
  },
  {
    title: "Artifact surface",
    copy: "CSV, plots, cards, markdown, metadata, and artifact manifests with explicit provenance.",
  },
  {
    title: "Agent surface",
    copy: "Stable tool and MCP payloads for humans, scripts, and agent workflows.",
  },
];

const links = [
  { label: "Install", href: "/install/" },
  { label: "Why AgentForecast", href: "/why-agentforecast/" },
  { label: "Backends", href: "/backends/" },
  { label: "Benchmarking", href: "/benchmarking/" },
  { label: "Support policy", href: "/support-policy/" },
  { label: "JMLR entry", href: "/papers/jmlr-mloss/" },
];

export default function AgentForecastLanding() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-8 lg:px-10">
        <header className="flex flex-wrap items-center justify-between gap-4 rounded-[28px] border border-slate-200 bg-[linear-gradient(145deg,rgba(255,255,255,0.98),rgba(250,250,250,0.98)),radial-gradient(circle_at_top_left,rgba(255,228,145,0.35),transparent_28%),radial-gradient(circle_at_top_right,rgba(47,107,255,0.08),transparent_22%)] p-5 shadow-[0_18px_60px_rgba(31,41,55,0.08)]">
          <div className="space-y-2">
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Reviewed release surface
            </div>
            <h1 className="max-w-3xl text-4xl font-semibold tracking-[-0.05em] text-slate-950 lg:text-6xl">
              Forecast to publish, without pretending to be a giant framework.
            </h1>
            <p className="max-w-3xl text-base leading-7 text-slate-600">
              AgentForecast is a forecast-to-publish layer over heterogeneous backends. It does not replace sktime,
              StatsForecast, MLForecast, or River. It gives you a smaller product surface, explicit artifact outputs,
              and benchmark-safe provenance.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-4">
            <div className="text-sm font-semibold text-slate-900">Install path</div>
            <pre className="mt-3 overflow-x-auto rounded-2xl border border-blue-100 bg-blue-50 p-4 text-sm text-blue-950">
{`python -m pip install .
python -m agentforecast.cli shoot sales --outdir demo`}
            </pre>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {surfaces.map((item) => (
            <article key={item.title} className="rounded-[22px] border border-slate-200 bg-slate-50 p-5 shadow-sm">
              <h2 className="text-lg font-semibold tracking-[-0.03em] text-slate-900">{item.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600">{item.copy}</p>
            </article>
          ))}
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Docs map</div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {links.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700 transition hover:-translate-y-0.5 hover:border-slate-300 hover:bg-white"
              >
                {item.label}
              </a>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
