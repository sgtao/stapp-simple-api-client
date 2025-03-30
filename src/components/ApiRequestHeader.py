# ApiRequestHeader.py
import pandas as pd
import streamlit as st


class ApiRequestHeader:
    def __init__(self):
        self.header_df = None

    def render_editor(self):
        self.header_df = st.data_editor(
            st.session_state.header_df,
            num_rows="dynamic",
            use_container_width=True,
        )
        st.session_state.header_df = self.header_df

        # ボタンで行追加・削除
        col1, col2 = st.columns(2)
        with col1:
            if st.button("行を追加"):
                new_row = {"Property": "foo", "Value": "bar"}
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

    def get_header_dict(self):
        header_dict = {}
        # ヘッダー情報を辞書形式に変換
        # header_dict = header_df.to_dict()
        # header_list = header_df.values.tolist()
        header_list = self.header_df.values.tolist()
        # print(header_list)
        # header_dict = {item[0]: item[1] for item in header_list}
        for item in header_list:
            key = item[0]
            value = item[1]
            # header_dict.append(dict({key, value}))
            header_dict[key] = value

        return header_dict
