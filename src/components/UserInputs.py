# UserInputs.py
import streamlit as st


class UserInputs:
    def __init__(self):
        self.user_property_path = ""
        # プリセット確認
        if "user_property_path" in st.session_state:
            self.user_property_path = st.session_state.user_property_path
        else:
            self.user_property_path = ""

    def render_property_path(self):
        # レスポンスの抽出プロパティパス指定
        st.session_state.user_property_path = st.text_input(
            "Runner UserName",
            type="default",
            placeholder="抽出するプロパティパス",
            help="例: tags[0].completion.value",
            value=self.user_property_path,
        )
