# api_server_control.py
# import json
import os
import requests

import streamlit as st
import subprocess
import signal

from components.SideMenus import SideMenus
from components.ResponseViewer import ResponseViewer
from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger


# ページ設定
st.set_page_config(
    page_title="API Server Control",
    page_icon="⚙️",
)

APP_TITLE = "API Server Control"
# SUBPROCESS_PROG = "src/services/api_server.py"
SUBPROCESS_PROG = "src/api_server.py"


def initial_session_state():
    # API サーバーの起動・停止を管理するセッション状態の初期化
    if "api_process" not in st.session_state:
        st.session_state.api_process = None
    if "port_number" not in st.session_state:
        st.session_state.port_number = 3000
    if "response" not in st.session_state:
        st.session_state.response = None


def start_api_server(port):
    """
    FastAPIサーバーをバックグラウンドで起動します。
    """
    try:
        # 既存のAPIサーバーが実行中の場合は停止
        if st.session_state.api_process:
            stop_api_server()

        # APIサーバーを起動し、プロセスをセッション状態に保存
        # command = ["python", "api_server.py", "--port", str(port)]
        command = ["python", SUBPROCESS_PROG, "--port", str(port)]
        st.session_state.api_process = subprocess.Popen(
            command, start_new_session=True
        )
        st.session_state.port_number = port
        st.success(f"API Server started on port {port}")
    except Exception as e:
        st.error(f"API Server failed to start: {e}")


def stop_api_server():
    """
    バックグラウンドで実行中のFastAPIサーバーを停止します。
    """
    if st.session_state.api_process:
        try:
            # Windows環境とLinux環境でプロセス停止処理を場合分け
            if os.name == "nt":
                # Windows: taskkillを使用
                subprocess.run(
                    [
                        "taskkill",
                        "/F",
                        "/PID",
                        str(st.session_state.api_process.pid),
                    ]
                )
            else:
                # Linux, macOS: プロセスグループにSIGTERMを送信
                os.killpg(
                    os.getpgid(st.session_state.api_process.pid),
                    signal.SIGTERM,
                )

            st.session_state.api_process = None  # プロセスをリセット
            st.success("API Server stopped.")
        except Exception as e:
            st.error(f"Failed to stop API Server: {e}")
    else:
        st.warning("API Server is not running.")


def test_api_hello(port):
    """
    APIサーバーへの接続をテストします。
    """
    uri = f"http://localhost:{port}/api/v0/hello"
    method = "GET"
    header_dict = {
        "Content-Type": "application/json",
    }
    try:
        if st.button("Test API (hello)"):
            # response = requests.get(uri)
            api_requestor = ApiRequestor()
            response = api_requestor.send_request(
                uri,
                method,
                header_dict,
            )
            response.raise_for_status()  # HTTPエラーをチェック
            st.success(
                f"""
                Successfully connected to API Server on port {port}.
                """
            )
            return response
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API Server: {e}")


def test_get_config_files(port):
    """
    APIサーバーへの接続をテストします。
    """
    uri = f"http://localhost:{port}/api/v0/configs"
    method = "GET"
    header_dict = {
        "Content-Type": "application/json",
    }
    try:
        if st.button("Test Configs(get list)"):
            # response = requests.get(uri)
            api_requestor = ApiRequestor()
            response = api_requestor.send_request(
                uri,
                method,
                header_dict,
            )
            response.raise_for_status()  # HTTPエラーをチェック
            st.success(
                f"""
                Successfully connected to API Server on port {port}.
                """
            )
            # st.write(response.json())
            # response_json = response.json()
            # st.session_state.config_files = response_json.get("result")
            return response
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API Server: {e}")


def test_post_service(port):
    """
    APIサーバーへの接続をテストします。
    """
    uri = f"http://localhost:{port}/api/v0/service"
    method = "POST"
    header_dict = {"Content-Type": "application/json"}
    # リクエストボディ入力（POST, PUTの場合のみ表示）
    # request_body = """
    #     {
    #         "config_file": "assets/001_get_simple_api_test.yaml"
    #     }
    # """
    request_body = {
        "config_file": "assets/001_get_simple_api_test.yaml",
        "num_user_inputs": st.session_state.num_inputs,
        "user_inputs": {},
    }
    for i in range(st.session_state.num_inputs):
        user_key = f"user_input_{i}"
        # value = st.session_state[f"user_input_{i}"].replace('"', "'")
        # request_body["user_inputs"].append({{user_key: f"{value}"}})
        if user_key in st.session_state:
            value = st.session_state[user_key]
            request_body["user_inputs"][user_key] = value
        else:
            st.warning(f"Session state key '{user_key}' not found.")
    # body_json = json.loads(request_body)
    # body_json = json.dumps(request_body)
    body_json = request_body

    try:
        if st.button("Test Service(post config)"):
            # response = requests.get(uri)
            api_requestor = ApiRequestor()
            response = api_requestor.send_request(
                uri,
                method,
                header_dict,
                body_json,
            )
            response.raise_for_status()  # HTTPエラーをチェック
            st.success(
                f"""
                Successfully connected to API Server on port {port}.
                """
            )
            return response
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API Server: {e}")


def main():
    # UI
    st.title(f"⚙️ {APP_TITLE}")

    # ポート番号の入力
    port = st.number_input(
        "Port Number",
        min_value=1024,
        max_value=65535,
        value=st.session_state.port_number,
        step=1,
    )

    # APIサーバーの起動・停止ボタン
    cols = st.columns(2)
    with cols[0]:
        if st.button(
            label="Run API Service",
            disabled=(st.session_state.api_process is not None),
        ):
            start_api_server(port)
    with cols[1]:
        if st.button(
            label="Stop API Service",
            disabled=(st.session_state.api_process is None),
            help="Click twice is better.",
        ):
            stop_api_server()

    # API接続テストボタン
    if st.session_state.api_process:
        # instantiation
        response_viewer = ResponseViewer("result")
        try:
            st.subheader("Test API Server")
            col1, col2 = st.columns(2)
            response = None
            with col1:
                if response is None:
                    response = test_api_hello(port)
                if response is None:
                    response = test_get_config_files(port)
                if response is None:
                    response = test_post_service(port)
            with col2:
                if st.button("Rerun (`R`)", icon="🏃"):
                    st.rerun()

            st.subheader("レスポンス")
            # st.write(response)
            # st.write(st.session_state.response)
            if response is not None:
                response_viewer.render_viewer(response)
                st.session_state.response = response
            elif st.session_state.response is not None:
                response_viewer.render_viewer(st.session_state.response)
            else:
                st.info("You can access to API Server via Test Buttons")

        except Exception as e:
            st.error(f"Failed to connect to API Server: {e}")


if __name__ == "__main__":
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    initial_session_state()
    side_menus = SideMenus()
    side_menus.set_user_property_path("result")
    side_menus.render_api_client_menu()
    main()
