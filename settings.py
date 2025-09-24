VERSION = "25.09.25"

# Исправлять раскладку автоматически.
SWITCH_AUTO = True

# Исправлять раскладку по заданной клавише.
SWITCH_MANUAL = True

# Исправлять две заглавных в начале слова.
SWITCH_TWOCAPS = True

# Сочетание клавиш на которую в системе завязано переключение раскладки.
SYS_SWITCH_KEY = ["ctrl_left", "shift_left"]

# Символы кототрые являются признаком заверешения ввода слова.
# space = 57, tab = 15, enter = 28
# {'space': ' ', 'tab': '\t', 'enter': '\r\n'}
EOW_KEY_CODES = [57, 15, 28]

# Клавиши по которым происходит автоматическое переключение раскладки если SWITCH_AUTO = True.
ASWITCH_KEY_CODES = [57, 15] # space, tab

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