# ApiRequestor.py
import requests

# import json


class ApiRequestor:
    def __init__(self):
        self.session = requests.Session()

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

            # レスポンス解析
            # try:
            #     return response.json()  # JSON形式の場合
            # except json.JSONDecodeError:
            #     return response.text  # テキスト形式の場合
            return response

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except ValueError as ve:
            return {"error": str(ve)}
