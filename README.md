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
- **Deploys:** every push to `main`, and daily at 01:15 Central so "upcoming"
  and "next meeting" stay true (`.github/workflows/deploy.yml`).
- **Backlog:** `bd ready` in this repo. Beads labelled `delegate:local` are
  worked by [bead-loop](https://github.com/imkarrer/bead-loop)
  (`.bead-loop.toml`); rules for agents are in [`AGENTS.md`](AGENTS.md).
