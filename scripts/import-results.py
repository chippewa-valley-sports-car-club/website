#!/usr/bin/env python3
"""Turn an AXWare "Final Raw Time Results" PDF into results-src timing data.

    flox activate -- python3 scripts/import-results.py PDF > results-src/<event>.tsv
    flox activate -- python3 scripts/import-results.py --pending

With a PDF, print the TSV that scripts/results-tables.py reads.

With --pending (what CI runs after a CMS edit): for every results page whose
`results_file` is a PDF and that has no results-src/<page>.tsv yet, write the
TSV, build the tables, fill in an empty summary, and link the event page to its
results. An existing TSV is never overwritten, so hand amendments (the `note`
column) survive. If a PDF can't be imported, the page's `import_problem` says
why in plain words (the CMS shows it on the form and the page shows it under
the results), nothing else is written, and the next run tries again.

The PDF is checked against itself before anything is written: the row count
must equal "Timed Entries", rows must be numbered 1..N in raw-time order, the
"Diff." and "From 1st" columns must match the times. (Pos. is not checked:
AXWare fills it from the final standings, cones included.) Any mismatch stops with the row, so a
bad parse fails loudly instead of publishing wrong standings.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIME = r"\d+\.\d{3}"
ROW = re.compile(rf"^\s*(\d+)\s+(\d+)\s+([A-Z0-9]+)\s+(\d+)\s+(.+?)\s+({TIME}|DNF)\s+({TIME}|-*)\s+({TIME}|-*)\s*$")
YEAR = re.compile(r"\b(19|20)\d{2}\b")


def pdf_text(pdf: Path) -> str:
    if not pdf.exists():
        sys.exit(f"No such file: {pdf}")
    try:
        return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True,
                              capture_output=True, text=True).stdout
    except FileNotFoundError:
        raise RuntimeError("pdftotext is missing: run under `flox activate`") from None
    except subprocess.CalledProcessError:
        sys.exit(f"Couldn't open {pdf} as a PDF")


def split_driver_car(text: str, line: str) -> tuple[str, str]:
    # The PDF lays driver and car out in columns, but a long name pushes the
    # car up against it with one space. Prefer the column gap, else the car's
    # model year.
    parts = re.split(r"\s{2,}", text, maxsplit=1)
    if len(parts) == 2:
        driver, car = parts
    else:
        year = YEAR.search(text)
        if not year or year.start() == 0:
            sys.exit(f"can't tell the driver from the car in: {line.strip()}")
        driver, car = text[:year.start()], text[year.start():]
    return driver.strip(), car.strip().rstrip("/")


def parse(text: str) -> list[dict]:
    if "Final Raw Time Results" not in text:
        sys.exit("not an AXWare \"Final Raw Time Results\" PDF; export that report from AXWare")
    expected = re.search(r"Timed Entries:\s*(\d+)", text)
    rows = []
    for line in text.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        row, pos, cls, number, rest, raw, diff, first = m.groups()
        driver, car = split_driver_car(rest, line)
        rows.append({"row": int(row), "pos": int(pos), "class": cls, "number": number,
                     "driver": driver, "car": car, "raw": raw, "diff": diff, "first": first, "line": line})
    check(rows, int(expected.group(1)) if expected else None)
    return rows


def check(rows: list[dict], expected: int | None) -> None:
    def fail(r, why):
        sys.exit(f"row {r['row']}: {why}\n  {r['line'].strip()}")

    if not rows:
        sys.exit("found no result rows in the PDF")
    if expected is not None and len(rows) != expected:
        sys.exit(f"the PDF says {expected} timed entries but {len(rows)} rows parsed")
    timed = [r for r in rows if r["raw"] != "DNF"]
    lead = Decimal(timed[0]["raw"]) if timed else None
    prev = None
    for n, r in enumerate(rows, 1):
        if r["row"] != n:
            fail(r, f"expected row {n}")
        if r["raw"] == "DNF":
            prev = None
            continue
        t = Decimal(r["raw"])
        if prev is not None and t < prev:
            fail(r, "times are out of order")
        if Decimal(r["first"]) != t - lead:
            fail(r, f"From 1st says {r['first']}, the times say {t - lead:.3f}")
        if prev is not None and Decimal(r["diff"]) != t - prev:
            fail(r, f"Diff. says {r['diff']}, the times say {t - prev:.3f}")
        prev = t


def tsv(rows: list[dict], source: str) -> str:
    out = [f"# Imported from {source} by scripts/import-results.py; checked against its own",
           "# entry count and gaps. Amend a time by editing it and saying why in `note`.",
           "class\tnumber\tdriver\tcar\traw\tnote"]
    out += [f"{r['class']}\t{r['number']}\t{r['driver']}\t{r['car']}\t{r['raw']}\t" for r in rows]
    return "\n".join(out) + "\n"


def front_matter(page: Path) -> tuple[str, str]:
    text = page.read_text()
    m = re.match(r"---\n(.*?\n)---\n", text, re.S)
    if not m:
        sys.exit(f"{page}: no front matter")
    return m.group(1), text


def field(fm: str, name: str) -> str | None:
    m = re.search(rf"^{name}:[ \t]*(.*)$", fm, re.M)
    return m.group(1).strip().strip("\"'") or None if m else None


def set_field(page: Path, name: str, value: str | None) -> None:
    """Set (or with None, remove) one front-matter line."""
    fm, text = front_matter(page)
    rest = re.sub(rf"^{name}:.*\n", "", fm, flags=re.M)
    line = f"{name}: {json.dumps(value, ensure_ascii=False)}\n" if value is not None else ""
    page.write_text(text.replace(fm, rest + line, 1))


def explain(problem: str) -> str:
    """Say what went wrong, and what to do, for someone who isn't technical."""
    if "not an AXWare" in problem:
        return ("This file isn't AXWare's \"Final Raw Time Results\" report. Export that report "
                "from AXWare as a PDF and upload it in place of this one.")
    m = re.search(r"class '([^']+)' \(([^)]*)\) has no factor", problem)
    if m:
        return (f"Class {m.group(1)} (driven by {m.group(2)}) has no PAX factor for this year yet. "
                "Ask the club's tech lead to add it; the tables build on their own once it's there.")
    if "Couldn't open" in problem:
        return ("This file isn't a PDF the site can read. Export AXWare's \"Final Raw Time Results\" "
                "report as a PDF and upload that.")
    if "No such file" in problem:
        return "The uploaded results file can't be found. Upload it again and save."
    return (f"The numbers in the PDF don't add up ({problem.splitlines()[0]}). Export the report "
            "from AXWare again and re-upload it; if it still happens, ask the club's tech lead.")


def link_event(event: str | None, results: str) -> None:
    if not event:
        return
    # The CMS's pick list stores the event's path; older pages store its name.
    page = ROOT / "content" / "events" / f"{Path(event).stem}.md"
    if not page.exists():
        print(f"  note: event page {page.relative_to(ROOT)} not found; not linked")
        return
    fm, text = front_matter(page)
    if field(fm, "results"):
        return
    page.write_text(text.replace(fm, fm + f"results: content/results/{results}.md\n", 1))
    print(f"  linked {page.relative_to(ROOT)} to its results")


def pending() -> int:
    done = failed = 0
    for page in sorted((ROOT / "content" / "results").glob("*.md")):
        if page.name == "_index.md":
            continue
        fm, _ = front_matter(page)
        pdf = field(fm, "results_file")
        src = ROOT / "results-src" / f"{page.stem}.tsv"
        if not pdf or not pdf.lower().endswith(".pdf") or src.exists():
            continue
        print(f"{page.relative_to(ROOT)}: importing {pdf}")
        tables = ROOT / "assets" / "results" / f"{page.stem}.md"
        try:
            src.write_text(tsv(parse(pdf_text(ROOT / "static" / pdf)), f"static/{pdf}"))
            run = subprocess.run([sys.executable, str(ROOT / "scripts" / "results-tables.py"), str(src), str(page)],
                                 capture_output=True, text=True)
            if run.returncode:
                raise SystemExit(run.stderr.strip() or run.stdout.strip())
        except SystemExit as err:
            src.unlink(missing_ok=True)
            tables.unlink(missing_ok=True)
            print(f"  problem: {err}")
            set_field(page, "import_problem", explain(str(err)))
            failed += 1
            continue
        set_field(page, "import_problem", None)
        link_event(field(fm, "event"), page.stem)
        done += 1
    print(f"{done} results file(s) imported, {failed} with a problem")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--pending"]:
        return pending()
    if len(argv) != 2:
        sys.exit(__doc__)
    pdf = Path(argv[1])
    sys.stdout.write(tsv(parse(pdf_text(pdf)), str(pdf)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
