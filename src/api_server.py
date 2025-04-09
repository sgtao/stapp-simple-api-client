# api_server.py
from fastapi import FastAPI
import uvicorn
import argparse

# from src.components.ConfigFiles import ConfigFiles
from components.ConfigFiles import ConfigFiles

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    parser.add_argument(
        "--port", type=int, default=3000, help="Port number to listen on"
    )
    args = parser.parse_args()

    print(f"Starting server on port: {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
