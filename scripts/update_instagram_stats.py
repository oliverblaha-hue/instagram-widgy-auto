import json
import os
import sys
import re
from http.cookiejar import CookieJar
from html import unescape
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen


TOKEN = os.environ.get("IG_ACCESS_TOKEN")
IG_USER_ID = os.environ.get("IG_USER_ID", "me")
PUBLIC_USERNAME = os.environ.get("IG_PUBLIC_USERNAME", "oliver_blaha_gallery")
API_VERSION = os.environ.get("META_GRAPH_VERSION", "v26.0")
API_HOST = os.environ.get("IG_API_HOST", "https://graph.instagram.com")
OUTPUT_PATH = Path(os.environ.get("OUTPUT_PATH", "instagram.json"))
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)


def format_int(value):
    if value is None:
        return None
    return f"{int(value):,}".replace(",", " ")


def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_count(value):
    text = value.strip().replace("\xa0", "").replace(" ", "")
    suffix = text[-1:].upper()
    multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(suffix, 1)
    if multiplier != 1:
        text = text[:-1]
    text = text.replace(",", "")
    return int(float(text) * multiplier)


def fetch_api_stats():
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
        "username": payload.get("username", PUBLIC_USERNAME),
        "followers": followers,
        "followers_count": followers,
        "followers_display": format_int(followers),
        "following": following,
        "following_display": format_int(following),
        "posts": posts,
        "posts_display": format_int(posts),
        "profile_picture_url": payload.get("profile_picture_url"),
        "updated_at": now_utc(),
        "source": "instagram_api",
    }


def fetch_public_profile_stats(username):
    url = f"https://www.instagram.com/{username}/?hl=en"
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        },
    )

    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")

    description_match = re.search(
        r'<meta\s+(?:property="og:description"|content="[^"]*"\s+name="description")[^>]*content="([^"]+)"',
        html,
    )
    if not description_match:
        description_match = re.search(r'<meta\s+content="([^"]+)"\s+name="description"', html)

    if not description_match:
        raise RuntimeError("Could not find Instagram profile description in public HTML.")

    description = unescape(description_match.group(1))
    counts_match = re.search(
        r"([0-9][0-9,.\s]*[KMB]?)\s+Followers,\s+"
        r"([0-9][0-9,.\s]*[KMB]?)\s+Following,\s+"
        r"([0-9][0-9,.\s]*[KMB]?)\s+Posts",
        description,
        re.IGNORECASE,
    )
    if not counts_match:
        raise RuntimeError(f"Could not parse Instagram counts from: {description}")

    image_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
    followers = parse_count(counts_match.group(1))
    following = parse_count(counts_match.group(2))
    posts = parse_count(counts_match.group(3))

    return {
        "username": username,
        "followers": followers,
        "followers_count": followers,
        "followers_display": format_int(followers),
        "following": following,
        "following_display": format_int(following),
        "posts": posts,
        "posts_display": format_int(posts),
        "profile_picture_url": unescape(image_match.group(1)) if image_match else None,
        "updated_at": now_utc(),
        "source": "instagram_public_profile",
        "note": "Neoficialni verejny fallback bez Meta API tokenu. Muze se rozbit, kdyz Instagram zmeni HTML.",
    }


def fetch_instastatistics_stats(username):
    cookie_jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie_jar))

    token_request = Request(
        "https://instastatistics.com/api/token",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with opener.open(token_request, timeout=30) as response:
        token_payload = json.loads(response.read().decode("utf-8"))

    token = token_payload.get("token")
    if not token:
        raise RuntimeError("Instastatistics token endpoint did not return a token.")

    user_request = Request(
        f"https://instastatistics.com/api/user/{username}",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "X-App-Token": token,
        },
    )
    with opener.open(user_request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    followers = payload.get("followers")
    following = payload.get("following")
    posts = payload.get("posts")

    if followers is None:
        stats_request = Request(
            f"https://instastatistics.com/api/stats/{username}",
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "X-App-Token": token,
            },
        )
        with opener.open(stats_request, timeout=30) as response:
            stats_payload = json.loads(response.read().decode("utf-8"))
        follower_points = stats_payload.get("instagram", {}).get("followers", [])
        if not follower_points:
            raise RuntimeError("Instastatistics did not return follower data.")
        followers = follower_points[-1][1]

    return {
        "username": payload.get("username", username),
        "followers": followers,
        "followers_count": followers,
        "followers_display": format_int(followers),
        "following": following,
        "following_display": format_int(following),
        "posts": posts,
        "posts_display": format_int(posts),
        "profile_picture_url": payload.get("avatar"),
        "updated_at": now_utc(),
        "source": "instastatistics_public_cache",
        "note": "Nouzovy verejny fallback bez Meta API tokenu. Hodnota muze byt zpozdena podle cache treti strany.",
    }


def fetch_stats():
    if TOKEN:
        return fetch_api_stats()
    print("IG_ACCESS_TOKEN is missing, using public Instagram profile fallback.")
    try:
        return fetch_public_profile_stats(PUBLIC_USERNAME)
    except Exception as error:
        print(f"Direct Instagram fallback failed: {error}", file=sys.stderr)
        print("Trying Instastatistics public cache fallback.")
        return fetch_instastatistics_stats(PUBLIC_USERNAME)



def main():
    stats = fetch_stats()
    OUTPUT_PATH.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
