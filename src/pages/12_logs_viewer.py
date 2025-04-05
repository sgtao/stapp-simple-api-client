# logs_viewer.py
from datetime import datetime
import os
import time

import streamlit as st

from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Log Viewer"


# ログファイル表示関数
def display_log(log_file_path):
    try:
        with open(log_file_path, "r") as f:
            log_contents = f.read()
        st.text(log_contents)
    except FileNotFoundError:
        st.error(f"Log file not found: {log_file_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def rotate_log_file(log_file_path, app_logger):
    """
    ログファイルをリネームする関数
    """
    new_log_file_path = None
    try:
        # 新しいファイル名を生成
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        new_log_file_path = f"{log_file_path.replace('.log', '')}_{now}.log"

        app_logger.info_log(f"rotate log file to {new_log_file_path}.")
        # ファイルをリネーム
        os.rename(log_file_path, new_log_file_path)

        st.success(f"Log file rotated to {new_log_file_path}")
        time.sleep(1)
        return new_log_file_path
    except FileNotFoundError:
        st.error(f"Log file not found: {log_file_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")


# メイン関数
def main():
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()

    st.title("Log Viewer")
    # ログファイルのパス
    log_file_path = app_logger.get_logfile_name()

    # ログファイルリネームボタン
    if st.button("Log Rotate"):
        rotated_filename = rotate_log_file(log_file_path, app_logger)
        if rotate_log_file is not None:
            # app_logger.logger.removeHandler()
            # app_logger.setup_logger(APP_TITLE)
            app_logger = AppLogger(APP_TITLE)
            app_logger.info_log(f"previous log renamed to {rotated_filename}.")
            st.rerun()

    display_log(log_file_path)


if __name__ == "__main__":
    main()
