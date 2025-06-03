#!/usr/bin/env python

# Для правильной работы требуется установить расширение
# https://extensions.gnome.org/extension/615/appindicator-support/
# https://github.com/ubuntu/gnome-shell-extension-appindicator
#
# Возможно будет достаточно просто установить пакет libappindicator-*
# https://packages.fedoraproject.org/pkgs/libappindicator/libappindicator/
# sudo dnf install libappindicator-gtk3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

import os
import time
import threading
import subprocess
from settings import VERSION
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

APPINDICATOR_ID = 'buntoappindicator'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
SWITCHER_COMMAND = 'sudo nice -n -18 python /usr/share/bunto/switcher.py'


class SwitcherProcess:
    def __init__(self):
        self.process = None
        self.AWAIT_TERMINATE = False

    def start(self):
        """Перед запуском убеждаемся что ни один экземпляр SwitcherProcess не запущен."""
        if not self.is_running():
            self.process = subprocess.Popen(SWITCHER_COMMAND.split())

    def terminate(self):
        if self.process:
            self.AWAIT_TERMINATE = True
            self.process.terminate()
            while self.is_running():
                time.sleep(0.1)
            self.AWAIT_TERMINATE = False

    def is_running(self):
        return bool(self.process and self.process.poll() is None)

def show_log(source):
    """Открыть лог файл."""
    subprocess.run(['xdg-open', '/usr/share/bunto/error.log'])


def show_settings(source):
    """Открыть настройки."""
    subprocess.run(['xdg-open', '/usr/share/bunto/settings.py'])


def close(source):
    """Выход из приложения."""
    switcher_process.terminate()
    gtk.main_quit()


def build_menu():
    """"""
    menu = gtk.Menu()
    ####
    item_title_version = gtk.MenuItem.new_with_label(f'Версия {VERSION}')
    item_title_version.connect('activate', show_log)
    menu.append(item_title_version)
    ####
    item_action = gtk.MenuItem.new_with_label('Настройки')
    item_action.connect('activate', show_settings)
    menu.append(item_action)
    ####
    item_close = gtk.MenuItem.new_with_label('Выход')
    item_close.connect('activate', close)
    menu.append(item_close)
    ####
    menu.show_all()
    return menu


def main():
    """"""
    icon_path = f'{DIR_PATH}/flag-white.png'
    indicator = appindicator.Indicator.new(
        APPINDICATOR_ID, os.path.abspath(icon_path),
        appindicator.IndicatorCategory.APPLICATION_STATUS)

    thread = threading.Thread(target=restart_switcher)
    thread.daemon = True
    thread.start()

    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    gtk.main()


def restart_switcher():
    """Это watchdog.
    Пытаемся перезапустиь процесс switcher в отдельном потоке раз в секунду.
    Перед запуском убеждаемся что еще ни один экземпляр процесса не запущен.
    """
    while True:
        switcher_process.start()
        time.sleep(1)


def check_running():
    """Проверяем что приложение еще не запущено и запрещаем повторный запуск.
    """
    path = f'{DIR_PATH}/main.py'    
    command = 'ps -e -o cmd= | grep bunto'
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True)
    result = result.stdout# .splitlines()

    if result.count(path) > 1:
        quit()
    else:
        return

if __name__ == '__main__':
    check_running()
    switcher_process = SwitcherProcess()
    main()
