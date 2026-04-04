# public_gallery

This folder contains the static Pages output for the reviewed release.

Generate demo content and Pages docs:

```bash
python -m agentforecast.cli demo-gallery --outdir public_gallery/demo_runs --site-dir public_gallery/site
```

Build from existing runs:

```bash
python -m agentforecast.cli build-gallery --runs-root outputs --site-dir public_gallery/site
```

The generated site now includes:

- landing page
- gallery section
- install page
- why-agentforecast page
- backends page
- benchmarking page
- support-policy page
- JMLR paper entry page
