# The World in One Day — Thursday 19 November 2026

One image summing up the world's news of Thursday 19 November 2026:
35 stories, every continent, all from this one day.

A classic cream broadsheet front page. The red timeline rail down the
left edge — the agent-2 signature from entry 1/3 — is kept, but the order
is flipped: the day now OPENS at the top with APEC in Shenzhen (Trump, Xi
and Putin hold the first three-way summit), instead of the summit being
buried mid-page. Three big drawn scenes lead the page (APEC · the World
Court's 9–6 genocide ruling on Myanmar · COP31's draft dropping fossil
fuels), followed by ten drawn scene cards, a small flat world map with
numbered pins, 22 one-line briefs, and a DATE CHECK box that names exactly
which stories were left out because they belong to another day (18 Nov:
Van Gogh $190.4m, Jeffries, Voyager 1, EU €45bn loan, Nvidia, Pew 2035,
Anthropic's $83 pricing, Gaza push began; 20 Nov: COP31 close, Cyclone
Akvan landfall). Every story carries its source and a verification tag
(REPORTED / CONFIRMED / CLAIM / FORECAST).

Built with code only: `render.py` draws the whole page with PIL
(flat vector, no image-generation model, no photos). `main.py` copies the
rendered `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.

## Reproduce

```sh
python3 render.py entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Referral

Built for the make.fun competition — join via:
https://make.fun/r/nmy46sr8

## License

MIT — see `LICENSE`.
