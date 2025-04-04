# ApiResponseViewer.py
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


class ApiResponseViewer:
    def render_viewer(self, response):
        # st.text(response.status_code)
        st.metric(label="Status Code", value=response.status_code)

        if st.session_state.user_property_path != "":
            response_json = response.json()  # JSON形式の場合
            property_path = st.session_state.user_property_path
            # 抽出したいプロパティの指定
            try:
                # property_value =
                #     response_json["completion"]["tags"][0]["value"]
                # property_value = response_json["tags"][0]
                # st.write(f"Extracted Value: {property_value}")

                extracted_value = extract_property_from_json(
                    response_json, property_path
                )
                # 抽出された値を表示
                if extracted_value is not None:
                    st.success(f"Extracted Value({property_path}): Found.")
                    st.markdown(extracted_value)
                else:
                    st.warning(f"Extracted Value({property_path}): Not Found!")

            except json.JSONDecodeError:
                st.text(response.text)  # テキスト形式の場合
            except TypeError:
                st.error("プロパティの型が想定と異なります。")

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
