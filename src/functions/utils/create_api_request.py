# create_api_request.py
import json

from fastapi import Request, HTTPException

from functions.ApiRequestor import ApiRequestor
from functions.ConfigProcess import ConfigProcess
from functions.utils.read_yaml_file import read_yaml_file
from functions.utils.convert_config_to_header import convert_config_to_header


async def create_api_request(request: Request):
    """
    リクエストからAPIリクエストの情報を抽出します。
    :param request: FastAPIのRequestオブジェクト
    :return: APIリクエストの情報 (辞書形式)
    """
    # --- 1. リクエストと設定読み込み ---
    api_request = {}
    try:
        body_data = await request.json()
        # api_logger.debug_log(f"request body: {body_data}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    num_user_inputs = body_data.get("num_user_inputs", 0)
    user_inputs = body_data.get("user_inputs", {})

    config_file_path = body_data.get("config_file")
    if not config_file_path:
        raise HTTPException(status_code=400, detail="Missing 'config_file'")
    config_data = read_yaml_file(config_file_path)

    config_process = ConfigProcess(config_data)
    session_state = config_process.get_from_session_sts()
    session_state["num_inputs"] = num_user_inputs
    for i in range(num_user_inputs):
        session_state[f"user_input_{i}"] = user_inputs.get(
            f"user_input_{i}", ""
        )

    api_url = config_process.get_from_session_sts("uri")
    method = config_process.get_from_session_sts("method")
    headers = convert_config_to_header(session_state)
    req_body_dict = (
        config_process.get_request_body() if method != "GET" else {}
    )
    req_body = json.loads(json.dumps(req_body_dict, ensure_ascii=False))

    if session_state.get("use_dynamic_inputs", False):
        api_requestor = ApiRequestor()
        api_url = api_requestor.replace_uri(session_state, api_url)
        req_body = json.loads(
            api_requestor.replace_body(session_state, json.dumps(req_body))
        )

    api_request["url"] = api_url
    api_request["method"] = method
    api_request["headers"] = headers
    api_request["req_body"] = req_body
    api_request["response_path"] = config_process.get_from_session_sts(
        "user_property_path"
    )

    # api_logger.info_log(f"API Client Request is {api_request}")

    return api_request
