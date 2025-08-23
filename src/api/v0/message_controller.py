# message_controller.py
from fastapi import APIRouter, Request, HTTPException

from functions.AppLogger import AppLogger
from functions.LlmAPI import LlmAPI
from functions.utils.create_api_request import create_api_request

APP_NAME = "api_server"
router = APIRouter(tags=["Messages"])


async def process_llm_request(request: Request):
    api_request = await create_api_request(request)
    if api_request["method"] == "GET":
        raise HTTPException(
            status_code=400, detail="GET not supported for messages"
        )

    body_data = await request.json()
    messages = body_data.get("messages")

    llm = LlmAPI(
        uri=api_request["url"],
        header_dict=api_request["headers"],
        req_body=api_request["req_body"],
        user_property_path=api_request["response_path"],
    )
    response = llm.single_response(messages)
    return {"result": response}


@router.post("/messages")
async def post_messages(request: Request):
    """
    messagesを含むリクエストを受け取り、
    config_file で指定したAPIを実行し、
    JSON形式で`{"result": [user_property value]}`を返します。
    """
    # --- 1. Logger setting and Instanciation ---
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    # --- 2. LlmAPIを使った変換とリクエスト ---
    try:
        return await process_llm_request(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
