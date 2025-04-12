# ResponseViewer.py
import json

import streamlit as st


def extract_property_from_json(json_data, property_path):
    """
    JSONデータから指定されたプロパティパスの値を取得します。

    Args:
        json_data (dict): JSONデータ
        property_path (str): プロパティパス (例: "completion.tags[0].value")

    Returns:
        any: プロパティパスに対応する値。エラーが発生した場合はNone
    """
    try:
        # プロパティパスを分割し、各キーを順番に辿る
        keys = property_path.split(".")
        value = json_data

        for key in keys:
            # リストのインデックスにアクセスする場合
            if "[" in key and "]" in key:
                # キーとインデックスを分離
                key_name, index = key.split("[")
                index = int(index[:-1])  # 閉じ括弧を削除して整数に変換

                # キーが存在しない場合はエラー
                if key_name and key_name not in value:
                    raise KeyError(f"キー '{key_name}' が見つかりません。")

                # インデックスが無効な場合はエラー
                if not isinstance(value[key_name], list) or index >= len(
                    value[key_name]
                ):
                    raise IndexError(f"インデックス '{index}' が範囲外です。")

                value = value[key_name][index]
            else:
                # キーが存在しない場合はエラー
                if key not in value:
                    raise KeyError(f"キー '{key}' が見つかりません。")
                value = value[key]

        return value
    except (KeyError, TypeError, IndexError) as e:
        # プロパティが見つからない場合はエラーメッセージを返す
        st.error(f"プロパティの抽出に失敗しました: {e}")
        return None


class ResponseViewer:
    def __init__(self, response_path=None):
        if "user_property_path" not in st.session_state:
            if response_path:
                st.session_state.user_property_path = response_path
            else:
                st.session_state.user_property_path = ""

    def response_content(self, response):
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return "application/json"
        elif "text/html" in content_type:
            return "text/html"
        elif "text/plain" in content_type:
            return "text/plain"
        else:
            return "unsupported"

    def header_viewer(self, response):
        with st.expander("レスポンスヘッダー"):
            try:
                # 辞書形式のヘッダーをJSONとして表示
                st.json(dict(response.headers))
            except Exception as e:
                st.error(
                    f"レスポンスヘッダーの表示中にエラーが発生しました: {str(e)}"
                )

    def body_viewer(self, content_type, response):
        with st.expander("レスポンスボディ"):
            try:
                if content_type == "application/json":
                    # JSON形式の場合
                    st.json(response.json())
                else:
                    # Text / HTML の場合
                    st.markdown(response.text)
            except json.JSONDecodeError:
                st.text(response.text)  # テキスト形式の場合

    def render_extracted_value(self, extracted_value):
        """抽出された値をタブで表示する"""
        tabs = st.tabs(
            [
                "markdown",
                "text",
                "json",
                "code",
                "html",
            ]
        )
        with tabs[0]:
            st.markdown(str(extracted_value))
        with tabs[1]:
            st.write(extracted_value)
        with tabs[2]:
            try:
                st.json(extracted_value)
            except Exception as e:
                st.error(
                    f"""Exception occured: {e}
                        JSON形式で表示できませんでした。元の値を表示します:
                        {extracted_value}
                    """
                )
        with tabs[3]:
            st.code(extracted_value)
        with tabs[4]:
            st.html(extracted_value)

    def render_viewer(self, response):
        try:
            # st.text(response.status_code)
            st.metric(label="Status Code", value=response.status_code)
            content_type = self.response_content(response)
            # if "headers" in response:
            #     self.header_viewer(response)
            #     self.body_viewer(content_type, response)
            self.header_viewer(response)
            self.body_viewer(content_type, response)

            if st.session_state.user_property_path != "":
                # 抽出したいプロパティの指定
                property_path = st.session_state.user_property_path

                if content_type == "application/json":
                    response_json = response.json()  # JSON形式の場合
                    extracted_value = extract_property_from_json(
                        response_json, property_path
                    )
                else:
                    # extracted_value = response.body
                    extracted_value = response.text

                # 抽出された値を表示
                if extracted_value is not None:
                    st.success(f"Extracted Value({property_path}): Found.")
                    # st.markdown(extracted_value)
                    self.render_extracted_value(extracted_value)
                else:
                    st.warning(f"Extracted Value({property_path}): Not Found!")

        except json.JSONDecodeError:
            st.text(response.text)  # テキスト形式の場合
        except TypeError:
            st.error("プロパティの型が想定と異なります。")
