[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/nvtuananhh/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/nvtuananhh/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

# The World Today — Friday 20 November 2026

One image that sums up the world's news of Friday 20 November 2026:
38 dated stories in 7 regions, 5 illustrated leads, a dated 18–20 November
timeline, market numbers and a sources line. Every story carries its date
on the page; events from 19 November are marked 19 NOV.

`main.py` draws the whole front page at runtime with the Python standard
library only (no Pillow, no network, no clock, no randomness). It writes
`/output/entry.png` when `/output` exists, otherwise `entry.png` next to
itself. Two runs write byte-identical files (verified locally, including
`env -i`, no-network and `nobody` runs).

## Run

```sh
python3 main.py
```

Output: a 1024×1024 PNG, 241,308 bytes.

## Stories

Leads: the ICJ genocide ruling, the overnight Kyiv barrage, the Shenzhen
trilateral, Cyclone Akvan's landfall, and the global AI sell-off. Regions:
Europe, Asia-Pacific, Middle East, Africa, Americas, Markets + Tech, and
Life, Science + Sport. See `SOURCES.md` for the source of every story.
