class Units:
    ms = 1
    s = ms * 1000
    m = s * 60
    h = m * 60
    d = h * 24
    w = d * 7

    @classmethod
    def fromstring(cls, string):
        return getattr(cls, string.lower(), None)


def string_to_ms(string):
    unit = string[-1:]
    value = int(string[:-1])
    return int(value * Units.fromstring(unit))
