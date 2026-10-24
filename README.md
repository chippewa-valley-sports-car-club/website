# fanout-ledger

The announcement ledger for [fanout](https://github.com/imkarrer/fanout): one
JSON line per item posted to each target. The website's deploy workflow
appends to `deliveries.jsonl` after each run and pushes this branch; it lives
apart from `main` so recording a delivery never triggers a deploy. Never edit
lines by hand: a line here is what stops an item being posted twice.
