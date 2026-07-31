import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


TOKEN = os.environ.get("IG_ACCESS_TOKEN")
IG_USER_ID = os.environ.get("IG_USER_ID", "me")
API_VERSION = os.environ.get("META_GRAPH_VERSION", "v26.0")
API_HOST = os.environ.get("IG_API_HOST", "https://graph.instagram.com")
OUTPUT_PATH = Path(os.environ.get("OUTPUT_PATH", "instagram.json"))


def format_int(value):
    if value is None:
        return None
    return f"{int(value):,}".replace(",", " ")


def fetch_stats():
    if not TOKEN:
        print("Missing IG_ACCESS_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)

    fields = [
        "id",
        "username",
        "followers_count",
        "follows_count",
        "media_count",
        "profile_picture_url",
    ]
    query = urlencode({
        "fields": ",".join(fields),
        "access_token": TOKEN,
    })
    url = f"{API_HOST.rstrip('/')}/{API_VERSION}/{IG_USER_ID}?{query}"

    with urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if "error" in payload:
        print(json.dumps(payload["error"], indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    followers = payload.get("followers_count")
    following = payload.get("follows_count")
    posts = payload.get("media_count")

    return {
        "username": payload.get("username", "oliver_blaha_gallery"),
        "followers": followers,
        "followers_count": followers,
        "followers_display": format_int(followers),
        "following": following,
        "following_display": format_int(following),
        "posts": posts,
        "posts_display": format_int(posts),
        "profile_picture_url": payload.get("profile_picture_url"),
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def main():
    stats = fetch_stats()
    OUTPUT_PATH.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
