# 11_trial_simple_api.py
import streamlit as st
import requests
import json

def make_api_request(uri, method, body=None):
    """APIリクエストを送信してレスポンスを返す"""
    try:
        if method == "GET":
            response = requests.get(uri)
        elif method == "POST":
            response = requests.post(uri, data=body)
        elif method == "PUT":
            response = requests.put(uri, data=body)
        # elif method == "DELETE":
        #     response = requests.delete(uri)
        else:
            st.error("無効なHTTPメソッドです。")
            return None

        response.raise_for_status()  # HTTPエラーをチェック

        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text  # JSONでない場合はテキストを返す

    except requests.exceptions.RequestException as e:
        st.error(f"リクエストエラー: {e}")
        return None

st.title("APIリクエストクライアント")

# URI入力
uri = st.text_input("URI", "https://dummyjson.com/products/1")

# HTTPメソッド選択
# method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT", "DELETE"])
method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT"])

# リクエストボディ入力（POST, PUTの場合）
body = st.text_area("リクエストボディ (JSON)", height=200)

# リクエスト送信ボタン
if st.button("リクエストを送信"):
    if method in ["POST", "PUT"] and not body:
        st.error("POSTまたはPUTリクエストにはリクエストボディが必要です。")
    else:
        try:
            body = json.loads(body) if body else None  # JSONとしてパース
        except json.JSONDecodeError:
            st.error("無効なJSON形式です。")
            body = None

        if body is not None:
            response_data = make_api_request(uri, method, body)

            if response_data:
                st.subheader("レスポンス")
                st.json(response_data)
