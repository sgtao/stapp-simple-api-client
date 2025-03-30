# ApiResponseViewer.py
import json

import streamlit as st


class ApiResponseViewer:
    def render_viewer(self, response):
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
