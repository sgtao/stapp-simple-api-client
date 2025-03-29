# ApiRequestor.py
import requests
import logging

import streamlit as st

# import json

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # logging.StreamHandler(),  # コンソール出力
        logging.FileHandler("logs/api_request.log"),  # ファイル出力
    ],
)


class ApiRequestor:
    def __init__(self):
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def send_request(self, url, method, headers=None, body=None):
        """
        汎用的なAPIリクエストメソッド
        :param url: APIエンドポイント
        :param method: HTTPメソッド (GET, POST, PUT, DELETE)
        :param headers: リクエストヘッダー (辞書形式)
        :param body: リクエストボディ (辞書形式)
        :return: レスポンスオブジェクトまたはエラーメッセージ
        """
        try:
            # メソッド開始時のログ
            self.logger.info(f"Starting request: {method} {url}")
            if headers:
                self.logger.debug(f"Headers: {headers}")
            if body:
                self.logger.debug(f"Body: {body}")

            # メソッドごとの処理
            if method in ["GET", "DELETE"]:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                )
            elif method in ["POST", "PUT"]:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body,
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # ステータスコードチェック
            response.raise_for_status()

            # メソッド終了時のログ
            self.logger.info(f"Request completed with {response.status_code}")
            self.logger.debug(f"Response headers: {response.headers}")
            self.logger.debug(f"Response body: {response.text}")

            # レスポンス解析
            # try:
            #     return response.json()  # JSON形式の場合
            # except json.JSONDecodeError:
            #     return response.text  # テキスト形式の場合
            return response

        except requests.exceptions.HTTPError as http_err:
            # HTTPエラー時のログ
            self.logger.error(f"HTTP error occurred: {http_err}")

            # HTTPエラー時の処理
            st.error(f"HTTPエラー: {http_err}")
            if hasattr(http_err.response, "status_code"):
                st.error(f"ステータスコード: {http_err.response.status_code}")
                st.error(f"理由: {http_err.response.reason}")
            return None

        except requests.exceptions.RequestException as req_err:
            # その他のリクエストエラー時のログ
            self.logger.error(f"Request error occurred: {req_err}")
            raise

        except Exception as e:
            # その他例外発生時のログ
            self.logger.exception(f"An unexpected error occurred: {e}")
            raise
