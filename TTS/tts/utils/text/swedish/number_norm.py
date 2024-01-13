import re
from typing import Dict

_point_number_re = re.compile(r"([0-9][0-9\.]+[0-9])")
_decimal_number_re = re.compile(r"([0-9]+\,[0-9]+)")
_currency_re = re.compile(r"(£|\$|¥|€)([0-9\,\.]*[0-9]+)")
_number_re = re.compile(r"-?[0-9]+")


def _remove_points(m):
    return m.group(1).replace(".", "")


def _expand_decimal_point(m):
    return m.group(1).replace(",", " komma ")


def __expand_currency(value: str, inflection: Dict[float, str]) -> str:
    parts = value.replace(".", "").split(",")
    if len(parts) > 2:
        return f"{value} {inflection[2]}"  # Unexpected format
    text = []
    integer = int(parts[0]) if parts[0] else 0
    if integer > 0:
        integer_unit = inflection.get(integer, inflection[2])
        text.append(f"{integer} {integer_unit}")
    fraction = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if fraction > 0:
        fraction_unit = inflection.get(fraction / 100, inflection[0.02])
        text.append(f"{fraction} {fraction_unit}")
    if len(text) == 0:
        return f"noll {inflection[2]}"
    return " ".join(text)


def _expand_currency(m: "re.Match") -> str:
    currencies = {
        "$": {
            0.01: "cent",
            0.02: "cents",
            1: "dollar",
            2: "dollars",
        },
        "€": {
            0.01: "cent",
            0.02: "cents",
            1: "euro",
            2: "euros",
        },
        "£": {
            0.01: "penny",
            0.02: "pence",
            1: "pound sterling",
            2: "pounds sterling",
        },
        "¥": {
            # TODO rin
            0.02: "sen",
            2: "yen",
        },
    }
    unit = m.group(1)
    currency = currencies[unit]
    value = m.group(2)
    return __expand_currency(value, currency)



def number_to_words(s):
    numbers = {
        0: "noll",
        1: "ett",
        2: "två",
        3: "tre",
        4: "fyra",
        5: "fem",
        6: "sex",
        7: "sju",
        8: "åtta",
        9: "nio",
        10: "tio",
        11: "elva",
        12: "tolv",
        13: "tretton",
        14: "fjorton",
        15: "femton",
        16: "sexton",
        17: "sjuton",
        18: "arton",
        19: "nitton",
    }
    tens = {
        2: "tjugo ",
        3: "tretti ",
        4: "fyrtio ",
        5: "femtio ",
        6: "sextio ",
        7: "sjuttio ",
        8: "åttio ",
        9: "nittio ",
    }
    num = int(s)

    text = ""
    if num > 999999:
        text += number_to_words(num // 1000000)
        text += " miljoner "
    num = num % 1000000

    if num > 999:
        text += number_to_words(num // 1000)
        text += " tusen "
    num = num % 1000

    if num > 99:
        text += number_to_words(num // 100)
        text += " hundra "
    num = num % 100

    if num < 20:
        return text + numbers[num]
    if num % 10 == 0:
        return text + tens[num // 10]
    return text + tens[num // 10] + numbers[num % 10]



def _expand_ordinal(m):
    return number_to_words(m.group(0))


def _expand_number(m):
    num = int(m.group(0))
    return number_to_words(num)

def normalize_numbers(text):
    text = re.sub(_point_number_re, _remove_points, text)
    text = re.sub(_currency_re, _expand_currency, text)
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = re.sub(_number_re, _expand_number, text)
    return text
