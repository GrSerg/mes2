# Служебный скрипт запуска/останова нескольких клиентских приложений

from subprocess import Popen, CREATE_NEW_CONSOLE
import time

# список запущенных процессов
p_list = []

while True:
    user = input("Запустить сервер и клиентов (s) / Выйти (q)")

    if user == 's':
        # запускаем сервер
        # Запускаем серверный скрипт и добавляем его в список процессов
        p_list.append(Popen('python server.py',
                            creationflags=CREATE_NEW_CONSOLE))
        print('Сервер запущен')
        # ждем на всякий пожарный
        time.sleep(1)
        # запускаем консольного клиента

        # Запускаем клиентский скрипт и добавляем его в список процессов
        for i in range(2):
            p_list.append(Popen('python client_console.py localhost 7777 console{}'.format(i),
                                 creationflags=CREATE_NEW_CONSOLE))
        print('Консольне клиенты запущены')

        for i in range(2):
            # Запускаем клиентов с графическим интерфейсом
            p_list.append(Popen('python client_gui.py localhost 7777 Gui{}'.format(i),
                                creationflags=CREATE_NEW_CONSOLE))

        print('GUI клиенты запущены')
    elif user == 'q':
        print('Открыто процессов {}'.format(len(p_list)))
        for p in p_list:
            print('Закрываю {}'.format(p))
            p.kill()
        p_list.clear()
        print('Выхожу')
        break