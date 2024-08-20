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

# settings = gtk.Settings.get_default()
# getting all existing properties #
# for i in settings.list_properties():
#    #print(i)
#    print(f'{i} == {settings.get_property(str(i.name))}')
# gtk_theme_name = settings.get_property('gtk-theme-name')
# settings.set_property("gtk-theme-name", gtk_theme_name)
# settings.set_property("gtk-application-prefer-dark-theme", True)
# settings.set_property("gtk-theme-name", "Numix")
# settings.set_property("gtk-application-prefer-dark-theme", False)


def main():
    icon = f'{DIR_PATH}/flag-white.png'
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath(
        icon), appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    gtk.main()


def build_menu():
    menu = gtk.Menu()
    item_title_version = gtk.MenuItem.new_with_label(f'Версия {VERSION}')
    item_title_version.connect('activate', show_log)
    ####
    menu.append(item_title_version)
    item_action = gtk.MenuItem.new_with_label('Настройки')
    item_action.connect('activate', show_settings)
    menu.append(item_action)
    ####
    item_quit = gtk.MenuItem.new_with_label('Выход')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu

def show_log(source):
    subprocess.run(['xdg-open', '/usr/share/bunto/error.log'])

def show_settings(source):
    subprocess.run(['xdg-open', '/usr/share/bunto/settings.py'])


def quit(source):
    switcher.terminate()
    while switcher.poll() is None:
        time.sleep(1) #0.2
    gtk.main_quit()


def quit_on_crash():
    while switcher.poll() is None:
        time.sleep(1)
    gtk.main_quit()


if __name__ == '__main__':
    command = f'sudo nice -n -15 python /usr/share/bunto/switcher.py'
    switcher = subprocess.Popen(command.split())

    thread = threading.Thread(
        target=quit_on_crash,
        daemon=True)
    thread.start()

    main()
