"""
Функции ​​сервера:​
- принимает ​с​ообщение ​к​лиента;
- формирует ​​ответ ​к​лиенту;
- отправляет ​​ответ ​к​лиенту;
- имеет ​​параметры ​к​омандной ​с​троки:
- -p ​​<port> ​-​ ​​TCP-порт ​​для ​​работы ​(​по ​у​молчанию ​​использует ​​порт ​​7777);
- -a ​​<addr> ​-​ ​I​P-адрес ​​для ​​прослушивания ​(​по ​у​молчанию ​с​лушает ​​все ​​доступные ​​адреса).
"""
import sys
import logging
import select
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from jim.config import *
from jim.core import Jim, JimMessage, JimResponse, JimContactList, JimAddContact, JimDelContact
from jim.exceptions import WrongInputError
from repo.server_models import session
from repo.server_repo import Repo
from repo.server_errors import ContactDoesNotExist

import log.server_log_config
from log.decorators import Log

# Получаем серверный логгер по имени, он уже объявлен в log_config и настроен
logger = logging.getLogger('server')
log = Log(logger)


class Handler:
    """Обработчик сообщений, тут будет основная логика сервера"""
    def __init__(self):
        # сохраняем репозиторий
        self.repo = Repo(session)


    def read_requests(self, r_clients, all_clients):
        """
        Чтение сообщений, которые будут посылать клиенты
        :param r_clients: клиенты которые могут отправлять сообщения
        :param all_clients: все клиенты
        :return:
        """
        # Список входящих сообщений
        messages = []

        for sock in r_clients:
            try:
                # Получаем входящие сообщения
                message = get_message(sock)
                # Добавляем их в список
                # В идеале нам нужно сделать еще проверку, что сообщение нужного формата прежде чем его пересылать!
                # Пока оставим как есть, этим займемся позже
                messages.append(message)
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)

        # Возвращаем словарь сообщений
        return messages

    @log
    def write_responses(self, messages, names, all_clients):
        """Отправляем сообщения либо конкретному пользователю, либо тому, кто ждет ответа"""

        for message, sock in messages:
            try:
                # теперь нам приходят разные сообщения, будем их обрабатывать
                action = Jim.from_dict(message)
                if action.action == GET_CONTACTS:
                    # нам нужен репозиторий
                    contacts = self.repo.get_contacts(action.account_name)
                    # формируем ответ
                    response = JimResponse(ACCEPTED, quantity=len(contacts))
                    # Отправляем
                    send_message(sock, response.to_dict())
                    # в цикле по контактам шлем сообщения
                    # отправляли в цикле и на клиенте иногда ловили ошибки
                    # for contact in contacts:
                    #     message = JimContactList(contact.Name)
                    #     print(message.to_dict())
                    #     send_message(sock, message.to_dict())
                    # отправляем одним списком
                    contact_names = [contact.Name for contact in contacts]
                    message = JimContactList(contact_names)
                    send_message(sock, message.to_dict())
                elif action.action == ADD_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.repo.add_contact(username, user_id)
                        # шлем удачный ответ
                        response = JimResponse(ACCEPTED)
                        # Отправляем
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        # формируем ошибку, такого контакта нет
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                        # Отправляем
                        send_message(sock, response.to_dict())
                elif action.action == DEL_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.repo.del_contact(username, user_id)
                        # шлем удачный ответ
                        response = JimResponse(ACCEPTED)
                        # Отправляем
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        # формируем ошибку, такого контакта нет
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')                            # Отправляем
                        send_message(sock, response.to_dict())
                elif action.action == MSG:
                    # получаем кому нужно отправить сообщение
                    to = action.to
                    # находим сокет этого клиента
                    client_sock = names[to]
                    # просто пересылаем туда сообщение
                    send_message(client_sock, action.to_dict())
            except WrongInputError as e:
                # Отправляем ошибку и текст из ошибки
                response = JimResponse(WRONG_REQUEST, error=str(e))
                send_message(sock, response.to_dict())
            except:  # Сокет недоступен, клиент отключился
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)

    @log
    def presence_response(self, presence_message):
        """
        Формирование ответа клиенту
        :param presence_message: Словарь presence запроса
        :return: Словарь ответа
        """
        # Делаем проверки
        try:
            presence = Jim.from_dict(presence_message)
            username = presence.account_name
            # сохраняем пользователя в базу если его там еще нет
            if not self.repo.client_exists(username):
                self.repo.add_client(username)
            # нам нужно связать имя пользователя и сокет

        except Exception as e:
            # Шлем код ошибки
            response = JimResponse(WRONG_REQUEST, error=str(e))
            return response.to_dict(), None
        else:
            # Если всё хорошо шлем ОК
            response = JimResponse(OK)
            # возвращаем еще имя пользователя
            return response.to_dict(), username


class Server:
    """Класс сервер"""

    def __init__(self, handler):
        """
        :param handler: обработчик событий
        """
        self.handler = handler
        # список клиентов
        self.clients = []
        # тут будут имена клиентов и их сокеты
        self.names = {}
        # сокет
        self.sock = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP

    def bind(self, addr, port):
        # запоминаем адрес и порт
        self.sock.bind((addr, port))

    def listen_forever(self):
        # запускаем цикл обработки событий много клиентов
        self.sock.listen(15)
        self.sock.settimeout(0.2)

        while True:
            try:
                conn, addr = self.sock.accept()  # Проверка подключений
                # получаем сообщение от клиента
                presence = get_message(conn)
                # формируем ответ
                response, client_name = self.handler.presence_response(presence)
                # отправляем ответ клиенту
                send_message(conn, response)
            except OSError as e:
                pass  # timeout вышел
            else:
                print("Получен запрос на соединение от %s" % str(addr))
                # Добавляем клиента в список
                self.clients.append(conn)
                # нам нужно связать имя клиента иего сокет
                self.names[client_name] = conn
                # проверим кто к нам подключился
                print('К нам подключился {}'.format(client_name))
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился

                requests = self.handler.read_requests(r, self.clients)  # Получаем входные сообщения
                self.handler.write_responses(requests, w, self.clients)  # Выполним отправку входящих сообщений


if __name__ == '__main__':
    try:
        addr = sys.argv[1]
    except IndexError:
        addr = ''
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 7777
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)

    handler = Handler()
    server = Server(handler)
    server.bind(addr, port)
    server.listen_forever()
