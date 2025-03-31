# 11_trial_simple_api.py
import json

import pandas as pd
import streamlit as st

from components.ApiKey import ApiKey
from components.ApiRequestHeader import ApiRequestHeader
from components.ApiResponseViewer import ApiResponseViewer
from components.UserInputs import UserInputs
from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

APP_TITLE = "APIクライアントアプリ"


def init_st_session_state():
    refreshed_state = False
    if "header_df" not in st.session_state:
        st.session_state.header_df = pd.DataFrame(
            [
                {"Property": "Content-Type", "Value": "application/json"},
            ]
        )
        refreshed_state = True
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
        refreshed_state = True
    if "use_dynamic_inputs" not in st.session_state:
        st.session_state.use_dynamic_inputs = False
        refreshed_state = True
    if "user_property_path" not in st.session_state:
        st.session_state.user_property_path = ""
        refreshed_state = True
    if refreshed_state:
        st.rerun()


def sidebar():
    # インスタンス化
    api_key_component = ApiKey()
    user_inputs_component = UserInputs()

    with st.sidebar:
        api_key_component.input_key()
        user_inputs_component.render_dynamic_inputs()
        user_inputs_component.render_property_path()
        with st.expander("session_state", expanded=False):
            st.write(st.session_state)


def main():
    st.title(f"🚀 {APP_TITLE}")
    """
    任意のAPIサービスにアクセスする[streamlit](https://streamlit.io/)アプリです。
    """
    # インスタンス化
    request_header = ApiRequestHeader()
    response_viewer = ApiResponseViewer()
    api_requestor = ApiRequestor()

    method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT", "DELETE"])
    uri = st.text_input("URI", "https://dummyjson.com/products/1")
    # method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT"])

    # 動的に入力フィールドを生成するかのチェックボックス
    st.session_state.use_dynamic_inputs = st.checkbox("動的な入力を利用する")

    # ヘッダー入力セクション
    header_dict = {}
    with st.expander("リクエストヘッダー設定"):
        request_header.render_editor()
        # ヘッダー情報を辞書形式で取得
        header_dict = request_header.get_header_dict()

    # リクエストボディ入力（POST, PUTの場合のみ表示）
    request_body = None
    if method in ["POST", "PUT"]:
        with st.expander("リクエストボディ設定"):
            request_body = st.text_area("リクエストボディ (JSON形式)", "{}")

    # リクエスト送信ボタン
    if st.button("リクエストを送信"):
        try:
            # ヘッダーとボディのJSON形式検証
            # headers = json.loads(headers_input) if headers_input else {}
            # headers = json.dumps(header_dict) if header_dict else {}
            if st.session_state.use_dynamic_inputs:
                for i in range(st.session_state.num_inputs):
                    key = f"user_input_{i}"
                    value = st.session_state[f"user_input_{i}"]
                    request_body = request_body.replace(f"＜{key}＞", value)

            body = json.loads(request_body) if request_body else None

            # APIリクエスト送信
            response = api_requestor.send_request(
                uri, method, header_dict, body
            )

            # レスポンス表示
            if response:
                st.subheader("レスポンス")
                response_viewer.render_viewer(response)
        except Exception as e:
            # ユーザー向けメッセージ
            st.error(
                "リクエスト中にエラーが発生しました。詳細は以下をご確認ください。"
            )
            # 詳細な例外情報を表示
            st.exception(e)


if __name__ == "__main__":
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    init_st_session_state()
    sidebar()
    main()
