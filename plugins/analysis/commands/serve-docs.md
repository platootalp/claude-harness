# Serve-Docs Command

Build the Astro documentation site and start the preview server.

## Usage
/serve-docs [--port PORT] [--build-only]

## Flags
- `--port PORT` — Specify the port (default: 4321)
- `--build-only` — Only build, do not start the preview server

## Examples
/serve-docs               → builds and serves on localhost:4321
/serve-docs --port 8080   → builds and serves on localhost:8080
/serve-docs --build-only  → only builds the static site

## Description
Builds the Astro site and starts the preview server for viewing generated documentation.

Steps:
1. Ensure the symlink exists: `cd plugins/analysis/site && npm run setup`
2. Install dependencies if needed: `cd plugins/analysis/site && npm install --legacy-peer-deps`
3. Build the site: `cd plugins/analysis/site && npm run build`
4. Serve the site: `cd plugins/analysis/site && npm run preview [--port PORT]`

The site serves generated docs from plugins/analysis/docs/ via the site/docs symlink.
