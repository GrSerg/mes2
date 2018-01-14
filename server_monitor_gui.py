import sys
from PyQt5 import QtWidgets, uic
from repo.server_models import session
from repo.server_repo import Repo

# Создаем приложение
app = QtWidgets.QApplication(sys.argv)
# грузим главную форму
window = uic.loadUi('server_monitor.ui')

# создаем репозиторий, тут нам не нужен сам сервер, он крутится в цикле, нужна только база данных для мониторинга
repo = Repo(session)


def load_clients():
    """загрузка клиентов в QListWidget"""
    # получаем всех клиентов
    clients = repo.get_clients()
    # чистим список
    window.listWidgetClients.clear()
    # добавляем
    for client in clients:
        window.listWidgetClients.addItem(str(client))


# def load_history():
#     """загрузка истории сообщений в QListWidget"""
#     # Получаем все истории
#     histories = repo.get_histories()
#     # чистим список
#     window.listWidgetHistory.clear()
#     # добавляем
#     for history in histories:
#         window.listWidgetHistory.addItem(str(history))


def refresh():
    """Обновить все"""
    load_clients()
    

# Сразу все грузим при запуске скрипта
refresh()

# Связываем меню сигнал triggered - нажатие и слот функцию reresh
window.actionrefresh.triggered.connect(refresh)

# рисуем окно
window.show()
# точка входа в приложение
sys.exit(app.exec_())
