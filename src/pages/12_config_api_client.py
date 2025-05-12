# config_api_client.py
import json

import streamlit as st

from components.ApiRequestHeader import ApiRequestHeader
from components.ApiRequestInputs import ApiRequestInputs
from components.ResponseViewer import ResponseViewer
from components.ClientController import ClientController
from components.ConfigFiles import ConfigFiles
from components.SideMenus import SideMenus
from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

APP_TITLE = "Config Api Client"


def apply_config_to_session_state(config):
    for key, value in config.items():
        st.session_state[key] = value


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"🚀 {APP_TITLE}")
    """
    `assets`と`privates`配下のYAMLファイルを使ってAPIサービスにアクセスします
    """

    # 以下は11_simple_api_client.pyと同様のAPIリクエスト部分
    request_header = ApiRequestHeader()
    request_inputs = ApiRequestInputs()
    response_viewer = ResponseViewer()
    api_requestor = ApiRequestor()
    client_controller = ClientController()

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

        # 読み込んだコンフィグをセッションステートに適用
        # apply_config_to_session_state(config)
        client_controller.set_session_state(config)

        # ユーザー入力：APIリクエストの指定項目
        method = request_inputs.render_method_selector()
        request_inputs.render_use_dynamic_checkbox()
        uri = request_inputs.render_uri_input()

        # ヘッダー入力セクション
        header_dict = {}
        with st.expander("リクエストヘッダー設定"):
            request_header.render_editor()
            # ヘッダー情報を辞書形式で取得
            header_dict = request_header.get_header_dict()

        # リクエストボディ入力（POST, PUTの場合のみ表示）
        request_body = request_inputs.render_body_input()

        if st.button("リクエストを送信"):
            try:
                # URIとリクエストボディのJSON形式検証
                sent_uri = uri
                sent_body = request_body
                if st.session_state.use_dynamic_inputs:
                    sent_uri = api_requestor.replace_uri(uri)
                    if request_body:
                        sent_body = api_requestor.replace_body(request_body)

                # st.text(sent_body)
                body_json = json.loads(sent_body) if request_body else None

                response = api_requestor.send_request(
                    sent_uri, method, header_dict, body_json
                )

                if response:
                    st.subheader("レスポンス")
                    response_viewer.render_viewer(response)
            except Exception as e:
                st.error(
                    "リクエスト中にエラーが発生しました。詳細は以下をご確認ください。"
                )
                st.exception(e)


if __name__ == "__main__":
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
