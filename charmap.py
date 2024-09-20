# space = 57, tab = 15, enter = 28
# {'space': ' ', 'tab': '\t', 'enter': '\r\n'}
_EOW_KEY_CODES = [57,15,28]

_KEY_MAP = {
    41: {'ru': 'ё', 'us': '`', 'ru_': 'Ё', 'us_': '~'},
    2: {'ru': '1', 'us': '1', 'ru_': '!', 'us_': '!'},
    3: {'ru': '2', 'us': '2', 'ru_': '"', 'us_': '@'},
    4: {'ru': '3', 'us': '3', 'ru_': '№', 'us_': '#'},
    5: {'ru': '4', 'us': '4', 'ru_': ';', 'us_': '$'},
    6: {'ru': '5', 'us': '5', 'ru_': '%', 'us_': '%'},
    7: {'ru': '6', 'us': '6', 'ru_': ':', 'us_': '^'},
    8: {'ru': '7', 'us': '7', 'ru_': '?', 'us_': '&'},
    9: {'ru': '8', 'us': '8', 'ru_': '*', 'us_': '*'},
    10: {'ru': '9', 'us': '9', 'ru_': '(', 'us_': '('},
    11: {'ru': '0', 'us': '0', 'ru_': ')', 'us_': ')'},
    12: {'ru': '-', 'us': '-', 'ru_': '_', 'us_': '_'},
    13: {'ru': '=', 'us': '=', 'ru_': '+', 'us_': '+'},
    43: {'ru': '\\', 'us': '\\', 'ru_': '/', 'us_': '|'},
    16: {'ru': 'й', 'us': 'q', 'ru_': 'Й', 'us_': 'Q'},
    17: {'ru': 'ц', 'us': 'w', 'ru_': 'Ц', 'us_': 'W'},
    18: {'ru': 'у', 'us': 'e', 'ru_': 'У', 'us_': 'E'},
    19: {'ru': 'к', 'us': 'r', 'ru_': 'К', 'us_': 'R'},
    20: {'ru': 'е', 'us': 't', 'ru_': 'Е', 'us_': 'T'},
    21: {'ru': 'н', 'us': 'y', 'ru_': 'Н', 'us_': 'Y'},
    22: {'ru': 'г', 'us': 'u', 'ru_': 'Г', 'us_': 'U'},
    23: {'ru': 'ш', 'us': 'i', 'ru_': 'Ш', 'us_': 'I'},
    24: {'ru': 'щ', 'us': 'o', 'ru_': 'Щ', 'us_': 'O'},
    25: {'ru': 'з', 'us': 'p', 'ru_': 'З', 'us_': 'P'},
    26: {'ru': 'х', 'us': '[', 'ru_': 'Х', 'us_': '{'},
    27: {'ru': 'ъ', 'us': ']', 'ru_': 'Ъ', 'us_': '}'},
    30: {'ru': 'ф', 'us': 'a', 'ru_': 'Ф', 'us_': 'A'},
    31: {'ru': 'ы', 'us': 's', 'ru_': 'Ы', 'us_': 'S'},
    32: {'ru': 'в', 'us': 'd', 'ru_': 'В', 'us_': 'D'},
    33: {'ru': 'а', 'us': 'f', 'ru_': 'А', 'us_': 'F'},
    34: {'ru': 'п', 'us': 'g', 'ru_': 'П', 'us_': 'G'},
    35: {'ru': 'р', 'us': 'h', 'ru_': 'Р', 'us_': 'H'},
    36: {'ru': 'о', 'us': 'j', 'ru_': 'О', 'us_': 'J'},
    37: {'ru': 'л', 'us': 'k', 'ru_': 'Л', 'us_': 'K'},
    38: {'ru': 'д', 'us': 'l', 'ru_': 'Д', 'us_': 'L'},
    39: {'ru': 'ж', 'us': ';', 'ru_': 'Ж', 'us_': ':'},
    40: {'ru': 'э', 'us': "'", 'ru_': 'Э', 'us_': '"'},
    44: {'ru': 'я', 'us': 'z', 'ru_': 'Я', 'us_': 'Z'},
    45: {'ru': 'ч', 'us': 'x', 'ru_': 'Ч', 'us_': 'X'},
    46: {'ru': 'с', 'us': 'c', 'ru_': 'С', 'us_': 'C'},
    47: {'ru': 'м', 'us': 'v', 'ru_': 'М', 'us_': 'V'},
    48: {'ru': 'и', 'us': 'b', 'ru_': 'И', 'us_': 'B'},
    49: {'ru': 'т', 'us': 'n', 'ru_': 'Т', 'us_': 'N'},
    50: {'ru': 'ь', 'us': 'm', 'ru_': 'Ь', 'us_': 'M'},
    51: {'ru': 'б', 'us': ',', 'ru_': 'Б', 'us_': '<'},
    52: {'ru': 'ю', 'us': '.', 'ru_': 'Ю', 'us_': '>'},
    53: {'ru': '.', 'us': '/', 'ru_': ',', 'us_': '?'}}

_KEY_MAP[57] = {'ru': ' ', 'us': ' ', 'ru_': ' ', 'us_': ' '} # space
_KEY_MAP[15] = {'ru': '\t', 'us': '\t', 'ru_': '\t', 'us_': '\t'} # tab
_KEY_MAP[28] = {'ru': '\r\n', 'us': '\r\n', 'ru_': '\r\n', 'us_': '\r\n'} # enter

_ASWITCH_KEY_CODES = [57, 15] # space, tab
_MSWITCH_KEY_CODES = [119] # pause