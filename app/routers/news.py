import os
import re
from xml.etree import ElementTree

import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/news", tags=["news"])

FEED_URL = os.environ.get("DASHBOARD_NEWS_FEED", "http://feeds.bbci.co.uk/news/rss.xml")


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


@router.get("")
async def get_news(limit: int = 6):
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        resp = await client.get(FEED_URL)
        resp.raise_for_status()

    root = ElementTree.fromstring(resp.content)
    items = root.findall("./channel/item")[:limit]

    snippets = []
    for item in items:
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        description = strip_html(item.findtext("description", ""))
        snippets.append({"title": title, "link": link, "summary": description})

    return snippets
