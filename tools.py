import subprocess
import time
from parameters import RUS_CHARS, ENG_CHARS

score = []


def translit(string):
    result = ''
    for char in string:
        if char in RUS_CHARS:
            result += ENG_CHARS[RUS_CHARS.find(char)]
        else:
            result += char
    return result


def convert():

    with open("./data/nonexistent4gram-ru.txt", "r") as f:
        score = f.readlines()

    with open("./data/nonexistent4gram-ru-tran.txt", "w") as f:
        for s in score:
            f.write(translit(s))


def load_ngrams(filenames):
    result = []
    for filename in filenames:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\n') for line in f]
            result.extend(lines)
    return result


def distinct():
    ngrams_ru = load_ngrams((
        './data/nonexistent2gram-ru-tran.txt',
        './data/nonexistent3gram-ru-tran.txt',
        './data/nonexistent4gram-ru-tran.txt',
    ))
    ngrams_en = load_ngrams((
        './data/nonexistent2gram-en.txt',
        './data/nonexistent3gram-en.txt',
        './data/nonexistent4gram-en.txt',
    ))

    d0, d1 = [], []

    for i, a in enumerate(ngrams_ru):
        if a in ngrams_en:
            print(f'{i} : {a}')
            d0.append(a)

    for i, a in enumerate(ngrams_en):
        if a in ngrams_ru:
            print(f'{i} : {a}')
            d1.append(a)

    d = d0 + d1
    print(len(set(d)))
    print(set(d))

def test_gsettings():
    print(time.time())
    command = ['gsettings', 'get',
            'org.gnome.desktop.input-sources', 'sources']
    result = subprocess.run(command, capture_output=True, text=True, shell=False).stdout
    print(time.time())
    print(result[10:12])    

# convert()
# distinct()
# test_gsettings()