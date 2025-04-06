# ApiRequestInputs.py
import streamlit as st

METHODS = ["GET", "POST", "PUT", "DELETE"]


class ApiRequestInputs:
    def __init__(self):
        # Method, URI, RequestBodyの初期化
        if "method" not in st.session_state:
            # st.session_state.method = "GET"
            st.session_state.method = METHODS[0]
        if "uri" not in st.session_state:
            st.session_state.uri = "https://dummyjson.com/products/1"
        if "req_body" not in st.session_state:
            st.session_state.req_body = "{}"
        if "use_dynamic_inputs" not in st.session_state:
            # st.session_state.use_dynamic_inputs = False
            st.session_state.use_dynamic_inputs = True

    def _update_method(self):
        st.session_state.method = st.session_state._method_selector

    def _update_uri(self):
        st.session_state.uri = st.session_state._uri_input

    def _update_req_body(self):
        st.session_state.req_body = st.session_state._body_input

    def _update_use_dynamic_inputs(self):
        st.session_state.use_dynamic_inputs = (
            st.session_state._use_dynamic_checkbox
        )

    def render_method_selector(self):
        return st.selectbox(
            label="HTTPメソッド",
            options=METHODS,
            index=METHODS.index(st.session_state.method),
            key="_method_selector",
            on_change=self._update_method,
        )

    def render_uri_input(self):
        return st.text_input(
            label="URI",
            key="_uri_input",
            value=st.session_state.uri,
            on_change=self._update_uri,
        )

    def render_body_input(self):
        # リクエストボディ入力（POST, PUTの場合のみ表示）
        if st.session_state.method in ["POST", "PUT"]:
            with st.expander("リクエストボディ設定"):
                return st.text_area(
                    label="リクエストボディ (JSON形式)",
                    key="_body_input",
                    value=st.session_state.req_body,
                    on_change=self._update_req_body,
                )
        else:
            return None

    def render_use_dynamic_checkbox(self):
        return st.checkbox(
            label="動的な入力を利用する",
            key="_use_dynamic_checkbox",
            value=st.session_state.use_dynamic_inputs,
            on_change=self._update_use_dynamic_inputs,
        )
