# Hosted gallery guide

`agentforecast` can now turn run directories into a static gallery.

## Fast path

```bash
python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site
```

## Build from your own runs

```bash
python -m agentforecast.cli build-gallery --runs-root outputs --site-dir public_gallery/site
```

## What you get

- `index.html`
- `feed.json`
- per-case HTML pages
- copied cards, charts, markdown, JSON, and CSV artifacts

This is meant for GitHub Pages or any basic static hosting.

## GitHub Pages deployment

The repository includes `.github/workflows/publish_gallery.yml` with the official Pages deployment chain:

- `actions/configure-pages`
- `actions/upload-pages-artifact`
- `actions/deploy-pages`

To make it live in GitHub:

1. Open repository `Settings -> Pages`
2. Set `Source` to `GitHub Actions`
3. Run the `publish-gallery` workflow once from the Actions tab

After that, scheduled runs can rebuild and redeploy the hosted gallery automatically.
