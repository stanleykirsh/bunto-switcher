RUS_CHARS = 'ё1234567890-=йцукенгшщзхъфывапролджэ\\ячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,'
ENG_CHARS = '`1234567890-=qwertyuiop[]asdfghjkl;\'\\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?'

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
    if char in _RUS_CHARS and not char.isdigit():
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
        if str12.isalnum():
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
        if str14.isalnum():
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
        if str15.isalnum():
            rugrams4.append(str15)
rugrams4 = list(set(rugrams4))

print(rugrams4, '\n', len(rugrams4))

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
        if str14.isalnum():
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
        if str15.isalnum():
            engrams4.append(str15)
engrams4 = list(set(engrams4))

print(engrams4, '\n', len(engrams4))

##############################################################
########################  MATCH  #############################
##############################################################

for rugram in rugrams4:
    if rugram in engrams4:
        _RUS_CHARS = RUS_CHARS + ' '
        _ENG_CHARS = ENG_CHARS + ' '
        rustr = ''
        for char in rugram:
            rustr += _RUS_CHARS[_ENG_CHARS.find(char)]
        print(rugram, rustr)