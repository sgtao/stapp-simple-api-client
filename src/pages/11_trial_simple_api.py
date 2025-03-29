# 11_trial_simple_api.py
import streamlit as st
import requests
import json


def make_api_request(uri, method, headers=None, body=None):
    try:
        response = {}
        if method == "GET":
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


st.title("APIリクエストクライアント")

uri = st.text_input("URI", "https://dummyjson.com/products/1")
# method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT", "DELETE"])
method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT"])

# ヘッダー入力セクション
with st.expander("リクエストヘッダー設定"):
    headers_input = st.text_area(
        "カスタムヘッダー (JSON形式)",
        help="""例: {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_TOKEN"
        }""",
    )

# メインフォーム
# # リクエストボディ入力（POST, PUTの場合）
# body = st.text_area("リクエストボディ (JSON)", height=200)
with st.form("api_request_form"):
    request_body = None
    if method != "GET":
        request_body = st.text_area("リクエストボディ (JSON形式)", "{}")

    if st.form_submit_button("リクエストを送信"):
        try:
            headers = json.loads(headers_input) if headers_input else {}
            response = make_api_request(uri, method, headers, request_body)

            if response:
                st.subheader("レスポンス")
                st.json(response.json())

        except json.JSONDecodeError:
            st.error("ヘッダーまたはリクエストボディのJSON形式が不正です")
