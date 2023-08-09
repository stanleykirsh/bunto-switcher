RUS_CHARS = """ё1234567890-=йцукенгшщзхъфывапролджэ\ячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ, """
ENG_CHARS = """`1234567890-=qwertyuiop[]asdfghjkl;'\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>? """


def strcontain(string: str, chars: str):
    for char in chars:
        if char in string:
            return True
    return False

##############################################################
########################   RUS   #############################
##############################################################

# из результирующего файла ngrams-ru.txt надо вручную удалить все строки вида " ,", ", ", " , " и т.д.
# иначе из-за них срабатвает автопереключение после ввода запятой в правильной английской раскладке "hello, " => "руддщб".

with open("./data/mart-ru.txt", "r") as f:
    text = f.read()

# добавим исключения
text += """"""

text = text.lower()
text = text.replace("""\n""", '')
text = text.replace("""\xa0""", '')
text = text.replace("""\>""", '')
text = text.replace(""" *""", '')
text = text.replace("""   """, ' ')
text = text.replace("""  """, ' ')
text = text.replace('…', ' ')

text = text.lower()
list_to_replace = str(set(RUS_CHARS) - set("""ёйцукенгшщзхъфывапролджэячсмитьбю""")) + '–—«»"'
for char_to_replace in list_to_replace:
    text = text.replace(char_to_replace, ' ')
text = ' '.join(text.split())

ngrams_ru = []
for window_size in (2, 3, 4):
    for i in range(len(text)):
        wtext = text[i:i+window_size]

        isvalidchar = True
        for char in wtext:
            if char not in """ёйцукенгшщзхъфывапролджэячсмитьбю """:
                isvalidchar = False
                break
        if not isvalidchar:
            continue

        spcscnt =  wtext.count(' ')
        if len(wtext) == 2 and spcscnt == 2:
            continue
        if spcscnt == 0:
            ngrams_ru.append(wtext)
        if spcscnt == 1 and (wtext[0] == ' ' or wtext[-1] == ' '):
            ngrams_ru.append(wtext)
        if spcscnt == 2 and (wtext[0] == ' ' and wtext[-1] == ' '):
            ngrams_ru.append(wtext)
ngrams_ru = list(set(ngrams_ru))

result = []
for token in ngrams_ru:
    translitted = ''
    for char in token:
        translitted += ENG_CHARS[RUS_CHARS.find(char)]
    result.append(translitted)
ngrams_ru = result
#print(ngrams_ru)

##############################################################
########################   ENG   #############################
##############################################################

with open("./data/mart-en.txt", "r") as f:
    text = f.read()

text = text.lower()
text = text.replace("""\n""", '')
text = text.replace("""\xa0""", '')
text = text.replace("""\>""", '')
text = text.replace(""" *""", '')
text = text.replace("""   """, ' ')
text = text.replace("""  """, ' ')
text = text.replace('…', ' ')

text = text.lower()
list_to_replace = str(set(ENG_CHARS) - set("""qwertyuiopasdfghjklzxcvbnm"""))
for char_to_replace in list_to_replace:
    text = text.replace(char_to_replace, ' ')
text = ' '.join(text.split())

ngrams_en = []
for window_size in (2, 3, 4):
    for i in range(len(text)):
        wtext = text[i:i+window_size]

        isvalidchar = True
        for char in wtext:
            if char not in """qwertyuiopasdfghjklzxcvbnm """:
                isvalidchar = False
                break
        if not isvalidchar:
            continue

        spcscnt =  wtext.count(' ')
        if len(wtext) == 2 and spcscnt == 2:
            continue
        if spcscnt == 0:
            ngrams_en.append(wtext)
        if spcscnt == 1 and (wtext[0] == ' ' or wtext[-1] == ' '):
            ngrams_en.append(wtext)
        if spcscnt == 2 and (wtext[0] == ' ' and wtext[-1] == ' '):
            ngrams_en.append(wtext)
ngrams_en = list(set(ngrams_en))
#print(ngrams_en)

unique_ru = '\n'.join(list(set(ngrams_ru) - set(ngrams_en)))
unique_en = '\n'.join(list(set(ngrams_en) - set(ngrams_ru)))

'''
# добавим исключения
xtext = """python**at**the**, **. """
for word in xtext.split('**'):
    unique_ru.replace(word, '')

xtext = """"""
for word in xtext.split('**'):
    unique_en.replace(word, '')
'''

print(unique_ru)
print(unique_en)


with open("./data/ngrams-ru.txt", "w") as f:
    f.write(unique_ru)

with open("./data/ngrams-en.txt", "w") as f:
    f.write(unique_en)
