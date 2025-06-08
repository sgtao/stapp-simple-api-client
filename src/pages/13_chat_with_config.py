# 13_chat_with_config.py
import json

# import os
# import requests
import time

# from pathlib import Path

import streamlit as st

from components.ApiRequestHeader import ApiRequestHeader
from components.ApiRequestInputs import ApiRequestInputs
from components.ChatMessage import ChatMessage
from components.ClientController import ClientController
from components.ConfigFiles import ConfigFiles

# from components.ResponseViewer import extract_property_from_json
from components.SideMenus import SideMenus

from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger
from functions.GroqAPI import GroqAPI

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Chat with Config"


# モーダルの定義
@st.dialog("Show Configed Request.")
def modal_request_viewer(request_header, request_inputs):
    def _modal_closer():
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    st.write("Configurated Request inputs:")
    # ユーザー入力：APIリクエストの指定項目
    request_inputs.render_method_selector()
    request_inputs.render_use_dynamic_checkbox()
    request_inputs.render_uri_input()

    # ヘッダー入力セクション
    with st.expander("リクエストヘッダー設定"):
        request_header.render_editor()

    # リクエストボディ入力（POST, PUTの場合のみ表示）
    request_inputs.render_body_input()

    # Close button for modal
    _modal_closer()


# def main():
def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"💬 {APP_TITLE}")
    # インスタンス化
    # request_header = ApiRequestHeader()
    # request_inputs = ApiRequestInputs()
    api_requestor = ApiRequestor()
    client_controller = ClientController()
    request_header = ApiRequestHeader()
    api_request_inputs = ApiRequestInputs()

    # assets/privatesフォルダからyamlファイルを選択
    config_files = ConfigFiles()

    if not config_files:
        st.warning(
            "No YAML config files in assets and private. Please add some."
        )
        return

    # selected_config_file = st.selectbox("Select a config file", config_files)
    selected_config_file = config_files.render_config_selector()

    # 選択されたコンフィグファイルを読み込む
    if selected_config_file:
        config = config_files.load_config_from_yaml(selected_config_file)
        config_files.render_config_viewer(selected_config_file, config)

    # Load Config and show Request settings
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Load Config File"):
            # 読み込んだコンフィグをセッションステートに適用
            # apply_config_to_session_state(config)
            client_controller.set_session_state(config)
            st.rerun()
    with col2:
        if st.button("Show Config. Request"):
            # response = test_post_service(port)
            modal_request_viewer(
                request_header=request_header,
                request_inputs=api_request_inputs,
            )
    with col3:
        if st.button("Clear Session States"):
            # 全てのセッション状態をクリアする場合はこちらを使用
            st.session_state.clear()
            st.rerun()
    with col4:
        pass
    with col5:
        pass

    # Chat with Config
    message = ChatMessage()
    message.display_chat_history()

    user_input = st.chat_input("何か入力してください")
    if user_input:
        # get response from GroqAPI
        # llm = GroqAPI(selected_model)
        if api_request_inputs.get_method() == "GET":
            st.warning(
                "GETメソッドは、リクエストボディを送信しません。"
                "リクエストヘッダーとURIのみが使用されます。"
            )
            time.sleep(3)
            st.rerun()

        message.add("user", user_input)
        uri = api_request_inputs.get_uri()
        header_dict = request_header.get_header_dict()
        request_body = api_request_inputs.get_req_body()
        # URIとリクエストボディのJSON形式検証
        sent_uri = uri
        sent_body = request_body
        if st.session_state.use_dynamic_inputs:
            sent_uri = api_requestor.replace_uri(uri)
            if request_body:
                sent_body = api_requestor.replace_body(request_body)
        req_body = json.loads(sent_body)
        try:
            llm = GroqAPI(
                uri=sent_uri,
                header_dict=header_dict,
                req_body=req_body,
                user_property_path=st.session_state.user_property_path,
            )

            # response = message.display_stream(
            #     generater=llm.response(message.get_messages())
            # )
            # response = llm.response(message.get_messages())
            # response = llm.single_response()
            response = llm.single_response(message.get_messages())
            # response = user_input
            message.add("assistant", response)
        except Exception as e:
            st.error(f"APIリクエストに失敗しました: {e}")
            time.sleep(3)
            st.rerun()


# if __name__ == "__main__":
#     main()
if __name__ == "__main__":
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
