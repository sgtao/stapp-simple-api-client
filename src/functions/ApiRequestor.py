# ApiRequestor.py
import requests
import urllib.parse

import streamlit as st

from functions.AppLogger import AppLogger


class ApiRequestor:
    def __init__(self):
        self.session = requests.Session()
        # self.logger = logging.getLogger(__name__)
        self.api_logger = AppLogger(__name__)

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
            self.api_logger.api_start_log(url, method, headers, body)

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
            self.api_logger.api_success_log(response)

            # レスポンス解析
            return response

        except requests.exceptions.HTTPError as http_err:
            # HTTPエラー時のログ
            self.api_logger.error_log(f"HTTP error occurred: {http_err}")

            # HTTPエラー時の処理
            st.error(f"HTTPエラー: {http_err}")
            if hasattr(http_err.response, "status_code"):
                st.error(f"ステータスコード: {http_err.response.status_code}")
                st.error(f"理由: {http_err.response.reason}")
                st.error(f"詳細: {http_err.response.json()}")
            return None

        except requests.exceptions.RequestException as req_err:
            # その他のリクエストエラー時のログ
            self.api_logger.error_log(f"Request error occurred: {req_err}")
            raise

        except Exception as e:
            # その他例外発生時のログ
            self.api_logger.error_log(f"An unexpected error occurred: {e}")
            raise

    def replace_uri(self, uri):
        replaced_uri = uri
        for i in range(st.session_state.num_inputs):
            key = f"user_input_{i}"
            value = urllib.parse.quote(st.session_state[f"user_input_{i}"])
            replaced_uri = replaced_uri.replace(f"＜{key}＞", value)

        return replaced_uri

    def replace_body(self, body):
        replaced_body = body
        for i in range(st.session_state.num_inputs):
            key = f"user_input_{i}"
            value = st.session_state[f"user_input_{i}"].replace('"', "'")
            replaced_body = replaced_body.replace(f"＜{key}＞", value)

        return replaced_body
