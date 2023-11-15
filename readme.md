# Bunto Switcher

Программа для автоматического переключения между различными раскладками клавиатуры в Linux.

## Возможности

* Автоматическое исправление последнего текста набранного в неправильной раскладке.
* Исправление текста набранного в неправильной раскладке при нажатии горячей клавиши.
* Автоматическое исправление двух заглавных букв в начале слова.

Протестировано и работает в Fedora 38 + Gnome 44 + Wayland.

## Установка

Выполнить команду:

```
sudo ./install
```

Для нормальной работы необходимо отключить попап уведомление GNOME о смене раскладки. Для этого нужно установить расширение Quick Lang Switch\
Отсюда: https://extensions.gnome.org/extension/4559/quick-lang-switch/\
Или отсюда: https://github.com/ankostis/gnome-shell-quick-lang-switch

## Удаление

Выполнить команду

```
sudo ./uninstall
```
## Использование

Автоматическое исправление последнего набранного текста выполняется после завершения ввода слова после нажатия пробела или таба.

Ручное исправление последнего набранного текста выполняется при нажатии горячей клавиши [Pause / Break].

По умолчанию для работы приложения необходимо чтобы переключение раскладки в системе было настроено на сочетание [Ctrl + Shift]. Сочетание используемое приложением можно поменять в настройках.

## Зависимости

Устанавливаются автоматически установочным скриптом.

* evdev
* dbus-x11
* appindicator
