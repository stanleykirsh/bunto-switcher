VERSION = "26.01.01"

# Исправлять раскладку автоматически.
SWITCH_AUTO = True

# Исправлять раскладку по заданной клавише.
SWITCH_MANUAL = True

# Исправлять две заглавных в начале слова.
SWITCH_TWOCAPS = True

# Сочетание клавиш на которую в системе завязано переключение раскладки.
SYS_SWITCH_KEY = [29, 42] # ["ctrl_left", "shift_left"]

# Символы которые являются признаком заверешения ввода слова.
EOW_KEY_CODES = [
    '0000', # brake
    '0570', # space
    '0150', # tab
    '0280', # enter
    '0031', # " (cyr) 
    '0400', # " (lat) 
    '0401', # '
    '0101', # (
    '0111', # )
    '0130', # +
    '0131', # =
    ]

# Клавиши по которым происходит автоматическое переключение раскладки если SWITCH_AUTO = True.
ASWITCH_KEY_CODES = [57, 15] # 57: space, 15: tab, 28: enter

# Клавиши по которым происходит ручное переключение раскладки если SWITCH_MANUAL = True.
MSWITCH_KEY_CODES = [119] # pause

# Приложения исключения
APP_EXCEPTIONS = '''
firewatch
gnome_shell
'''

# Игнорировать автопереключение
IGNORE_WORDS = '''
dnf
gtk
gtk3
gtk4
gtk5
gtx
rx
hdd
zyltrc
'''