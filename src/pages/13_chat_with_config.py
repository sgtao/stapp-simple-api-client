# 13_chat_with_config.py
# import os
import requests
import time

# from pathlib import Path

import streamlit as st

from functions.ApiRequestor import ApiRequestor
from components.ApiRequestHeader import ApiRequestHeader
from components.ApiRequestInputs import ApiRequestInputs
from components.ClientController import ClientController
from components.ConfigFiles import ConfigFiles
from components.SideMenus import SideMenus

# from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Chat with Config"


class GroqAPI:
    def __init__(
        self,
        uri: str = "https://api.groq.com/openai/v1/chat/completions",
        model_name: str = "llama-3.3-70b-versatile",
        header_dict: dict = None,
        req_body: dict = None,
    ):
        self.model_name = model_name
        self.url = uri
        self.header_dict = header_dict or {}
        self.req_body = req_body or {}

    def _response(self, messages):
        headers = self.header_dict.copy()
        payload = self.req_body
        # payload.update(
        #     {
        #         "model": self.model_name,
        #         "messages": messages,
        #         "temperature": 0,
        #         "max_tokens": 4096,
        #         "stream": True,
        #         "stop": None,
        #     }
        # )
        # stream=Trueでストリーミングレスポンスを受け取る
        response = requests.post(
            # self.api_url, headers=headers, json=payload, stream=True
            url=self.url,
            headers=headers,
            # json=payload,
            data=payload,
            stream=False,
        )
        response.raise_for_status()
        return response

    def response(self, messages):
        try:
            response = self._response(messages)
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            st.error(f"APIリクエストに失敗しました: {e}")
            time.sleep(3)
            st.rerun()


class Message:
    system_prompt: str = (
        """あなたは聡明なAIです。ユーザの入力に全て日本語で返答を生成してください"""
    )

    def __init__(self, system_prompt: str = system_prompt):
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                }
            ]

    def add(self, role: str, content: str):
        st.session_state.messages.append({"role": role, "content": content})

    def get_messages(self):
        return st.session_state.messages

    def display_chat_history(self):
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def display_stream(self, generater):
        with st.chat_message("assistant"):
            return st.x(generater)


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
    user_input = st.chat_input("何か入力してください")

    message = Message()

    if user_input:
        message.add("user", user_input)
        message.display_chat_history()

        # get response from GroqAPI
        # llm = GroqAPI(selected_model)
        if api_request_inputs.get_method() == "GET":
            st.warning(
                "GETメソッドは、リクエストボディを送信しません。"
                "リクエストヘッダーとURIのみが使用されます。"
            )
            time.sleep(3)
            st.rerun()

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
        llm = GroqAPI(
            uri=sent_uri,
            header_dict=header_dict,
            req_body=sent_body,
        )

        # response = message.display_stream(
        #     generater=llm.response(message.get_messages())
        # )
        response = llm.response(message.get_messages())
        # response = user_input
        message.add("assistant", response)


# if __name__ == "__main__":
#     main()
if __name__ == "__main__":
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
