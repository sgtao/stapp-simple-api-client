# api_server_control.py
# import json
import os

import streamlit as st
import subprocess
import signal

from functions.AppLogger import AppLogger


# ページ設定
st.set_page_config(
    page_title="API Server Control",
    page_icon="⚙️",
)

APP_TITLE = "API Server Control"
SUBPROCESS_PROG = "src/functions/api_server.py"


def initial_session_state():
    # API サーバーの起動・停止を管理するセッション状態の初期化
    if "api_process" not in st.session_state:
        st.session_state.api_process = None
    if "port_number" not in st.session_state:
        st.session_state.port_number = 3000


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


def test_api_connection(port):
    """
    APIサーバーへの接続をテストします。
    """
    import requests

    url = f"http://localhost:{port}/api/v0/hello"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーをチェック
        st.success(
            f"""
            Successfully connected to API Server on port {port}.
            Response: {response.json()}
            """
        )
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
            "Run API Service",
            disabled=(st.session_state.api_process is not None),
        ):
            start_api_server(port)
    with cols[1]:
        if st.button(
            "Stop API Service",
            disabled=(st.session_state.api_process is None),
        ):
            stop_api_server()

    # API接続テストボタン
    if st.session_state.api_process:
        if st.button("Test API Connection"):
            test_api_connection(port)


if __name__ == "__main__":
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    initial_session_state()
    main()
