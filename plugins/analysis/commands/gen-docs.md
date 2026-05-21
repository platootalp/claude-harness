# Gen-Docs Command

Invoke the Doc Gen Agent to generate documentation for a codebase and build the search index.

## Usage
/gen-docs [target]

## Examples
/gen-docs src/auth/    → generates docs for the auth module
/gen-docs .            → generates docs for the entire project
/gen-docs              → generates docs for the entire project (default)

## Description
Runs the full documentation generation pipeline:
1. Invokes codebase-to-docs skill on the target
2. Verifies generated markdown in plugins/analysis/docs/
3. Builds the search index for the Astro site
4. Reports the number of docs generated

After running this command, use /serve-docs to view the generated documentation in a browser.
