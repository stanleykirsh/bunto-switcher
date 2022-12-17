#('EV_SYN', 0):
EV_SYNS = [
('SYN_REPORT', 0), 
('SYN_CONFIG', 1), 
('?', 4), 
('?', 17), 
('?', 21)] 

#('EV_KEY', 1):
EV_KEYS = [
('KEY_ESC',         'esc',          'esc',          1), 
('KEY_1',           '1',            '!',            2), 
('KEY_2',           '2',            '@',            3), 
('KEY_3',           '3',            '#',            4), 
('KEY_4',           '4',            '$',            5), 
('KEY_5',           '5',            '%',            6), 
('KEY_6',           '6',            '^',            7), 
('KEY_7',           '7',            '&',            8), 
('KEY_8',           '8',            '*',            9), 
('KEY_9',           '9',            '(',            10), 
('KEY_0',           '0',            ')',            11), 
('KEY_MINUS',       '-',            '_',            12), 
('KEY_EQUAL',       '=',            '+',            13), 
('KEY_BACKSPACE',   'backspace',    'backspace',    14), 
('KEY_TAB',         'tab',          'tab',          15), 
('KEY_Q',           'q',            'Q',            16), 
('KEY_W',           'w',            'W',            17), 
('KEY_E',           'e',            'E',            18), 
('KEY_R',           'r',            'R',            19), 
('KEY_T',           't',            'T',            20), 
('KEY_Y',           'y',            'Y',            21), 
('KEY_U',           'u',            'U',            22), 
('KEY_I',           'i',            'I',            23), 
('KEY_O',           'o',            'O',            24), 
('KEY_P',           'p',            'P',            25), 
('KEY_LEFTBRACE',   '[',            '{',            26), 
('KEY_RIGHTBRACE',  ']',            '}',            27), 
('KEY_ENTER',       'enter',        'enter',        28), 
('KEY_LEFTCTRL',    'ctrl',         'ctrl',         29), 
('KEY_A',           'a',            'A',            30), 
('KEY_S',           's',            'S',            31), 
('KEY_D',           'd',            'D',            32), 
('KEY_F',           'f',            'F',            33), 
('KEY_G',           'g',            'G',            34), 
('KEY_H',           'h',            'H',            35), 
('KEY_J',           'j',            'J',            36), 
('KEY_K',           'k',            'K',            37), 
('KEY_L',           'l',            'L',            38), 
('KEY_SEMICOLON',   ';',            ':',            39), 
('KEY_APOSTROPHE',  '\'',           '"',            40), 
('KEY_GRAVE',       '`',            '~',            41), 
('KEY_LEFTSHIFT',   'shift',        'shift',        42), 
('KEY_BACKSLASH',   '\\',           '|',            43), 
('KEY_Z',           'z',            'Z',            44), 
('KEY_X',           'x',            'X',            45), 
('KEY_C',           'c',            'C',            46), 
('KEY_V',           'v',            'V',            47), 
('KEY_B',           'b',            'B',            48), 
('KEY_N',           'n',            'N',            49), 
('KEY_M',           'm',            'M',            50), 
('KEY_COMMA',       ',',            '<',            51), 
('KEY_DOT',         '.',            '>',            52), 
('KEY_SLASH',       '/',            '?',            53), 
('KEY_RIGHTSHIFT',  'shift',        'shift',        54), 
('KEY_KPASTERISK',  '*',            '*',            55), 
('KEY_LEFTALT',     'alt',          'alt',          56), 
('KEY_SPACE',       'space',        'space',        57), 
('KEY_CAPSLOCK',    'caps lock',    'caps lock',    58), 
('KEY_F1',          'f1',           'f1',           59), 
('KEY_F2',          'f2',           'f2',           60), 
('KEY_F3',          'f3',           'f3',           61), 
('KEY_F4',          'f4',           'f4',           62), 
('KEY_F5',          'f5',           'f5',           63), 
('KEY_F6',          'f6',           'f6',           64), 
('KEY_F7',          'f7',           'f7',           65), 
('KEY_F8',          'f8',           'f8',           66), 
('KEY_F9',          'f9',           'f9',           67), 
('KEY_F10',         'f10',          'f10',          68), 
('KEY_NUMLOCK',     'num lock',     'num lock',     69), 
('KEY_SCROLLLOCK',  'scrol lock',   'scrol lock',   70), 
('KEY_KP7',         '7',            '7',            71), 
('KEY_KP8',         '8',            '8',            72), 
('KEY_KP9',         '9',            '9',            73), 
('KEY_KPMINUS',     '-',            '-',            74), 
('KEY_KP4',         '4',            '4',            75), 
('KEY_KP5',         '5',            '5',            76), 
('KEY_KP6',         '6',            '6',            77), 
('KEY_KPPLUS',      '+',            '+',            78), 
('KEY_KP1',         '1',            '1',            79), 
('KEY_KP2',         '2',            '2',            80), 
('KEY_KP3',         '3',            '3',            81), 
('KEY_KP0',         '0',            '0',            82), 
('KEY_KPDOT',       '.',            '.',            83), 
('KEY_ZENKAKUHANKAKU', '',          '',             85), 
('KEY_102ND',       '',             '',             86), 
('KEY_F11',         'f11',          'f11',          87), 
('KEY_F12',         'f12',          'f12',          88), 
('KEY_RO',          '',             '',             89), 
('KEY_KATAKANA',    '',             '',             90),
('KEY_HIRAGANA',    '',             '',             91),
('KEY_HENKAN',      '',             '',             92),
('KEY_KATAKANAHIRAGANA', '',        '',             93),
('KEY_MUHENKAN',    '',             '',             94),
('KEY_KPJPCOMMA',   '',             '',             95),
('KEY_KPENTER',     'enter',        'enter',        96),
('KEY_RIGHTCTRL',   'ctrl',         'ctrl',         97),
('KEY_KPSLASH',     '/',            '/',            98),
('KEY_SYSRQ',       'print screen', 'print screen', 99), 
('KEY_RIGHTALT',    'alt',          'alt',          100), 
('KEY_HOME',        'home',         'home',         102), 
('KEY_UP',          'up',           'up',           103), 
('KEY_PAGEUP',      'page up',      'page up',      104), 
('KEY_LEFT',        'left',         'left',         105), 
('KEY_RIGHT',       'right',        'right',        106), 
('KEY_END',         'end',          'end',          107),
('KEY_DOWN',        'down',         'down',         108), 
('KEY_PAGEDOWN',    'page down',    'page down',    109), 
('KEY_INSERT',      'insert',       'insert',       110), 
('KEY_DELETE',      'delete',       'delete',       111), 
#(['KEY_MIN_INTERESTING', 'KEY_MUTE'], '', 113),
('KEY_VOLUMEDOWN',  '',             '',             114), 
('KEY_VOLUMEUP',    '',             '',             115), 
('KEY_POWER',       '',             '',             116), 
('KEY_KPEQUAL',     '',             '',             117), 
('KEY_PAUSE',       'pause',        'pause',        119),
('KEY_KPCOMMA',     '',             '',             121), 
#(['KEY_HANGEUL', 'KEY_HANGUEL'], '', 122), 
('KEY_HANJA',       '',             '',             123), 
('KEY_YEN',         '',             '',             124), 
('KEY_LEFTMETA',    'windows',      'windows',      125), 
('KEY_RIGHTMETA',   'windows',      'windows',      126), 
('KEY_COMPOSE',     'menu',         'menu',         127), 
('KEY_STOP',        '',             '',             128), 
('KEY_AGAIN',       '',             '',             129), 
('KEY_PROPS',       '',             '',             130), 
('KEY_UNDO',        '',             '',             131), 
('KEY_FRONT',       '',             '',             132), 
('KEY_COPY',        '',             '',             133), 
('KEY_OPEN',        '',             '',             134), 
('KEY_PASTE',       '',             '',             135), 
('KEY_FIND',        '',             '',             136), 
('KEY_CUT',         '',             '',             137), 
('KEY_HELP',        '',             '',             138), 
('KEY_F13',         '',             '',             183), 
('KEY_F14',         '',             '',             184), 
('KEY_F15',         '',             '',             185), 
('KEY_F16',         '',             '',             186), 
('KEY_F17',         '',             '',             187), 
('KEY_F18',         '',             '',             188), 
('KEY_F19',         '',             '',             189), 
('KEY_F20',         '',             '',             190), 
('KEY_F21',         '',             '',             191), 
('KEY_F22',         '',             '',             192), 
('KEY_F23',         '',             '',             193), 
('KEY_F24',         '',             '',             194), 
('KEY_UNKNOWN',     '',             '',             240)]

#('EV_MSC', 4): 
EV_MSCS = [
('MSC_SCAN', 4)]

#('EV_LED', 17)
EV_LEDS = [
('LED_NUML', 0), 
('LED_CAPSL', 1), 
('LED_SCROLLL', 2), 
('LED_COMPOSE', 3), 
('LED_KANA', 4)]