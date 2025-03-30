# AppLogger.py
import os

import logging


class AppLogger:
    def __init__(
        self, name, log_file="logs/api_request.log", level=logging.DEBUG
    ):
        """
        ロガーを設定するクラス
        :param name: ロガー名
        :param log_file: ログファイルのパス
        :param level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # ログディレクトリの作成
        LOG_DIR = "logs"
        if log_file == "logs/api_request.log" and not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        # ファイルハンドラー
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # フォーマッター
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        # ハンドラー追加（重複追加を防ぐ）
        if not self.logger.hasHandlers():
            self.logger.addHandler(file_handler)

    def app_start(self):
        self.logger.info(f"Start App: {self.name}")

    def api_start_log(self, url, method, headers=None, body=None):
        self.logger.info(f"Starting request: {method} {url}")
        if headers:
            self.logger.debug(f"Request headers: {headers}")
        if body:
            self.logger.debug(f"Request body: {body}")

    def api_success_log(self, response):
        # メソッド終了時のログ
        self.logger.info(f"Request completed with {response.status_code}")
        self.logger.debug(f"Response headers: {response.headers}")
        self.logger.debug(f"Response body: {response.text}")

    def error_log(self, message):
        # メソッド終了時のログ
        self.logger.error(message)
