# search_controller.py
# from bs4 import BeautifulSoup
from fastapi import APIRouter, Query
import httpx
from duckduckgo_search import DDGS
from urllib.parse import urlparse


APP_NAME = "api_server"
router = APIRouter(tags=["Service"])

DUCK_API_URL = "https://api.duckduckgo.com/"


@router.get("/search")
async def search_web(q: str = Query(..., description="Search keyword")):
    """DuckDuckGoのInstant Answer APIで検索"""
    params = {"q": q, "format": "json", "no_redirect": 1, "no_html": 1}
    async with httpx.AsyncClient() as client:
        res = await client.get(DUCK_API_URL, params=params)
        data = res.json()

    results = []
    if "RelatedTopics" in data:
        for topic in data["RelatedTopics"]:
            if "Text" in topic:
                results.append(
                    {
                        "title": topic["Text"],
                        "url": topic.get("FirstURL", ""),
                    }
                )

    return {"count": len(results), "results": results}


async def fetch_snippet(client: httpx.AsyncClient, url: str) -> str:
    """ページのスニペットをmetaタグや冒頭文から抽出"""
    try:
        # print(f"scrape uri: {url}")
        # 1. URLを解析
        parsed = urlparse(url)

        # 2. パスの末尾部分
        # （例: "/c/Artificial_intelligence_associations"
        #  → "Artificial_intelligence_associations"）
        path = parsed.path.strip("/")
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "c":
            query = parts[1]
        else:
            return {"error": "Invalid DuckDuckGo category URI"}

        results = DDGS().text(query, max_results=5)
        # print(results)
        return results
    except Exception:
        return "(スニペット取得に失敗しました)"
    return "(説明文なし)"


@router.get("/search_scrape")
async def search_scrape(q: str = Query(...)):
    """DuckDuckGoのInstant Answer APIで検索＋スニペット抽出"""
    params = {"q": q, "format": "json", "no_redirect": 1, "no_html": 1}
    results = []

    async with httpx.AsyncClient() as client:
        res = await client.get(DUCK_API_URL, params=params)
        data = res.json()

        if "RelatedTopics" in data:
            # RelatedTopics からURLとタイトルを取得
            for topic in data["RelatedTopics"]:
                if "Text" in topic and "FirstURL" in topic:
                    snippet = await fetch_snippet(client, topic["FirstURL"])
                    results.append(
                        {
                            "title": topic["Text"],
                            "uri": topic["FirstURL"],
                            "snippet": snippet,
                        }
                    )

    return {"count": len(results), "results": results}
