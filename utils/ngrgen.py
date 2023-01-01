RUS_CHARS = """ё1234567890-=йцукенгшщзхъфывапролджэ\ячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"""
ENG_CHARS = """`1234567890-=qwertyuiop[]asdfghjkl;'\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?"""

def strcontain(string:str, chars:str):
    for char in chars:
        if char in string:
            return True
    return False

##############################################################
########################   RUS   #############################
##############################################################

with open("./data/91502280.txt", "r") as f:
    text = f.read()

text = text.lower()
text = text.replace("""\n""", '')
text = text.replace("""\xa0""", '')
text = text.replace("""\>""", '')
text = text.replace(""" *""", '')
text = text.replace("""   """, ' ')
text = text.replace("""  """, ' ')

preprocessed = ''
for char in text:
    _RUS_CHARS = RUS_CHARS + ' '
    _ENG_CHARS = ENG_CHARS + ' '
    if char in _RUS_CHARS and char not in ('0123456789'):
        preprocessed += _ENG_CHARS[_RUS_CHARS.find(char)]
text = preprocessed

# 1-грамы
print('# 1-грамы')
rugrams1 = []
for i in range(len(text)):
    string = text[i:i+3]
    if string[0] == ' ' and string[2] == ' ' and string[1].isalpha():
        rugrams1.append(string[1])
rugrams1 = list(set(rugrams1))

# 2-грамы
print('# 2-грамы')
rugrams2 = []
for i in range(len(text)):
    string = text[i:i+3]
    if len(string) < 3:
        continue
    if (string[0] == ' '
        and string[1] in ENG_CHARS
            and string[2] in ENG_CHARS):
        str12 = string[1:3]
        if not strcontain(str12, """-_!%*=+\|()<>?/"""):
            rugrams2.append(str12)
rugrams2 = list(set(rugrams2))

# 3-грамы
print('# 3-грамы')
rugrams3 = []
for i in range(len(text)):
    string = text[i:i+4]
    if len(string) < 4:
        continue
    if (string[0] == ' '
        and string[1] in ENG_CHARS
        and string[2] in ENG_CHARS
            and string[3] in ENG_CHARS):
        str14 = string[1:4]
        if not strcontain(str14, """-_!%*=+\|()<>?/"""):
            rugrams3.append(str14)
rugrams3 = list(set(rugrams3))

# 4-грамы
print('# 4-грамы')
rugrams4 = []
for i in range(len(text)):
    string = text[i:i+5]
    if len(string) < 5:
        continue
    if (string[0] == ' '
        and string[1] in ENG_CHARS
        and string[2] in ENG_CHARS
        and string[3] in ENG_CHARS
            and string[4] in ENG_CHARS):
        str15 = string[1:5]
        if not strcontain(str15, """-_!%*=+\|()<>?/"""):
            rugrams4.append(str15)
rugrams4 = list(set(rugrams4))

# 5-грамы
print('# 5-грамы')
rugrams5 = []
for i in range(len(text)):
    string = text[i:i+6]
    if len(string) < 6:
        continue
    if (string[0] == ' '
        and string[1] in ENG_CHARS
        and string[2] in ENG_CHARS
        and string[3] in ENG_CHARS
        and string[4] in ENG_CHARS
            and string[5] in ENG_CHARS):
        str16 = string[1:6]
        if not strcontain(str16, """-_!%*=+\|()<>?/"""):
            rugrams5.append(str16)
rugrams5 = list(set(rugrams5))

print(rugrams1, '\n', len(rugrams1))
print(rugrams2, '\n', len(rugrams2))
print(rugrams3, '\n', len(rugrams3))
print(rugrams4, '\n', len(rugrams4))
print(rugrams5, '\n', len(rugrams5))

##############################################################
########################   ENG   #############################
##############################################################

with open("./data/en-tbp.txt", "r") as f:
    text = f.read()

text = text.lower()
text = text.replace("""\n""", '')
text = text.replace("""\xa0""", '')
text = text.replace("""\>""", '')
text = text.replace(""" *""", '')
text = text.replace("""   """, ' ')
text = text.replace("""  """, ' ')

preprocessed = ''
for char in text:
    if char in (ENG_CHARS+' ') and not char.isdigit():
        preprocessed += char
text = preprocessed

# 1-грамы
print('# 1-грамы')
engrams1 = []
for i in range(len(text)):
    string = text[i:i+3]
    if string[0] == ' ' and string[2] == ' ' and string[1].isalpha():
        engrams1.append(string[1])
engrams1 = list(set(engrams1))

# 2-грамы
print('# 2-грамы')
engrams2 = []
for i in range(len(text)):
    string = text[i:i+3]
    if len(string) < 3:
        continue
    if (string[0] == ' '
        and string[1] in ENG_CHARS
            and string[2] in ENG_CHARS):
        str12 = string[1:3]
        if not strcontain(str12, """-_!%*=+\|()?/.,"""):
            engrams2.append(str12)
engrams2 = list(set(engrams2))

# 3-грамы
print('# 3-грамы')
engrams3 = []
for i in range(len(text)):
    string = text[i:i+4]
    if len(string) < 4:
        continue
    if (string[0] == ' '
        and string[1] in ENG_CHARS
        and string[2] in ENG_CHARS
            and string[3] in ENG_CHARS):
        str14 = string[1:4]
        if not strcontain(str14, """-_!%*=+\|()?/.,"""):
            engrams3.append(str14)
engrams3 = list(set(engrams3))

# 4-грамы
print('# 4-грамы')
engrams4 = []
for i in range(len(text)):
    string = text[i:i+5]
    if len(string) < 5:
        continue
    if (string[0] == ' '
        and string[1] in ENG_CHARS
        and string[2] in ENG_CHARS
        and string[3] in ENG_CHARS
            and string[4] in ENG_CHARS):
        str15 = string[1:5]
        if not strcontain(str15, """-_!%*=+\|()?/.,"""):
            engrams4.append(str15)
engrams4 = list(set(engrams4))

# 5-грамы
print('# 5-грамы')
engrams5 = []
for i in range(len(text)):
    string = text[i:i+6]
    if len(string) < 6:
        continue
    if (string[0] == ' '
        and string[1] in ENG_CHARS
        and string[2] in ENG_CHARS
        and string[3] in ENG_CHARS
        and string[4] in ENG_CHARS
            and string[5] in ENG_CHARS):
        str16 = string[1:6]
        if not strcontain(str16, """-_!%*=+\|()?/.,"""):
            engrams5.append(str16)
engrams5 = list(set(engrams5))

print(engrams1, '\n', len(engrams1))
print(engrams2, '\n', len(engrams2))
print(engrams3, '\n', len(engrams3))
print(engrams4, '\n', len(engrams4))
print(engrams5, '\n', len(engrams5))

##############################################################
########################  MATCH  #############################
##############################################################

result_ru = ''
result_en = ''

for engram in engrams1:
    if engram not in rugrams1:
        result_en += f'{engram}\n'

for rugram in rugrams1:
    if rugram not in engrams1:
        result_ru += f'{rugram}\n'
    if rugram in engrams1:
        _RUS_CHARS = RUS_CHARS + ' '
        _ENG_CHARS = ENG_CHARS + ' '
        rustr = ''
        for char in rugram:
            rustr += _RUS_CHARS[_ENG_CHARS.find(char)]
        print(rugram, rustr)

for engram in engrams2:
    if engram not in rugrams2:
        result_en += f'{engram}\n'

for rugram in rugrams2:
    if rugram not in engrams2:
        result_ru += f'{rugram}\n'
    if rugram in engrams2:
        _RUS_CHARS = RUS_CHARS + ' '
        _ENG_CHARS = ENG_CHARS + ' '
        rustr = ''
        for char in rugram:
            rustr += _RUS_CHARS[_ENG_CHARS.find(char)]
        print(rugram, rustr)

for engram in engrams3:
    if engram not in rugrams3:
        result_en += f'{engram}\n'

for rugram in rugrams3:
    if rugram not in engrams3:
        result_ru += f'{rugram}\n'
    if rugram in engrams3:
        _RUS_CHARS = RUS_CHARS + ' '
        _ENG_CHARS = ENG_CHARS + ' '
        rustr = ''
        for char in rugram:
            rustr += _RUS_CHARS[_ENG_CHARS.find(char)]
        print(rugram, rustr)

for engram in engrams4:
    if engram not in rugrams4:
        result_en += f'{engram}\n'

for rugram in rugrams4:
    if rugram not in engrams4:
        result_ru += f'{rugram}\n'
    if rugram in engrams4:
        _RUS_CHARS = RUS_CHARS + ' '
        _ENG_CHARS = ENG_CHARS + ' '
        rustr = ''
        for char in rugram:
            rustr += _RUS_CHARS[_ENG_CHARS.find(char)]
        print(rugram, rustr)

for engram in engrams5:
    if engram not in rugrams5:
        result_en += f'{engram}\n'

for rugram in rugrams5:
    if rugram not in engrams5:
        result_ru += f'{rugram}\n'
    if rugram in engrams5:
        _RUS_CHARS = RUS_CHARS + ' '
        _ENG_CHARS = ENG_CHARS + ' '
        rustr = ''
        for char in rugram:
            rustr += _RUS_CHARS[_ENG_CHARS.find(char)]
        print(rugram, rustr)

# рукотворные исключения
# [TBD] то что после хеша надо удалять из противоположного списка
# EN
result_en += """the\n"""   # еру
result_en += """pyt\n"""   # зне
result_en += """at\n"""    # фе
result_en += """no\n"""    # тщ
result_en += """if\n"""    # ша
result_en += """[]\n"""    # хъ

# RU
result_en += """k\n"""    # фе

with open("./data/ngrams-ru.txt", "w") as f:
    f.write(result_ru)

with open("./data/ngrams-en.txt", "w") as f:
    f.write(result_en)