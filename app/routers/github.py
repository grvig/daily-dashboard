import os
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/github", tags=["github"])

GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "grvig")


def compute_push_streak(events: list[dict]) -> int:
    push_dates = {
        datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).date()
        for e in events
        if e.get("type") == "PushEvent"
    }
    if not push_dates:
        return 0

    today = datetime.now(timezone.utc).date()
    streak = 0
    day = today
    # Allow the streak to still count if today has no push yet.
    if day not in push_dates:
        day -= timedelta(days=1)
    while day in push_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


@router.get("")
async def get_github_stats():
    async with httpx.AsyncClient(timeout=10, headers={"Accept": "application/vnd.github+json"}) as client:
        profile_resp = await client.get(f"https://api.github.com/users/{GITHUB_USERNAME}")
        if profile_resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"GitHub user '{GITHUB_USERNAME}' not found")
        profile_resp.raise_for_status()
        profile = profile_resp.json()

        events_resp = await client.get(
            f"https://api.github.com/users/{GITHUB_USERNAME}/events/public",
            params={"per_page": 100},
        )
        events_resp.raise_for_status()
        events = events_resp.json()

    return {
        "username": profile["login"],
        "public_repos": profile["public_repos"],
        "followers": profile["followers"],
        "streak_days": compute_push_streak(events),
    }
