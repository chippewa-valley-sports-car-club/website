# Agent instructions: cvscc.org

A Hugo static site for the Chippewa Valley Sports Car Club, published by
GitHub Pages. Non-technical club members edit its content through Pages CMS
forms, so the content files are an interface: their shape is fixed in
`docs/content-model.md`.

## The proof

```bash
nix develop -c scripts/check.sh      # green ends with the line "check: PASS"
```

CI runs exactly this, and so does the bead loop's gate. Nothing is done red.
To look at a page, build into a scratch directory and read the HTML:
`nix develop -c hugo --quiet --destination /tmp/site && grep -n 'next-meeting' /tmp/site/index.html`.

## Rules

1. **Hugo only.** No theme, no npm, no JavaScript framework, no CSS
   framework. One stylesheet, `assets/css/main.css`. A few lines of vanilla
   JavaScript only when a bead asks for it.
2. **This is Hugo 0.163.** Write `hugo.Data.club`, never `site.Data` or
   `.Site.Data`, and `site.Language.Locale`, never `.Site.LanguageCode`. Both
   old spellings are deprecated, and the check treats warnings as errors.
3. **Every internal link goes through `relURL` or `.RelPermalink`.** The check
   builds under `/website/`, so a bare `href="/events/"` fails it.
4. **The content model is a contract.** Read keys exactly as
   `docs/content-model.md` names them. Every key not marked required may be
   missing or empty, so guard it with `with` or `if`. Never rename a key. A new
   key goes in the content model, in `.pages.yml` once that file exists, and in
   the template, all in the same change.
5. **Partials do one thing.** `layouts/partials/<thing>.html`, called with
   `{{ partial "<thing>.html" . }}`. Page types live in
   `layouts/<section>/list.html` and `layouts/<section>/single.html`.
6. **Accessible and mobile-first.** Semantic elements, alt text on images
   (fall back to the name), links that say where they go, and a layout that
   works at 360 px wide.
7. **Leave alone:** `.github/`, `flake.nix`, `flake.lock`, `scripts/check.sh`
   and `.beads/`, unless the bead says otherwise.

## Sample content

`content/events/example-autocross.md`, `content/results/example-autocross.md`
and `content/news/2026-10-22-discord.md` exist so every template has
something to render. Keep them until a bead says to remove them, and add
sample entries in the same spirit when a template needs one (a sample sponsor
belongs in `data/sponsors.yml`).
