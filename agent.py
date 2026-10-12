import json
import os

import anthropic
from dotenv import load_dotenv

from script_writer import write_script
from pipeline import build

load_dotenv()
client = anthropic.Anthropic()
USED_FILE = "output/used_topics.json"
LANGUAGE = "English"


def load_used():
    if os.path.exists(USED_FILE):
        with open(USED_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_used(used):
    os.makedirs("output", exist_ok=True)
    with open(USED_FILE, "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)


def pick_topic(niche, language=LANGUAGE):
    used = load_used()
    prompt = (
        f"YouTube channel niche: {niche}.\n"
        f"Suggest 10 interesting video topics in {language}.\n"
        "Each topic must answer one specific question and rely on real, "
        "verifiable facts.\n"
        f"Do not repeat these topics: {json.dumps(used, ensure_ascii=False)}\n"
        'Return ONLY a JSON list, for example: ["topic 1", "topic 2"]'
    )
    resp = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    text = text.replace("```json", "").replace("```", "")
    topics = [t for t in json.loads(text) if t not in used]
    if not topics:
        raise RuntimeError("No new topic found, run again")
    topic = topics[0]
    used.append(topic)
    save_used(used)
    return topic


def make_one(niche, topic=None, language=LANGUAGE, fmt="shorts"):
    topic = topic or pick_topic(niche, language)
    print("Selected topic:", topic)

    print("Writing script...")
    data = write_script(topic, niche, language)

    scenes = [
        {"narration": s["narration"], "keyword": s["search_keyword"]}
        for s in data["scenes"]
    ]

    video = build(scenes)

    try:
        from thumbnail import make_thumbnail
        make_thumbnail(video, data["title"])
        print("Thumbnail ready: output/thumbnail.jpg")
    except ImportError:
        print("thumbnail.py not found, skipped")

    with open("output/info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Video ready:", video)
    print("Title:", data["title"])

    return {
        "topic": topic,
        "title": data["title"],
        "video": str(video),
        "format": fmt,
    }


def main():
    niche = input("Niche: ")
    make_one(niche)


if __name__ == "__main__":
    main()