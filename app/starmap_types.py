from enum import Enum

class Tectonics(Enum):
    Continental = 1
    Jovian = 2
    Mountains = 3
    Chaos = 4
    Ridges = 5
    Dunes = 6

class Atmosphere(Enum):
    none = 0
    Terran = 1
    Silicate = 2
    Martian = 3
    Venusian = 4
    Alkali = 5
    Neptunian = 6
    Steam = 7
    Jovian = 8
    Titanean = 9

class Ocean(Enum):
    none = 0
    Water = 1
    Acid = 2
    Lava = 3
    Air = 4

# class SpectralType(Enum):
#     G2V = 1
#     B0V = 2
#     G5V = 3
#     M9V_T4 = 4,