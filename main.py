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

from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk as gtk

from settings import VERSION

import subprocess
import threading
import time
import os


APPINDICATOR_ID = 'buntoappindicator'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
SWITCHER_COMMAND = f'sudo nice -n -15 python /usr/share/bunto/switcher.py'


class SwitcherProcess:
    def __init__(self):
        self.process = None
        self.TERMINATE = False

    def start(self):
        """Перед запуском убеждаемся что ни один экземпляр SwitcherProcess не запущен."""
        if (not switcher_process.TERMINATE
            and (not switcher_process.process
                 or switcher_process.process.poll() is not None)):
            self.process = subprocess.Popen(SWITCHER_COMMAND.split())
    
    def terminate(self):
        if switcher_process.process:
            switcher_process.TERMINATE = True
            switcher_process.process.terminate()
            while switcher_process.process.poll() is None:
                time.sleep(0.1)


def show_log(source):
    """Открыть лог файл."""
    subprocess.run(['xdg-open', '/usr/share/bunto/error.log'])


def show_settings(source):
    """Открыть настройки."""
    subprocess.run(['xdg-open', '/usr/share/bunto/settings.py'])


def quit(source):
    """Выход из приложения."""
    switcher_process.terminate()
    gtk.main_quit()


def build_menu():
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
    item_quit = gtk.MenuItem.new_with_label('Выход')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    ####
    menu.show_all()
    return menu


def main():

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
    """Перезапустить процесс switcher."""
    """Перед запуском убеждаемся что еще ни один экземпляр процесса не запущен."""
    while True:
        if (not switcher_process.TERMINATE
            and (not switcher_process.process
                 or switcher_process.process.poll() is not None)):
            switcher_process.start()
        time.sleep(1)


if __name__ == '__main__':
    switcher_process = SwitcherProcess()
    main()
