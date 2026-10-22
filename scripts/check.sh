#!/usr/bin/env bash
# The one proof a change is good: CI runs it on every PR, the bead loop runs it
# as its gate, and you can run it before you push.
#
#   flox activate -- scripts/check.sh
#
# 1. Every data file and the CMS config parse as YAML.
# 2. Hugo builds with warnings as errors, under a sub-path base URL, which is
#    how GitHub Pages serves a project site. A link that skips relURL breaks there.
# 3. Every internal link and asset in the built site resolves (lychee, offline).
set -euo pipefail
cd "$(dirname "$0")/.."

for tool in hugo lychee yq; do
  command -v "$tool" >/dev/null || { echo "missing $tool: run under 'flox activate -- scripts/check.sh'" >&2; exit 1; }
done

for f in data/*.yml .pages.yml; do
  [[ -e $f ]] || continue
  yq eval 'true' "$f" >/dev/null || { echo "check: $f is not valid YAML" >&2; exit 1; }
done

# AGENTS.md rule 2: Hugo 0.168 still accepts site.Data without a warning, so
# the build alone can't catch it.
if grep -rnE '(site|\.Site)\.Data|\.Site\.LanguageCode' layouts/; then
  echo "check: use hugo.Data and site.Language.Locale (AGENTS.md rule 2)" >&2; exit 1
fi

# AGENTS.md rule 5: `type` in front matter silently swaps the page's template.
if grep -rlE '^type:' content/; then
  echo "check: front matter must not set type: (an event's kind is event_type)" >&2; exit 1
fi

# AGENTS.md rule 3: relURL of "/x" resolves from the host root and drops the
# /website/ sub-path; the link check only sees links the sample content renders.
if grep -rnE '"/[^"]*" *\| *relURL|printf "/[^"]*"[^|]*\| *relURL' layouts/; then
  echo "check: relURL takes a path without a leading slash (\"events/\", not \"/events/\")" >&2; exit 1
fi

out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
hugo --gc --panicOnWarning --printPathWarnings --logLevel warn \
  --baseURL "http://localhost/website/" --destination "$out/website"

lychee --offline --no-progress --include-fragments --root-dir "$out" "$out/website"
echo "check: PASS"
