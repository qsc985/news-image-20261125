# news-image-20261125 — The World Today: Wednesday 25 November 2026

[![Bounty](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/qsc985/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/qsc985/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

A newspaper-front-page image summing up the world's news of
**Wednesday 25 November 2026**, drawn from scratch with Pillow.

## What the image shows

A one-page front page of a fictional paper, **THE WORLD TODAY**, dated
Wednesday 25 November 2026:

- **Lead — Cybersecurity, Washington:** hackers breached the CIA and the
  Office of the Director of National Intelligence's unclassified
  open-source network. No classified information was affected, officials
  say; who did it is not known.
- **Tech, New York:** a Brooklyn jury found Huawei guilty of stealing
  trade secrets — 10 of 12 counts, including bank fraud — clearing it of
  the top racketeering charge.
- **War in Ukraine, Kyiv:** President Zelenskyy confirmed Ukraine was
  behind the drone strike on the Russian cargo ship Sparta II in the Gulf
  of Finland; ally Norway urged caution.
- **Middle East, Riyadh:** a Houthi drone hit Riyadh's tallest tower, the
  385-metre Public Investment Fund tower, wounding 11 — the second strike
  on it in less than a week.
- **United States, Washington:** President Trump awarded Rudy Giuliani the
  Presidential Medal of Freedom.
- **Markets, New York:** Anthropic shares slid below their $83 IPO price,
  days after the record Nasdaq debut.
- **In Brief:** WHO evacuates health workers from an Ebola hospital in
  eastern Congo; Trump pardons the Thanksgiving turkeys; the Sarkozy
  corruption case goes to trial in France; Sweden's parliament votes on
  Kristersson staying PM. Plus the International Day for the Elimination
  of Violence against Women.

Every story is sourced in [SOURCES.md](SOURCES.md) with outlet, date and
link.

## Files

- `main.py` — the entry program (Python 3.13, standard library only).
  Verifies `entry.png` (valid PNG, 1024x1024, at most 1 MiB) and copies it
  to `$MAKEFUN_OUTPUT_DIR` (default `/output`) as `entry.png`.
- `render_news.py` — the renderer that draws `entry.png` from scratch
  with Pillow (build-time only; `main.py` does not need it).
- `entry.png` — the finished front page, 1024x1024.
- `SOURCES.md` — sourcing for every story in the image.
- `README.md` — this file.
- `LICENSE` — MIT.

## How to run it

```sh
# Re-draw the image (needs Pillow and the Liberation/DejaVu fonts):
python3 render_news.py

# Run the entry program:
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# -> out/entry.png
```

Running `main.py` twice produces byte-identical output: it copies the
bundled image unchanged.

## License

MIT — see [LICENSE](LICENSE).
