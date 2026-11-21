[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/zenganteng0987/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/zenganteng0987/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

A pure-stdlib Python program that draws an open passport spread for the
invented atoll republic of **Taluna** and writes `/output/entry.png`:
a data page with a vector-drawn portrait, full holder details and a
machine-readable zone (TD3, check digits computed per ICAO 9303), and a
visa page with entry and exit stamps from neighbouring invented
countries, a Vardos visa sticker, and a coral-route permit endorsement
that tells what kind of place Taluna is. No third-party imports, no
network, no fonts read from disk — all lettering comes from a 5x7
bitmap font embedded in the code, and the PNG is encoded by hand.

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` (and `./entry.png` when run locally).
