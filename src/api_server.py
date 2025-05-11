# api_server.py
# import sys
import os

# import glob
import argparse
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import yaml
import requests
import urllib.parse

# from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

# from src.components.ConfigFiles import ConfigFiles
from components.ConfigFiles import ConfigFiles
from components.ResponseViewer import extract_property_from_json

app = FastAPI()
APP_NAME = "api_server"


def read_yaml_file(file_path):
    """YAMLファイルの内容を読み込みます。"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Config file not found: {os.path.basename(file_path)}",
        )
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=500, detail=f"Error parsing YAML file: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading config file: {e}"
        )


def convert_config_to_header(config):
    header_dict = {}
    api_key = os.getenv("API_KEY")

    config_headers = config.get("header_df")
    for header_item in config_headers:
        if header_item["Property"] == "Authorization":
            auth_value = header_item["Value"].replace("＜API_KEY＞", api_key)
            header_dict["Authorization"] = auth_value
        else:
            header_dict[f"{header_item['Property']}"] = header_item["Value"]
    return header_dict


@app.get("/api/v0/hello")
@app.post("/api/v0/hello")
async def hello():
    """
    GETとPOSTメソッドで`/api/v0/hello`エンドポイントにアクセスすると、
    JSON形式で`{"result": "hello"}`を返します。
    """
    return {"result": "hello"}


# @app.get("/api/v0/service/configs")
@app.get("/api/v0/configs")
async def configs():
    """
    JSON形式で`{"result": [config_files]}`を返します。
    """
    # assets/privatesフォルダからyamlファイルを選択
    config_files = ConfigFiles()
    config_files_list = config_files.get_config_files_list()
    return {"result": config_files_list}


@app.post("/api/v0/config-title")
async def config_title(request: Request):
    api_logger = AppLogger(APP_NAME)
    """
    config_file で指定したファイルの`title`と`note`を返します。
    """
    try:
        body_data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON format in request body"
        )

    # 1. config_file の取得とYAML読み込み
    print(body_data)
    config_file_path = body_data.get("config_file")
    api_logger.debug_log(f"Request Config title of {config_file_path}")
    if not config_file_path:
        raise HTTPException(
            status_code=400,
            detail="Missing 'config_file' in request body",
        )
    config_data = read_yaml_file(config_file_path)
    result_data = {}
    if "title" in config_data:
        result_data["title"] = config_data.get("title")
    if "note" in config_data:
        result_data["note"] = config_data.get("note")

    api_logger.debug_log(f"Return Config title: {result_data}")
    return {"result": result_data}


# @app.get("/api/v0/service/configs")
@app.post("/api/v0/service")
async def execute_service(request: Request):
    api_logger = AppLogger(APP_NAME)
    """
    config_file で指定したAPIを実行し、
    JSON形式で`{"result": [user_property value]}`を返します。
    """
    # assets/privatesフォルダからyamlファイルを選択
    # config_files = ConfigFiles()
    # config_files_list = config_files.get_config_files_list()
    try:
        body_data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON format in request body"
        )

    # 1. config_file の取得とYAML読み込み
    print(body_data)
    config_file_path = body_data.get("config_file")
    if not config_file_path:
        raise HTTPException(
            status_code=400,
            detail="Missing 'config_file' in request body",
        )
    config_data = read_yaml_file(config_file_path)

    # 2. Config データへの user_input_* の適用 (プレースホルダ置換)
    # processed_config = apply_user_inputs(config_data, user_inputs)
    processed_config = config_data.get("session_state")

    # 3. APIリクエスト情報の取得
    api_url = processed_config.get("uri")
    method = processed_config.get("method", "GET").upper()
    # headers = {"Content-Type": "application/json"}
    try:
        # processed_config に api_key など、ヘッダー生成に必要な情報が含まれる想定
        headers = convert_config_to_header(processed_config)
        api_logger.debug_log(f"Generated headers: {headers}")
    except Exception as e:
        api_logger.error_log(f"Failed to convert config to header: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process headers from config: {e}",
        )

    req_body_template_str = processed_config.get("req_body")
    response_path = processed_config.get("user_property_path")

    if not api_url:
        raise HTTPException(
            status_code=400, detail="Missing 'url' in processed config"
        )

    # 4. コンフィグ情報の置換
    # number_user_inputs = body_data.get("num_user_inputs")
    user_inputs = body_data.get("user_inputs")
    replaced_uri = api_url
    # print(f"Original URI: {api_url}")
    print(f"user_inputs: {user_inputs}")
    # # user_inputs が辞書であることを確認
    # if isinstance(user_inputs, dict):
    for key, user_input_value in user_inputs.items():
        # user_input_value が None でないことを確認
        if user_input_value is not None:
            # print(
            #     f"Replacing placeholder ＜{key}＞ with '{user_input_value}'"
            # )
            # URI の置換
            value_encoded = urllib.parse.quote(str(user_input_value))
            placeholder = f"＜{key}＞"
            replaced_uri = replaced_uri.replace(f"＜{key}＞", value_encoded)
            if placeholder in replaced_uri:
                replaced_uri = replaced_uri.replace(placeholder, value_encoded)
                api_logger.debug_log(
                    f"Replaced '{placeholder}' in URI with '{value_encoded}'"
                )
    api_logger.debug_log(f"Final request URI: {replaced_uri}")

    # リクエストボディのプレースホルダ置換とJSONパース
    request_body_dict = None
    if req_body_template_str:
        processed_req_body_str = req_body_template_str

        if method in ["POST", "PUT"] and req_body_template_str:
            if isinstance(user_inputs, dict):
                for key, user_input_value in user_inputs.items():
                    if user_input_value is not None:
                        # 単純置換
                        placeholder = f"＜{key}＞"
                        # 値を文字列に変換して置換 (エスケープなし)
                        processed_req_body_str = (
                            processed_req_body_str.replace(
                                placeholder, str(user_input_value)
                            )
                        )
                        api_logger.debug_log(
                            f"Replaced '{placeholder}' in body template with "
                            + f"'{user_input_value}' (simple string replace)"
                        )

            api_logger.debug_log(
                f"""Processed request body string after replacements:
                {processed_req_body_str}"""
            )

            try:
                request_body_dict = json.loads(processed_req_body_str)
                api_logger.debug_log(
                    f"Parsed request body dict/list: {request_body_dict}"
                )
            except json.JSONDecodeError as e:
                api_logger.error_log(
                    f"""Failed to decode request body string into JSON:
                    {e} - Body: {processed_req_body_str}"""
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"""Failed to parse request body after replacements.
                    Check user inputs and template format. Error: {e}""",
                )

    # 5. 外部APIへのリクエスト発行
    try:
        # api_requestor = ApiRequestor()
        api_requestor = requests.Session()  # セッションを使うと効率が良い
        api_logger.api_start_log(
            replaced_uri, method, headers, request_body_dict
        )

        # response = api_requestor.send_request(
        # response = await api_requestor.request(
        response = api_requestor.request(
            method=method,
            # url=api_url,
            url=replaced_uri,
            headers=headers,  # processed_config から取得したヘッダー
            # data=None # 'json' を使う場合は 'data' は通常 None
            # body=(
            # json=(
            #     # 4. 置換したリクエストボディ
            #     # json.load(req_body_template)
            #     req_body_template
            #     if method in ["POST", "PUT"]
            #     else None
            # ),
            json=request_body_dict,
            timeout=30,
        )
        # HTTPエラーチェック
        response.raise_for_status()
        api_logger.api_success_log(response)
        api_response_json = response.json()

    except requests.exceptions.HTTPError as http_err:
        # 外部APIが 4xx, 5xx エラーを返した場合
        err_status = "N/A"
        err_reason = "N/A"
        err_detail = "N/A"
        response_text = "N/A"
        if http_err.response is not None:
            err_status = http_err.response.status_code
            err_reason = http_err.response.reason
            response_text = http_err.response.text
            try:
                err_detail = http_err.response.json()
            except json.JSONDecodeError:
                err_detail = response_text
        api_logger.error_log(f"HTTP error occurred: {http_err}")
        api_logger.error_log(
            f"Status: {err_status}, Reason: {err_reason}, Detail: {err_detail}"
        )
        # 外部APIからのエラーなので 502 Bad Gateway を返すのが一般的
        raise HTTPException(
            status_code=502,
            detail=f"""External API Error: {err_status} {err_reason}.
            Detail: {err_detail}""",
        )

    except requests.exceptions.RequestException as req_err:
        # 接続エラー、タイムアウト、DNS解決エラーなど
        api_logger.error_log(
            f"Request error occurred (Connection/Timeout etc.): {req_err}"
        )
        # 外部APIへの接続失敗なので 504 Gateway Timeout などが考えられる
        raise HTTPException(
            status_code=504,
            detail=f"Failed to connect to external API: {req_err}",
        )

    except json.JSONDecodeError as e:
        # 外部APIからの正常レスポンス(2xx)がJSON形式でなかった場合
        resp_text = (
            response.text
            if "response" in locals() and hasattr(response, "text")
            else "N/A"
        )
        api_logger.error_log(
            f"""External API did not return valid JSON
            for a successful response: {e} - Response Text: {resp_text}"""
        )
        raise HTTPException(
            status_code=502,  # 外部APIのレスポンス形式が不正なので 502
            detail="External API returned non-JSON response with success",
        )

    except Exception as e:
        # 予期せぬその他のエラー
        api_logger.error_log(
            f"An unexpected error occurred during API request execution: {e}",
            exc_info=True,
        )  # トレースバックも記録
        raise HTTPException(
            status_code=500,  # サーバー内部のエラー
            detail=f"An internal server error occurred: {e}",
        )

    # 6. レスポンスの処理 (指定されたパスで抽出)
    # extracted_value = api_response_json
    try:
        extracted_value = extract_property_from_json(
            api_response_json, response_path
        )
        if extracted_value is None and response_path:
            api_logger.warning(
                f"Property path '{response_path}' not found or null value."
            )
        else:
            api_logger.info_log(
                f"Successfully extracted value using path '{response_path}'"
            )
    except Exception as e:
        api_logger.error_log(
            f"""Failed to extract property using path '{response_path}'
            from response: {e}""",
            exc_info=True,
        )
        # 抽出失敗は内部エラーとして 500 を返すか、状況に応じて判断
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process response from external API: {e}",
        )

    # 7. 結果の返却
    return JSONResponse(content={"result": extracted_value})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    parser.add_argument(
        "--port", type=int, default=3000, help="Port number to listen on"
    )
    args = parser.parse_args()

    print(f"Starting server on port: {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
