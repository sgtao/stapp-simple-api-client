# service_controller.py
# import json

from fastapi import APIRouter, Request, HTTPException

from functions.AppLogger import AppLogger

# from functions.utils.read_yaml_file import read_yaml_file
# from functions.utils.convert_config_to_header import convert_config_to_header
# from functions.ConfigProcess import ConfigProcess
from functions.ApiRequestor import ApiRequestor
from functions.ResponseOperator import ResponseOperator
from functions.utils.create_api_request import create_api_request

APP_NAME = "api_server"
router = APIRouter(tags=["Service"])


async def send_api_request(url, method, headers, req_body, response_path=None):
    """
    APIRequestorを使ってAPIリクエストを送信します。
    :param url: APIのURI
    :param method: HTTPメソッド (GET, POST, PUT, DELETE)
    :param headers: リクエストヘッダー (辞書形式)
    :param req_body: リクエストボディ (辞書形式)
    :return: レスポンスオブジェクト
    """
    api_logger = AppLogger(APP_NAME)
    api_requestor = ApiRequestor()
    response_op = ResponseOperator()
    response = api_requestor.send_request(url, method, headers, req_body)
    api_response_json = response.json()
    result = response_op.extract_property_from_json(
        api_response_json, response_path
    )
    api_logger.info_log(f"Return API response result: {result}")

    return {"results": result}


@router.post("/service")
async def execute_service(request: Request):
    """
    リクエストを受け取り、config_file で指定したAPIを実行し、
    JSON形式で`{"results": [user_property value]}`を返します。
    """
    # --- 1. Logger setting and Instanciation ---
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    try:
        api_request = await create_api_request(request)
        api_logger.info_log(f"API Client Request is {api_request}")
        # api_logger.info_log(f"API request URI: {api_request.url.path}")
        return await send_api_request(**api_request)
    except Exception as e:
        api_logger.error_log(f"API request is failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
