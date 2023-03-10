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

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

import os
import subprocess
from switcher import Switcher

APPINDICATOR_ID = 'buntoappindicator'
dir_path = os.path.dirname(os.path.realpath(__file__))

def main():
    icon = f'{dir_path}/flag-white.png'
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath(icon), appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    gtk.main()


def build_menu():
    menu = gtk.Menu()
    item_action = gtk.MenuItem.new_with_label('Настройки')
    item_action.connect('activate', settings)
    menu.append(item_action)
    item_quit = gtk.MenuItem.new_with_label('Выход')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


def settings(source):
    pass


def quit(source):
    gtk.main_quit()

if __name__ == "__main__":
    # proc = subprocess.Popen(['sudo','python','switcher.py'])
    switcher = Switcher()
    switcher.start()
    main()
