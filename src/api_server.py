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

from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger
from functions.ConfigProcess import ConfigProcess
from functions.LlmAPI import LlmAPI

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
        auth_value = header_item["Value"].replace("＜API_KEY＞", api_key)
        header_dict[f"{header_item['Property']}"] = auth_value
    return header_dict


@app.get("/api/v0/hello")
@app.post("/api/v0/hello")
async def hello(request: Request):
    """
    GETとPOSTメソッドで`/api/v0/hello`エンドポイントにアクセスすると、
    JSON形式で`{"result": "hello"}`を返します。
    """
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"{request.url.path} Receive {request.method}")
    return {"result": "hello"}


@app.get("/api/v0/configs")
async def configs(request: Request):
    """
    JSON形式で`{"result": [config_files]}`を返します。
    """
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"{request.url.path} Receive {request.method}")
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
    print(f"Receive message in {body_data}")
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


async def create_api_request(
    request: Request,
    APP_NAME="api_server",
):
    """
    リクエストからAPIリクエストの情報を抽出します。
    :param request: FastAPIのRequestオブジェクト
    :return: APIリクエストの情報 (辞書形式)
    """
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"Creating API request from {request.url.path}")

    # 初期化
    # api_request = {
    #     "url": "",
    #     "method": "GET",
    #     "headers": {},
    #     "body": {},
    #     "response_path": None,
    # }
    api_request = {}

    # --- 1. リクエストと設定読み込み ---
    try:
        body_data = await request.json()
        api_logger.debug_log(f"request body: {body_data}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    # リクエストボディのuser_inputs検証
    num_user_inputs = body_data.get("num_user_inputs", 0)
    user_inputs = body_data.get("user_inputs", {})

    config_file_path = body_data.get("config_file")
    if not config_file_path:
        raise HTTPException(status_code=400, detail="Missing 'config_file'")
    config_data = read_yaml_file(config_file_path)
    api_logger.debug_log(f"config_data: {config_data}")

    config_process = ConfigProcess(config_data)
    session_state = config_process.get_from_session_sts()
    # api_logger.debug_log(f"session_state pre modified: {session_state}")
    session_state["num_inputs"] = num_user_inputs
    for i in range(num_user_inputs):
        key = f"user_input_{i}"
        session_state[key] = user_inputs.get(key, "")
    # api_logger.debug_log(f"session_state: {session_state}")

    api_url = config_process.get_from_session_sts("uri")
    method = config_process.get_from_session_sts("method")
    headers = convert_config_to_header(session_state)
    req_body_dict = (
        config_process.get_request_body() if method != "GET" else {}
    )
    conf_req_body = json.dumps(req_body_dict, ensure_ascii=False)
    # api_logger.debug_log(
    #     f"conf_req_body(type{type(conf_req_body)}): {conf_req_body}"
    # )
    req_body = json.loads(conf_req_body)
    dynamic_inputs = session_state.get("use_dynamic_inputs", False)
    if dynamic_inputs:
        """URIとリクエストボディの動的変数置換を行う"""
        api_requestor = ApiRequestor()
        api_url = api_requestor.replace_uri(session_state, api_url)
        # api_logger.debug_log(f"api_url: {api_uri}")
        _req_body = api_requestor.replace_body(session_state, conf_req_body)
        # api_logger.debug_log(f"req_body: {_req_body}")
        req_body = json.loads(_req_body)

    response_path = config_process.get_from_session_sts("user_property_path")
    # api_logger.debug_log(f"dynamic_inputs: {dynamic_inputs}")

    api_request["url"] = api_url
    api_request["method"] = method
    api_request["headers"] = headers
    api_request["req_body"] = req_body
    api_request["response_path"] = response_path

    api_logger.info_log(f"API Client Request is {api_request}")

    return api_request


async def send_api_request(
    url,
    method,
    headers,
    req_body,
    response_path=None,
    APP_NAME="api_server",
):
    """
    APIRequestorを使ってAPIリクエストを送信します。
    :param url: APIのURI
    :param method: HTTPメソッド (GET, POST, PUT, DELETE)
    :param headers: リクエストヘッダー (辞書形式)
    :param req_body: リクエストボディ (辞書形式)
    :return: レスポンスオブジェクト
    """
    # --- 1. Logger setting ---
    api_logger = AppLogger(f"{APP_NAME}( to {url}):")

    # --- 2. APIRequestor を使った置換とリクエスト ---
    try:
        api_requestor = ApiRequestor()
        response = api_requestor.send_request(
            url=url, method=method, headers=headers, body=req_body
        )
        api_response_json = response.json()
    except Exception as e:
        api_logger.error_log(f"APIリクエスト失敗: {e}")
        raise HTTPException(status_code=502, detail=f"APIリクエスト失敗: {e}")

    # return response
    # --- 3. レスポンス抽出 ---
    try:
        result = extract_property_from_json(api_response_json, response_path)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"レスポンス抽出エラー: {e}"
        )

    return JSONResponse(content={"result": result})


@app.post("/api/v0/service")
async def execute_service(request: Request):
    """
    config_file で指定したAPIを実行し、
    JSON形式で`{"result": [user_property value]}`を返します。
    """
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    # --- 1. リクエストと設定読み込み ---
    try:
        api_request = await create_api_request(
            request=request,
            APP_NAME=f"{APP_NAME}({request.url.path}):",
        )
    except Exception as e:
        api_logger.error_log(f"APIリクエスト作成失敗: {e}")
        raise HTTPException(
            status_code=400, detail=f"APIリクエスト作成失敗: {e}"
        )

    # --- 2. APIRequestor を使った置換とリクエスト ---
    try:
        return await send_api_request(
            url=api_request["url"],
            method=api_request["method"],
            headers=api_request["headers"],
            req_body=api_request["req_body"],
            response_path=api_request["response_path"],
            APP_NAME=f"{APP_NAME}({request.url.path}):",
        )
    except Exception as e:
        api_logger.error_log(f"APIリクエスト失敗: {e}")
        raise HTTPException(status_code=502, detail=f"APIリクエスト失敗: {e}")


# process request with message via `/api/v0/messages"`
@app.post("/api/v0/messages")
async def post_messages(request: Request):
    """
    messagesを含むリクエストを受け取り、
    config_file で指定したAPIを実行し、
    JSON形式で`{"result": [user_property value]}`を返します。
    """
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    # --- 1. リクエストと設定読み込み ---
    try:
        messages = []
        api_request = await create_api_request(
            request=request,
            APP_NAME=f"{APP_NAME}({request.url.path}):",
        )
        if api_request["method"] == "GET":
            api_logger.info_log("cannot support to GET request")
            raise HTTPException(
                status_code=400, detail="cannot support to GET request"
            )
        # get message from request
        body_data = await request.json()
        messages = body_data.get("messages")

    except Exception as e:
        api_logger.error_log(f"APIリクエスト作成失敗: {e}")
        raise HTTPException(
            status_code=400, detail=f"APIリクエスト作成失敗: {e}"
        )

    # --- 2. LlmAPIを使った変換とリクエスト ---
    try:
        llm = LlmAPI(
            # uri=sent_uri,
            uri=api_request["url"],
            header_dict=api_request["headers"],
            req_body=api_request["req_body"],
            user_property_path=api_request["response_path"],
        )

        # send message:
        response = llm.single_response(messages)

        # 結果の返却
        return JSONResponse(content={"result": response})

    except Exception as e:
        api_logger.error_log(f"APIリクエスト失敗: {e}")
        raise HTTPException(status_code=502, detail=f"APIリクエスト失敗: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    parser.add_argument(
        "--port", type=int, default=3000, help="Port number to listen on"
    )
    args = parser.parse_args()

    print(f"Starting server on port: {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
