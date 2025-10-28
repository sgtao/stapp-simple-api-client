# search_controller.py
from fastapi import APIRouter, Query
import httpx


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
