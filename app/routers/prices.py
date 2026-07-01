import os

import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/prices", tags=["prices"])

# CoinGecko coin ids, comma-separated (no API key required for this endpoint).
COIN_IDS = os.environ.get("DASHBOARD_COINS", "bitcoin,ethereum,solana").split(",")


@router.get("")
async def get_prices():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": ",".join(COIN_IDS),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return [
        {
            "id": coin_id,
            "price_usd": info["usd"],
            "change_24h_pct": round(info.get("usd_24h_change", 0), 2),
        }
        for coin_id, info in data.items()
    ]
