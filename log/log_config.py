import logging
import logging.handlers
import os


LOG_FOLDER_PATH = os.path.join(os.getcwd(), 'log', 'files')
CLIENT_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'client.log')
SERVER_LOF_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'server.log')
# Создаем логгеры все в одном месте, потом будем их получить по имени
# Клиентский логгер
client_logger = logging.getLogger('client')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
client_handler = logging.FileHandler(CLIENT_LOG_FILE_PATH, encoding='utf-8')
client_handler.setLevel(logging.INFO)
client_handler.setFormatter(formatter)
client_logger.addHandler(client_handler)
client_logger.setLevel(logging.INFO)
# Серверный логгер
server_logger = logging.getLogger('server')
server_handler = logging.handlers.TimedRotatingFileHandler(SERVER_LOF_FILE_PATH, when='d')
server_handler.setFormatter(formatter)
server_logger.addHandler(server_handler)
server_logger.setLevel(logging.INFO)
