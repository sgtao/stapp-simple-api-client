# ClientController.py
from datetime import datetime
import time
import yaml

import streamlit as st


class ClientController:
    def __init__(self) -> None:
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        pass

    @st.dialog("Setting Info.")
    def modal(self, type):
        st.write(f"Modal for {type}:")
        if type == "save_state":
            self.save_session_state()
            self._modal_closer()
        else:
            st.write("No Definition.")

    def _modal_closer(self):
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    # 『保存』モーダル：
    def save_session_state(self):
        with st.expander("Save Helium State ?", expanded=False):
            pad = "stappHeliumRunnerState.yaml"
            time_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{pad}"
            # セッション状態からパラメータを取得
            save_data = {
                "time_stamp": time_stamp,
                "session_state": {
                    "uri": st.session_state.uri,
                    "method": st.session_state.method,
                },
            }

            # YAMLに変換
            yaml_str = yaml.dump(
                save_data, allow_unicode=True, default_flow_style=False
            )

            # ダウンロードボタンを表示
            st.download_button(
                label="Download as YAML",
                data=yaml_str,
                file_name=file_name,
                mime="text/yaml",
            )

    def _clear__states(self):
        # st.session_state.min_user_inputs = 0
        # st.session_state.user_inputs = []
        st.session_state.api_running = False
        # st.session_state.hl_runner = []
        # st.session_state.config = None

    def render_buttons(self):
        st.write("##### Runner Ctrl.")
        (
            col1,
            col2,
            col3,
            col4,
            col5,
        ) = st.columns(5)
        with col1:
            if st.button(
                help="Stop Running",
                label="⏹️",
                disabled=(st.session_state.api_running is False),
            ):
                # st.stop()
                st.session_state.api_running = False
                st.rerun()
        with col2:
            if st.button(
                help="Save Helium States",
                label="📥",
                disabled=st.session_state.api_running,
            ):
                self.modal("save_state")
        with col3:
            pass
        with col4:
            pass
        with col5:
            pass
