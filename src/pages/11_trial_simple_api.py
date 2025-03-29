# 11_trial_simple_api.py
import streamlit as st
import requests
import json


def make_api_request(uri, method, headers=None, body=None):
    try:
        response = {}
        if method in ["GET", "DELETE"]:
            # request without body
            response = requests.request(
                method=method,
                url=uri,
                headers=headers,
            )
        else:
            # request with body
            response = requests.request(
                method=method,
                url=uri,
                headers=headers,
                json=json.loads(body) if body else None,
            )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"APIリクエストエラー: {str(e)}")
        return None


def main():
    st.title("APIリクエストクライアント")

    uri = st.text_input("URI", "https://dummyjson.com/products/1")
    method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT", "DELETE"])
    # method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT"])

    # ヘッダー入力セクション
    headers_input = None
    with st.expander("リクエストヘッダー設定"):
        headers_input = st.text_area(
            "カスタムヘッダー (JSON形式)",
            help="""例: {
                "Content-Type": "application/json",
                "Authorization": "Bearer YOUR_TOKEN"
            }""",
        )

    # リクエストボディ入力（POST, PUTの場合のみ表示）
    request_body = None
    if method in ["POST", "PUT"]:
        with st.expander("リクエストボディ設定"):
            request_body = st.text_area("リクエストボディ (JSON形式)", "{}")

    # リクエスト送信ボタン
    if st.button("リクエストを送信"):
        try:
            # ヘッダーとボディのJSON形式検証
            headers = json.loads(headers_input) if headers_input else {}
            body = json.loads(request_body) if request_body else None

            # APIリクエスト送信
            response = make_api_request(uri, method, headers, body)

            # レスポンス表示
            if response:
                st.subheader("レスポンス")
                try:
                    st.json(response.json())  # JSON形式の場合
                except json.JSONDecodeError:
                    st.text(response.text)  # テキスト形式の場合

        except Exception:
            st.error(f"Error が置きました. Error: {Exception}")


if __name__ == "__main__":
    main()
