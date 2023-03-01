from enum import Enum, auto


class Status(Enum):
    ACCEPTED = auto()
    DECLINED = auto()


class InterfixS(Enum):
    """Interfix used to form combinations in multiple languages"""

    # see https://ordia.toolforge.org/search?q=-s-
    sv = "L54926"
    da = "L34278"
    nb = "L589898"
    de = "L615991"
    nn = "L739937"
