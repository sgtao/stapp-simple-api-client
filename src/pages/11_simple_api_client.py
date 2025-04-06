# 11_trial_simple_api.py
import json

import streamlit as st

from components.ApiKey import ApiKey
from components.ApiRequestHeader import ApiRequestHeader
from components.ApiRequestInputs import ApiRequestInputs
from components.ApiResponseViewer import ApiResponseViewer
from components.ClientController import ClientController
from components.UserInputs import UserInputs
from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Simple Api Client"


def init_st_session_state():
    refreshed_state = False
    if "api_running" not in st.session_state:
        st.session_state.api_running = False
        refreshed_state = True
    if refreshed_state:
        st.rerun()


def sidebar():
    # インスタンス化
    api_key_component = ApiKey()
    user_inputs_component = UserInputs()
    client_controller = ClientController()

    with st.sidebar:
        api_key_component.input_key()
        user_inputs_component.render_dynamic_inputs()
        user_inputs_component.render_property_path()
        with st.expander("session_state", expanded=False):
            st.write(st.session_state)
        client_controller.render_buttons()


def main():
    st.title(f"🚀 {APP_TITLE}")
    """
    任意のAPIサービスにアクセスする[streamlit](https://streamlit.io/)アプリです。
    """
    # インスタンス化
    request_header = ApiRequestHeader()
    request_inputs = ApiRequestInputs()
    response_viewer = ApiResponseViewer()
    api_requestor = ApiRequestor()

    # ユーザー入力：APIリクエストの指定項目
    method = request_inputs.render_method_selector()
    use_dynamic_inputs = request_inputs.render_use_dynamic_checkbox()
    uri = request_inputs.render_uri_input()

    # ヘッダー入力セクション
    header_dict = {}
    with st.expander("リクエストヘッダー設定"):
        request_header.render_editor()
        # ヘッダー情報を辞書形式で取得
        header_dict = request_header.get_header_dict()

    # リクエストボディ入力（POST, PUTの場合のみ表示）
    request_body = request_inputs.render_body_input()

    # リクエスト送信ボタン
    if st.button("リクエストを送信"):
        try:
            # 確定情報のセット
            st.session_state.uri = uri
            st.session_state.method = method
            st.session_state.req_body = request_body
            st.session_state.use_dynamic_inputs = use_dynamic_inputs

            # URIとリクエストボディのJSON形式検証
            sent_uri = uri
            sent_body = request_body
            if st.session_state.use_dynamic_inputs:
                sent_uri = api_requestor.replace_uri(uri)
                if request_body:
                    sent_body = api_requestor.replace_body(request_body)

            # st.text(sent_body)
            body_json = json.loads(sent_body) if request_body else None

            # APIリクエスト送信
            response = api_requestor.send_request(
                sent_uri, method, header_dict, body_json
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
    # init_st_session_state()
    sidebar()
    main()
