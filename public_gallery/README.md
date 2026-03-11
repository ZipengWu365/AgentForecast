# public_gallery

This folder is for static hosted output.

Generate demo content:

```bash
python -m agentforecast.cli demo-gallery --outdir public_gallery/demo_runs --site-dir public_gallery/site
```

Build from existing runs:

```bash
python -m agentforecast.cli build-gallery --runs-root outputs --site-dir public_gallery/site
```
