# cvscc.org

The Chippewa Valley Sports Car Club website: a [Hugo](https://gohugo.io)
static site, built and published by GitHub Pages from `main`.

- **Editing content:** club editors use Pages CMS forms; see
  `docs/editing-the-website.md` once it exists. What each form field means:
  [`docs/content-model.md`](docs/content-model.md).
- **Changing the site itself:**
  ```bash
  nix develop -c hugo server          # live preview at http://localhost:1313
  nix develop -c scripts/check.sh     # the proof CI runs; must end "check: PASS"
  ```
- **Autocross results:** put the timing data in `results-src/YYYY-MM-DD-<event>.tsv`
  (class, number, driver, car, best raw time, and a note for any amended
  result), keep `results-src/pax-YYYY.tsv` current, then
  ```bash
  nix develop -c python3 scripts/results-tables.py results-src/<event>.tsv content/results/<event>.md
  ```
  It writes the raw, PAX and by-class tables and the top-ten-on-PAX list.
  PAX times are truncated to 0.001, as AXWare does.
- **Deploys:** every push to `main`, and daily at 01:15 Central so "upcoming"
  and "next meeting" stay true (`.github/workflows/deploy.yml`).
- **Backlog:** `bd ready` in this repo. Beads labelled `delegate:local` are
  worked by [bead-loop](https://github.com/imkarrer/bead-loop)
  (`.bead-loop.toml`); rules for agents are in [`AGENTS.md`](AGENTS.md).
