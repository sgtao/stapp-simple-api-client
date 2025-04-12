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

# from src.components.ConfigFiles import ConfigFiles
from components.ConfigFiles import ConfigFiles
from components.ResponseViewer import extract_property_from_json

app = FastAPI()


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


# @app.get("/api/v0/service/configs")
@app.post("/api/v0/service")
async def execute_service(request: Request):
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
    config_file_path = body_data.get("config_file")
    if not config_file_path:
        raise HTTPException(
            status_code=400,
            detail="Missing 'config_file' in request body",
        )
    config_data = read_yaml_file(config_file_path)

    # 3. Config データへの user_input_* の適用 (プレースホルダ置換)
    # processed_config = apply_user_inputs(config_data, user_inputs)
    processed_config = config_data.get("session_state")

    # 4. APIリクエスト情報の取得
    api_url = processed_config.get("uri")
    method = processed_config.get("method", "GET").upper()
    # headers = processed_config.get("header_df")
    headers = {"Content-Type": "application/json"}
    req_body_template = processed_config.get("req_body")
    response_path = processed_config.get("user_property_path")

    if not api_url:
        raise HTTPException(
            status_code=400, detail="Missing 'url' in processed config"
        )

    # 5. 外部APIへのリクエスト発行
    try:
        api_requestor = requests.Session()  # セッションを使うと効率が良い
        response = api_requestor.request(
            method=method,
            url=api_url,
            headers=headers,  # processed_config から取得したヘッダー
            json=(
                req_body_template if method in ["POST", "PUT"] else None
            ),  # processed_config から取得したボディ
        )
        response.raise_for_status()  # HTTPエラーチェック
        api_response_json = response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to request external API: {e}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502, detail="External API did not return valid JSON"
        )

    # 6. レスポンスの処理 (指定されたパスで抽出)
    # extracted_value = api_response_json
    extracted_value = extract_property_from_json(
        api_response_json, response_path
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
