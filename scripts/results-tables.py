#!/usr/bin/env python3
"""Build an autocross results page's tables from the timing data.

    flox activate -- python3 scripts/results-tables.py \\
        results-src/2026-08-23-fall-autocross.tsv content/results/2026-08-23-fall-autocross.md

Input: a tab-separated file with the columns class, number, driver, car, raw,
note (lines starting with # are comments). `raw` is the driver's best raw time,
or DNF. A non-empty `note` marks an amended result: the time gets an asterisk
and the note is printed under the tables.

PAX factors come from results-src/pax-<year>.tsv (the year is taken from the
input file's name). PAX time = raw x factor, truncated to 0.001, as
AXWare does (checked against the club's Spring 2026 sheet, all 44 rows).

Output: three tables (raw, PAX, by class) written into the results page
between <!-- results:start --> and <!-- results:end -->, and the page's
`highlights` (the top-ten table) set to the top ten on PAX. Everything else in
the page is left alone.
"""

from __future__ import annotations

import re
import sys
from decimal import ROUND_DOWN, Decimal
from pathlib import Path

START, END = "<!-- results:start -->", "<!-- results:end -->"


def read_tsv(path: Path) -> list[dict[str, str]]:
    lines = [l for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")]
    header = lines[0].split("\t")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        cells = line.split("\t")
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        if len(cells) > len(header):
            sys.exit(f"{path}: line {n} has {len(cells)} columns, expected {len(header)}")
        rows.append(dict(zip(header, (c.strip() for c in cells))))
    return rows


def time(s: str) -> Decimal | None:
    if s.upper() == "DNF":
        return None
    if not re.fullmatch(r"\d+\.\d{3}", s):
        sys.exit(f"bad time {s!r}: use seconds with three decimals, or DNF")
    return Decimal(s)


def fmt(t: Decimal | None) -> str:
    return "DNF" if t is None else f"{t:.3f}"


def build(entries: list[dict], pax: dict[str, dict]) -> tuple[str, list[dict]]:
    for e in entries:
        if e["class"] not in pax:
            sys.exit(f"class {e['class']!r} ({e['driver']}) has no factor in the PAX table")
        e["factor"] = Decimal(pax[e["class"]]["factor"])
        e["rawt"] = time(e["raw"])
        e["paxt"] = None if e["rawt"] is None else (e["rawt"] * e["factor"]).quantize(Decimal("0.001"), ROUND_DOWN)
        e["mark"] = "*" if e.get("note") else ""

    def key(field):
        return lambda e: (e[field] is None, e[field] or 0, e["driver"])

    by_raw = sorted(entries, key=key("rawt"))
    by_pax = sorted(entries, key=key("paxt"))
    order = {c: i for i, c in enumerate(pax)}

    out = []
    out.append("**Jump to:** [Raw times](#raw-times) · [PAX](#pax) · [By class](#by-class)\n")

    out.append("## Raw times\n")
    out.append("Every driver's best run, fastest first, regardless of class.\n")
    out.append("| Pos | Class | # | Driver | Car | Time |")
    out.append("| ---: | --- | ---: | --- | --- | ---: |")
    for i, e in enumerate(by_raw, 1):
        pos = i if e["rawt"] is not None else "–"
        out.append(f"| {pos} | {e['class']} | {e['number']} | {e['driver']} | {e['car']} | {fmt(e['rawt'])}{e['mark']} |")

    out.append("\n## PAX\n")
    out.append("Each best run multiplied by its class's PAX factor, so every class competes in one standing.\n")
    out.append("| Pos | Class | # | Driver | Car | Raw | Factor | PAX time |")
    out.append("| ---: | --- | ---: | --- | --- | ---: | ---: | ---: |")
    for i, e in enumerate(by_pax, 1):
        pos = i if e["paxt"] is not None else "–"
        out.append(f"| {pos} | {e['class']} | {e['number']} | {e['driver']} | {e['car']} | "
                   f"{fmt(e['rawt'])}{e['mark']} | {e['factor']:.3f} | {fmt(e['paxt'])}{e['mark']} |")

    out.append("\n## By class\n")
    out.append("Each class ranked on raw time.\n")
    for cls in sorted({e["class"] for e in entries}, key=lambda c: order[c]):
        members = [e for e in by_raw if e["class"] == cls]
        out.append(f"### {cls}: {pax[cls]['name']}\n")
        out.append("| Pos | # | Driver | Car | Time | Gap |")
        out.append("| ---: | ---: | --- | --- | ---: | ---: |")
        lead = members[0]["rawt"]
        for i, e in enumerate(members, 1):
            pos = i if e["rawt"] is not None else "–"
            gap = "" if e["rawt"] is None or i == 1 else f"+{e['rawt'] - lead:.3f}"
            out.append(f"| {pos} | {e['number']} | {e['driver']} | {e['car']} | {fmt(e['rawt'])}{e['mark']} | {gap} |")
        out.append("")

    notes = [e for e in entries if e["mark"]]
    if notes:
        out.append("### Amended results\n")
        for e in notes:
            pax_note = f" On PAX ({pax[e['class']]['name']}, {e['factor']:.3f}) that is {fmt(e['paxt'])}." if e["paxt"] else ""
            out.append(f"\\* **{e['driver']}** ({e['class']}, #{e['number']}): {e['note']}.{pax_note} "
                       "The downloadable timing sheet shows the original time.\n")
    if any(e["rawt"] is None for e in entries):
        out.append("DNF: did not finish.\n")
    return "\n".join(out).rstrip() + "\n", by_pax


def highlights(by_pax: list[dict]) -> str:
    def q(s):
        return '"' + s.replace('"', '\\"') + '"'
    lines = ["highlights:"]
    for i, e in enumerate([e for e in by_pax if e["paxt"] is not None][:10], 1):
        lines.append(f"  - {{place: {i}, class: {e['class']}, driver: {q(e['driver'])}, "
                     f"car: {q(e['car'])}, time: \"{fmt(e['paxt'])}{e['mark']}\"}}")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.exit(__doc__)
    src, page = Path(argv[1]), Path(argv[2])
    year = re.match(r"(\d{4})-", src.name)
    if not year:
        sys.exit(f"{src.name}: name it YYYY-MM-DD-<event>.tsv")
    pax_file = src.parent / f"pax-{year.group(1)}.tsv"
    pax = {r["class"]: r for r in read_tsv(pax_file)}
    tables, by_pax = build(read_tsv(src), pax)

    text = page.read_text()
    if START not in text or END not in text:
        sys.exit(f"{page}: add {START} and {END} where the tables go")
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    text = f"{before}{START}\n\n{tables}\n{END}{after}"
    text, n = re.subn(r"^highlights:\n(?:  .*\n)*", highlights(by_pax), text, count=1, flags=re.M)
    if n == 0:
        text = text.replace("\n---\n", "\n" + highlights(by_pax) + "---\n", 1)
    page.write_text(text)
    print(f"{page}: {len(by_pax)} entries, PAX leader {by_pax[0]['driver']} {fmt(by_pax[0]['paxt'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
