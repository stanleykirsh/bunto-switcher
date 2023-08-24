# Bunto Switcher

Программа для автоматического переключения между различными раскладками клавиатуры в Linux.

* Автоматическое исправление текста набранного в неправильной раскладке.
* Автоматическое исправление двух заглавных букв в начале слова.
* Переключение языка последнего набранного текста при нажатии горячей клавиши.

Протестировано и работает в Fedora 38 + Gnome 44 + Wayland.

## Установка

Выполнить команду:

```
sudo ./install
```

## Удаление

Выполнить команду

```
sudo ./uninstall
```
## Использование

Автоматическое исправление последнего набранного текста выполняется после завершения ввода слова после нажатия пробела или таба.<br>
Ручное переключение выполняется при нажатии горячей клавиши Pause / Break.

## Зависимости

Устанавливаются автоматически установочным скриптом.

* evdev
* dbus-x11
* appindicator
