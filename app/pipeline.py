import asyncio
import os
import subprocess

from voice import make_voice
from visuals import download_video
from editor import make_video

# Ssenari: hər səhnədə danışılan mətn və video üçün ingiliscə açar söz
SCENES = [
    {"narration": "Günəş işığı ağ görünür, amma əslində bütün rənglərdən ibarətdir.",
     "keyword": "sunlight"},
    {"narration": "Havadakı kiçik hissəciklər mavi işığı digər rənglərdən daha çox səpələyir.",
     "keyword": "blue sky"},
    {"narration": "Gün batanda işıq daha uzun yol gəlir, mavi itir, qırmızı və narıncı qalır.",
     "keyword": "sunset sky"},
]

def build(scenes, out_path="output/final.mp4"):
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    clips = []

    for i, s in enumerate(scenes, 1):
        print(f"Sehne {i}/{len(scenes)} hazirlanir...")
        audio = f"temp/s{i}.mp3"
        raw = f"temp/s{i}_raw.mp4"
        clip = f"temp/s{i}.mp4"
        asyncio.run(make_voice(s["narration"], audio))
        download_video(s["keyword"], raw)
        make_video(raw, audio, clip)
        clips.append(clip)

    # Bütün klipləri bir ardıcıllıqla birləşdir
    with open("temp/list.txt", "w", encoding="utf-8") as f:
        for c in clips:
            path = os.path.abspath(c).replace(chr(92), "/")
            f.write("file '" + path + "'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", "temp/list.txt", "-c", "copy", out_path],
        check=True,
    )
    return out_path

if __name__ == "__main__":
    result = build(SCENES)
    print("Hazir:", result)