# logs_viewer.py
import streamlit as st


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


# メイン関数
def main():
    st.title(" Log Viewer")
    # ログファイルのパス
    log_file_path = "logs/api_request.log"
    display_log(log_file_path)


if __name__ == "__main__":
    main()
