# prekupnik-dily

Sběrač inzerátů s autodíly z Bazoše, Sbazaru, Aukra a Annonce.
Běží zdarma na GitHub Actions každých 20 minut, ukládá do `data/inzeraty.sqlite`.
Aktuální stav: [data/STAV.md](data/STAV.md).

Co sledovat: `collectors/config.py`. Hlášení podhodnocených inzerátů přijde
po nasbírání referenčních cen (cca 14 dní).
