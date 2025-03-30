# 11_trial_simple_api.py
import json

import pandas as pd
import streamlit as st

from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

APP_TITLE = "APIクライアントアプリ"


def init_st_session_state():
    # ヘッダー情報の初期化
    if "header_df" not in st.session_state:
        st.session_state.header_df = pd.DataFrame(
            [
                {"Property": "Content-Type", "Value": "application/json"},
            ]
        )


def sidebar():
    with st.sidebar:
        with st.expander("session_state", expanded=False):
            st.write(st.session_state)


def main():
    st.title(APP_TITLE)
    """
    任意のAPIサービスにアクセスする[streamlit](https://streamlit.io/)アプリです。
    """

    # インスタンス化
    api_requestor = ApiRequestor()

    method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT", "DELETE"])
    uri = st.text_input("URI", "https://dummyjson.com/products/1")
    # method = st.selectbox("HTTPメソッド", ["GET", "POST", "PUT"])

    # ヘッダー入力セクション
    header_dict = {}
    with st.expander("リクエストヘッダー設定"):
        # headers_input = st.text_area(
        #     "カスタムヘッダー (JSON形式)",
        #     help="""例: {
        #         "Content-Type": "application/json",
        #         "Authorization": "Bearer YOUR_TOKEN"
        #     }""",
        # )

        header_df = st.data_editor(
            st.session_state.header_df,
            num_rows="dynamic",
            use_container_width=True,
        )
        st.session_state.header_df = header_df

        # ボタンで行追加・削除
        col1, col2 = st.columns(2)
        with col1:
            if st.button("行を追加"):
                new_row = {"Property": "", "Value": ""}
                st.session_state.header_df = pd.concat(
                    [st.session_state.header_df, pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                st.rerun()
        with col2:
            if st.button("行を削除"):
                if len(st.session_state["header_df"]) > 0:
                    st.session_state["header_df"] = st.session_state[
                        "header_df"
                    ].iloc[:-1]
                st.rerun()

        # ヘッダー情報を辞書形式に変換
        # header_dict = header_df.to_dict()
        header_list = header_df.values.tolist()
        # print(header_list)
        # header_dict = {item[0]: item[1] for item in header_list}
        for item in header_list:
            key = item[0]
            value = item[1]
            # header_dict.append(dict({key, value}))
            header_dict[key] = value

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
            body = json.loads(request_body) if request_body else None

            # APIリクエスト送信
            response = api_requestor.send_request(
                uri, method, header_dict, body
            )

            # レスポンス表示
            if response:
                st.subheader("レスポンス")
                # st.text(response.status_code)
                st.metric(label="Status Code", value=response.status_code)

                with st.expander("レスポンスヘッダー"):
                    try:
                        # 辞書形式のヘッダーをJSONとして表示
                        st.json(dict(response.headers))
                    except Exception as e:
                        st.error(
                            f"レスポンスヘッダーの表示中にエラーが発生しました: {str(e)}"
                        )
                with st.expander("レスポンスボディ"):
                    try:
                        st.json(response.json())  # JSON形式の場合
                    except json.JSONDecodeError:
                        st.text(response.text)  # テキスト形式の場合

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
