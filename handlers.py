from jim.config import MESSAGE
from PyQt5.QtCore import QObject, pyqtSignal
from jim.utils import get_message
from jim.core import Jim, JimResponse, JimMessage
from jim.exceptions import WrongParamsError, ToLongError, WrongActionError, WrongDictError, ResponseCodeError
from jim.config import *


class Receiver:
    ''' Класс-получатель информации из сокета
    '''

    def __init__(self, sock, request_queue):
        # запоминаем очередь ответов
        self.request_queue = request_queue
        # запоминаем сокет
        self.sock = sock
        self.is_alive = False

    def process_message(self, message):
        """метод для обработки принятого сообщения, будет переопределен в наследниках"""
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            data = get_message(self.sock)
            try:
                # Преобразуем словарь в Jim, Это может быть action, а может быть response
                jm = Jim.from_dict(data)

                # Если это сообщение
                if isinstance(jm, JimMessage):
                    # мы его обрабатываем
                    self.process_message(jm)
                else:
                    # Это либо ответ от сервера либо действия с контактами
                    # мы это складываем в очередь
                    self.request_queue.put(jm)
            except Exception as e:
                # Ошбики быть не должно так как сервер отправлять верные данные
                # но лучше этот случай все равно обработать
                # выведем ошибку, но лучше писать в будующем в log
                print(e)


    def stop(self):
        self.is_alive = False


class ConsoleReciever(Receiver):
    """Консольный обработчик входящих сообщений"""

    def process_message(self, message):
        # Выводим текст сообщения в консоль и рисуем от кого пришло
        print("\n>> user {}: {}".format(message.from_, message.message))


class GuiReciever(Receiver, QObject):
    """GUI обработчик входящих сообщений"""
    # мы его наследуюем от QObject чтобы работала модель сигнал слот
    # можно и не наследовать, но тогда надо передавать объект в который мы будем сообщения выводить
    # через сигнал слот более гибко т.к. мы можем обработать сигнал как хотим уже внутри gui
    # событий (сигнал) что пришли данные
    gotData = pyqtSignal(str)
    # событие (сигнал) что прием окончен
    finished = pyqtSignal(int)

    def __init__(self, sock, request_queue):
        # инициализируем как Receiver
        Receiver.__init__(self, sock, request_queue)
        # инициализируем как QObject
        QObject.__init__(self)

    def process_message(self, message):
        """Обработка сообщения"""
        # Генерируем сигнал (сообщаем, что произошло событие)
        # В скобках передаем нужные нам данные
        text = '{} >>> {}'.format(message.from_, message.message)
        self.gotData.emit(text)

    def poll(self):
        super().poll()
        # Когда обработка событий закончиться сообщаем об этом генерируем сигнал finished
        self.finished.emit(0)
