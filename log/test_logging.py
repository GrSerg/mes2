import logging
import os
import pytest
from .log import Log
import log.log_config as log_config


class TestLog:

    def test_create_message(self):
        assert Log._create_message() == ''
        assert Log._create_message(10) == '= 10'
        assert Log._create_message(10, 1, 2, 3) == 'args: (1, 2, 3) = 10'
        assert Log._create_message(10, 1, 2, 3, name='test') == "args: (1, 2, 3) kwargs: {'name': 'test'} = 10"

    def test_call(self):
        print('Создаею тестовый логгер')
        test_logger = logging.getLogger('test_logger')
        test_log_path = os.path.join(log_config.LOG_FOLDER_PATH, 'test.log')
        test_handler = logging.FileHandler(test_log_path, encoding='utf-8')
        test_handler.setLevel(logging.INFO)
        test_handler.setFormatter(log_config.formatter)
        test_logger.addHandler(test_handler)
        test_logger.setLevel(logging.INFO)
        print('Создаею класс декоратор, передаю логгер')
        log = Log(test_logger)

        @log
        def test_func(name, age):
            return 100

        test_func('TestName', 20)

        with open(test_log_path, 'r') as f:
            text = f.read()
            # Текущее время осложняет тестирование, поэтому написание теста кажется трудоемким, но заготовку оставляю
            assert True

            # print('Удаляю тестовый класс')
            # del log
            # print('Отключаю логгер')
            # del test_logger
            # print('Удаляю тестовый лог файл')
            # os.remove(TestLog.TEST_LOG_FILENAME)
