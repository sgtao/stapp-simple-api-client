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
        elif type == "load_state":
            self.load_session_state()
            self._modal_closer()
        else:
            st.write("No Definition.")

    def _modal_closer(self):
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    # 『保存』モーダル：
    def _header_df_to_dict(self, header_df):
        dict_list = []
        records_list = header_df.to_dict(orient="records")
        for item in records_list:
            if item["Property"] == "Authorization":
                # auth_value = item["Value"].replace(
                #     "Bearer .*", "Bearer ＜API_KEY＞"
                # )
                auth_value = item["Value"].replace(
                    st.session_state.api_key, "＜API_KEY＞"
                )
                dict_list.append({item["Property"]: auth_value})
            else:
                dict_list.append({item["Property"]: item["Value"]})

        return dict_list

    def save_session_state(self):
        with st.expander("Save Session State ?", expanded=False):
            pad = "stappApiClientState.yaml"
            time_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{pad}"
            # セッション状態からパラメータを取得
            save_data = {
                "time_stamp": time_stamp,
                "session_state": {
                    "method": st.session_state.method,
                    "uri": st.session_state.uri,
                    # "header_df": st.session_state.header_df,
                    "header_df": self._header_df_to_dict(
                        st.session_state.header_df
                    ),
                    "req_body": st.session_state.req_body,
                    "use_dynamic_inputs": st.session_state.use_dynamic_inputs,
                    "user_property_path": st.session_state.user_property_path,
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

    # 『読込み』モーダル：
    def _on_file_upload(self):
        st.session_state.config = None

    def _load_config(self, uploaded_yaml):
        """
        YAMLファイルを読み込み、ユーザー入力を初期化する

        Args:
            uploaded_file: Streamlitのfile_uploaderから受け取るファイルオブジェクト

        Returns:
            Dict[str, Any]: 処理済みの設定データ
        """
        try:
            config = yaml.safe_load(uploaded_yaml)
            # st.session_state.user_inputs = []
            # st.session_state.min_user_inputs =
            # _initialize_user_inputs(config)
            return config
        except yaml.YAMLError as e:
            st.error(f"YAML解析エラー: {str(e)}")
            return {}
        except Exception as e:
            st.error(f"設定ファイルの処理に失敗しました: {str(e)}")
            return {}

    def _set_session_state(self, config):
        if "session_state" not in config:
            return

        cfg_session_state = config.get("session_state", {})
        # "method": st.session_state.method,
        # "uri": st.session_state.uri,
        # "header_df": st.session_state.header_df,
        # "req_body": st.session_state.req_body,
        # "use_dynamic_inputs": st.session_state.use_dynamic_inputs,
        # "user_property_path": st.session_state.user_property_path,
        if "method" in cfg_session_state:
            st.session_state.method = cfg_session_state.get("method")
        if "uri" in cfg_session_state:
            st.session_state.uri = cfg_session_state.get("uri")
        # if "header_df" in cfg_session_state:
        #     st.session_state.uri = cfg_session_state.get("header_df")
        if "req_body" in cfg_session_state:
            st.session_state.req_body = cfg_session_state.get("req_body")
        if "use_dynamic_inputs" in cfg_session_state:
            if cfg_session_state.get("use_dynamic_inputs") == "true":
                st.session_state.use_dynamic_inputs = True
            else:
                st.session_state.use_dynamic_inputs = False
        if "user_property_path" in cfg_session_state:
            st.session_state.user_property_path = cfg_session_state.get(
                "user_property_path"
            )

    def load_session_state(self):

        uploaded_file = st.file_uploader(
            label="Choose a YAML config file",
            type="yaml",
            on_change=self._on_file_upload,
        )

        if uploaded_file is not None and st.session_state.config is None:
            try:
                config = self._load_config(uploaded_file)
                if config:
                    st.session_state.config = config
                    self._set_session_state(config)
                    # main_viewer.config_viewer(st.session_state.config)
                    st.rerun()
            except yaml.YAMLError as e:
                st.error(f"Error loading YAML file: {e}")

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
                help="Save Session States",
                label="📥",
                disabled=st.session_state.api_running,
            ):
                self.modal("save_state")
        with col3:
            if st.button(
                help="Load Session States",
                label="📤",
                disabled=st.session_state.api_running,
            ):
                self.modal("load_state")
        with col4:
            pass
        with col5:
            pass
