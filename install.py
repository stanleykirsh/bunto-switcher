import os
import shutil
import pathlib
import subprocess
import distutils

print("Установка bunto switcher...")

# Определяем имя текущего пользователя.
print("Определяю текущего пользователя...")
username = os.environ['SUDO_USER']

# Удаляем папку.
print("Готовлю папку для приложения...")
dirpath = pathlib.Path("/usr/share/bunto")
if dirpath.exists() and dirpath.is_dir():
    shutil.rmtree(dirpath)

# Создаем папку.
pathlib.Path("/usr/share/bunto").mkdir(parents=True, exist_ok=True)

# Копируем файлы приложения.
print("Копирую файлы...")
distutils.dir_util.copy_tree("./", "/usr/share/bunto/")

# Добавляем приложение в обзор приложений.
print("Добавляю приложение в список программ...")
shutil.copy("./bunto.desktop", "/usr/share/applications/")

# Добавляем приложение в автозапуск.
print("Добавляю приложение в автозапуск...")
shutil.copy("./bunto.desktop", f"/home/{username}/.config/autostart/")

"""
# Устанавливаем зависимости
# релогин или перезагрузка может потребоваться после первого шага
# appindicator
result = subprocess.run("sudo dnf install gnome-shell-extension-appindicator".split(), stdout=subprocess.PIPE)
result = result.stdout.decode('utf-8')
print(result)

result = subprocess.run("gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com".split(), stdout=subprocess.PIPE)
result = result.stdout.decode('utf-8')
print(result)

# evdev
result = subprocess.run("sudo dnf makecache".split(), stdout=subprocess.PIPE)
result = result.stdout.decode('utf-8')
print(result)

result = subprocess.run("sudo dnf install python3-evdev.x86_64".split(), stdout=subprocess.PIPE)
result = result.stdout.decode('utf-8')
print(result)

# dbus-x11
result = subprocess.run("sudo dnf install dbus-x11 -y".split(), stdout=subprocess.PIPE)
result = result.stdout.decode('utf-8')
print(result)
"""

# Добавляем разрешение в nosudo если его еще нет.
print("Проверяю разрешение в nosudo...")

substr = "NOPASSWD: /usr/bin/nice"
sudoers = "/etc/sudoers"
need_update = True

with open(sudoers) as f:
    if substr in f.read():
        need_update = False
        print("Разрешение уже имеется...")
        print("Изменение nosudo не требуется...")
    else:        
        print("Разрешение отсутствует...")
        print("Добавляю разрешение...")

if need_update:
    with open(sudoers, "a") as f:
        f.write(f"{username} ALL=(ALL) NOPASSWD: /usr/bin/nice")

print("Готово!")
