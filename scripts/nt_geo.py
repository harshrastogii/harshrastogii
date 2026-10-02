"""A stylised Northern Territory: outline, islands and the towns that light it up.

Coordinates are (longitude, latitude), deliberately simplified. The map is a
night-lights motif, not a survey product.
"""

COAST = [  # north coast, west (WA border) to east (QLD border)
    (129.00, -14.88), (129.35, -14.92), (129.70, -15.05), (129.78, -14.85),
    (129.58, -14.55), (129.40, -14.38), (129.50, -14.08), (129.70, -13.75),
    (129.88, -13.48), (130.15, -13.20), (130.27, -12.88), (130.55, -12.62),
    (130.78, -12.42), (130.92, -12.28), (131.08, -12.20), (131.32, -12.10),
    (131.65, -12.26), (132.10, -12.27), (132.42, -12.15), (132.56, -11.76),
    (132.22, -11.50), (132.16, -11.16), (132.60, -11.24), (132.78, -11.56),
    (133.20, -11.70), (133.62, -11.86), (134.20, -12.00), (134.70, -11.94),
    (135.10, -12.24), (135.50, -12.05), (135.90, -11.90), (136.40, -11.95),
    (136.70, -12.10), (136.92, -12.32), (136.62, -12.80), (136.12, -13.20),
    (135.92, -13.60), (135.86, -14.10), (135.52, -14.55), (135.46, -14.90),
    (135.90, -15.20), (136.30, -15.55), (136.75, -15.85), (137.20, -16.05),
    (137.60, -16.35), (138.00, -16.55),
]
BORDER = [(138.00, -26.00), (129.00, -26.00)]  # then back up the WA border

ISLANDS = [
    [(130.40, -11.45), (130.95, -11.30), (131.40, -11.40), (131.55, -11.65),
     (131.10, -11.85), (130.60, -11.80), (130.36, -11.70)],          # Melville
    [(129.95, -11.45), (130.32, -11.40), (130.34, -11.80), (130.14, -11.95),
     (129.85, -11.75)],                                              # Bathurst
    [(136.35, -13.75), (136.75, -13.70), (136.86, -14.05), (136.55, -14.25),
     (136.30, -14.05)],                                              # Groote Eylandt
]

# name, lon, lat, size (3 = regional centre, 2 = town, 1 = community)
TOWNS = [
    ("Darwin", 130.84, -12.46, 3), ("Katherine", 132.26, -14.47, 3),
    ("Tennant Creek", 134.19, -19.65, 3), ("Alice Springs", 133.88, -23.70, 3),
    ("Nhulunbuy", 136.78, -12.18, 2), ("Jabiru", 132.84, -12.67, 2),
    ("Yulara", 130.99, -25.24, 2), ("Borroloola", 136.30, -16.07, 2),
    ("Wadeye", 129.52, -14.24, 2), ("Maningrida", 134.23, -12.06, 2),
    ("Kalkarindji", 130.71, -17.43, 1), ("Ngukurr", 134.73, -14.73, 1),
    ("Elliott", 133.54, -17.55, 1), ("Hermannsburg", 132.78, -23.94, 1),
    ("Yuendumu", 131.80, -22.25, 1), ("Lajamanu", 130.64, -18.33, 1),
    ("Galiwinku", 135.57, -12.03, 1), ("Daly Waters", 133.37, -16.25, 1),
    ("Timber Creek", 130.48, -15.65, 1), ("Ali Curung", 134.33, -21.02, 1),
    ("Papunya", 131.92, -23.21, 1), ("Kintore", 129.38, -23.27, 1),
    ("Mataranka", 133.07, -14.92, 1), ("Numbulwar", 135.74, -14.27, 1),
    ("Alyangula", 136.42, -13.85, 1), ("Wurrumiyanga", 130.63, -11.76, 1),
    ("Pine Creek", 131.83, -13.82, 1), ("Batchelor", 131.03, -13.05, 1),
    ("Ti Tree", 133.42, -22.13, 1), ("Harts Range", 134.92, -22.97, 1),
    ("Finke", 134.58, -25.57, 1), ("Docker River", 129.10, -24.86, 1),
    ("Ramingining", 134.92, -12.33, 1), ("Minjilang", 132.62, -11.42, 1),
]

# A Stuart Highway "fibre" spine and radio spurs off it, in the spirit of Underlink.
BACKBONE = ["Darwin", "Batchelor", "Pine Creek", "Katherine", "Mataranka",
            "Daly Waters", "Elliott", "Tennant Creek", "Ali Curung", "Ti Tree",
            "Alice Springs", "Finke"]
SPURS = [
    ["Katherine", "Timber Creek", "Kalkarindji", "Lajamanu"],
    ["Darwin", "Jabiru", "Maningrida", "Ramingining", "Galiwinku", "Nhulunbuy"],
    ["Mataranka", "Ngukurr", "Numbulwar", "Alyangula"],
    ["Daly Waters", "Borroloola"],
    ["Batchelor", "Wadeye"],
    ["Alice Springs", "Hermannsburg", "Papunya", "Kintore", "Docker River"],
    ["Ti Tree", "Yuendumu"],
    ["Alice Springs", "Harts Range"],
    ["Hermannsburg", "Yulara"],
    ["Jabiru", "Minjilang"],
    ["Darwin", "Wurrumiyanga"],
]


def town(name):
    for t in TOWNS:
        if t[0] == name:
            return t
    raise KeyError(name)


def inside(lon, lat):
    """Point-in-polygon against the mainland outline."""
    poly = COAST + BORDER
    hit = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit
