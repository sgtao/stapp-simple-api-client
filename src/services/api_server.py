# api_server.py
from fastapi import FastAPI
import uvicorn
import argparse

app = FastAPI()


@app.get("/api/v0/hello")
@app.post("/api/v0/hello")
async def hello():
    """
    GETとPOSTメソッドで`/api/v0/hello`エンドポイントにアクセスすると、
    JSON形式で`{"result": "hello"}`を返します。
    """
    return {"result": "hello"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    parser.add_argument(
        "--port", type=int, default=3000, help="Port number to listen on"
    )
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
