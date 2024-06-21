from enum import Enum

class Tectonics(Enum):
    Continental = 1
    Jovian = 2

class Atmosphere(Enum):
    none = 0
    Terran = 1
    Silicate = 2

class Ocean(Enum):
    none = 0
    Water = 1
    Acid = 2

# class SpectralType(Enum):
#     G2V = 1
#     B0V = 2
#     G5V = 3
#     M9V_T4 = 4,