import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("PIXABAY_API_KEY")


def _search(keyword, per_page=10):
    if not API_KEY:
        raise RuntimeError("PIXABAY_API_KEY not found in .env")
    r = requests.get(
        "https://pixabay.com/api/videos/",
        params={"key": API_KEY, "q": keyword, "per_page": per_page,
                "safesearch": "true"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("hits", [])


def _pick_url(hit):
    for quality in ("medium", "large", "small", "tiny"):
        info = hit["videos"].get(quality)
        if info and info.get("url"):
            return info["url"]
    return None


def _download(url, path):
    data = requests.get(url, timeout=180)
    data.raise_for_status()
    with open(path, "wb") as f:
        f.write(data.content)


def download_videos(keywords, folder, count=3):
    """Hər açar söz üçün fərqli videolar tapıb endirir (təkrar yoxdur)."""
    if isinstance(keywords, str):
        keywords = [keywords]
    os.makedirs(folder, exist_ok=True)

    pools = []
    for k in keywords:
        try:
            pools.append(_search(k))
        except Exception as e:
            print("Search failed for", k, "-", e)

    paths, seen = [], set()
    depth = 0
    while len(paths) < count and any(depth < len(p) for p in pools):
        for pool in pools:
            if len(paths) >= count:
                break
            if depth < len(pool):
                hit = pool[depth]
                url = _pick_url(hit)
                if hit["id"] in seen or not url:
                    continue
                seen.add(hit["id"])
                path = os.path.join(folder, f"clip{len(paths)}.mp4")
                _download(url, path)
                paths.append(path)
        depth += 1

    if not paths:
        raise RuntimeError(f"No videos found for: {keywords}")
    return paths


def download_video(keyword, path):
    """Köhnə uyğunluq üçün: tək video endirir."""
    clip = download_videos([keyword], os.path.dirname(path) or ".", 1)[0]
    os.replace(clip, path)
    return path


if __name__ == "__main__":
    print(download_videos(["blue sky clouds", "sunset sky"], "temp/test_clips", 3))