"""Co sledujeme. Upravovat jen tady."""

# Hledané výrazy – začínáme úzce (časté a dobře obchodovatelné díly),
# rozšíříme po prvním týdnu podle toho, co se skutečně objevuje.
HLEDAT = [
    "motor 1.9 tdi",
    "motor 2.0 tdi",
    "prevodovka dsg",
    "turbo",
    "alu kola 17",
    "alu kola 18",
    "zimni kola",
    "xenon svetla",
    "led svetla",
    "navigace columbus",
    "navigace discover",
    "tazne zarizeni",
    "autobaterie",
    "diagnostika vag",
]

# Překlepy, které lidé v inzerátech dělají – takové kusy skoro nikdo nenajde.
PREKLEPY = [
    "skoda oktavia",
    "octavie",
    "pasat",
    "pasát",
    "wolkswagen",
    "merzedes",
    "mercedez",
    "hyundaj",
    "pežot",
    "peugot",
    "alfa romeo",  # kontrolní – správně psané, pro srovnání objemu
]

LOKALITA_PSC = "27351"   # Velké Přítočno – střed pro okruh
OKRUH_KM = 100
