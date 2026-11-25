# The World Today — 25 November 2026

[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/c/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/freezzard/news25-entry1/rank.svg)](https://make.fun/c/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/freezzard/news25-entry1/reward.svg)](https://make.fun/c/news-image-20261125)

One image that sums up the world's news of Wednesday 25 November 2026:
a dense broadsheet digest — 3 hero stories, a pinned world map with region
and subject tallies, 12 illustrated cards, a day-in-numbers strip, and 24
numbered briefs. 39 stories in all, across 6 regions.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

The program copies `entry.png` to `/output/entry.png` (or
`$MAKEFUN_OUTPUT_DIR/entry.png`) after verifying it byte by byte: PNG
signature, 1024x1024 IHDR, 8-bit RGB/RGBA, every chunk CRC, an IDAT chunk,
and the 1 MiB cap. It runs twice with identical bytes and uses no network.

`build_paint.py` is the painter that drew `entry.png` (Pillow, deterministic).
It is kept in the repository so the image can be rebuilt and inspected.

## The day in the image

- **Heroes:** Kyiv claims a drone strike on a Russian ship in the Gulf of
  Finland · Pakistan's first astronaut lifts off aboard Shenzhou-24 ·
  Nvidia slides as the AI rally stalls.
- **Cards:** the Houthi strike on Riyadh's tallest tower, Iran's blockade
  vow and the Hormuz tanker mines, the Gaza strike, Sarkozy's trial, the
  CIA/ODNI breach, Huawei's US verdict, Giuliani's Medal of Freedom,
  Abrego Garcia's departure, Baghdad's move on Kurdish oilfields, the
  Eskisehir helicopter crash, Spain's 20 weeks' leave, Israel's frozen
  coalition talks.
- **Briefs:** Nepal's quake, the UAE bus crash, AIDS deaths at a 20-year
  low, Hasina's planned return, the Rohingya returns, NATO's Poland
  deployment, Russia's record military budget, Kenya's eCitizen breach,
  Real Madrid 5-1 PSV, England's T20I win, and more.
