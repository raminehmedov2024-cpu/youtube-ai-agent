import asyncio
import math
import os
import shutil
import subprocess

from voice import make_voice
from visuals import download_videos
from editor import make_video

VOICE = "en-US-AndrewNeural"
SEGMENT_SECONDS = 4
FPS = 30
VF = (
    "scale=1920:1080:force_original_aspect_ratio=increase,"
    f"crop=1920:1080,setsar=1,fps={FPS},format=yuv420p"
)

# Yalnız test üçün (agent.py işləyəndə istifadə olunmur)
SCENES = [
    {"narration": "Sunlight looks white, but it is actually made of every color.",
     "keyword": "sunlight | rainbow | prism light"},
    {"narration": "Tiny particles in the air scatter blue light more than other colors.",
     "keyword": "blue sky | clouds timelapse | atmosphere"},
]


def audio_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def fmt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def make_srt(text, duration, path, words_per_line=5):
    words = text.split()
    chunks = [words[i:i + words_per_line] for i in range(0, len(words), words_per_line)]
    total = sum(len(" ".join(c)) for c in chunks) or 1
    t = 0.0
    blocks = []
    for i, c in enumerate(chunks, 1):
        line = " ".join(c)
        d = duration * len(line) / total
        blocks.append(f"{i}\n{fmt(t)} --> {fmt(t + d)}\n{line}\n")
        t += d
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(blocks))


def cut_segment(src, dst, seconds):
    """Klipi eyni formata salıb lazım olan uzunluğa kəsir."""
    subprocess.run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-i", src,
         "-t", f"{seconds:.2f}", "-an", "-vf", VF,
         "-c:v", "libx264", "-preset", "fast", "-crf", "20", dst],
        check=True,
    )


def concat(files, out_path, list_path, reencode=False):
    with open(list_path, "w", encoding="utf-8") as f:
        for p in files:
            f.write("file '" + os.path.abspath(p).replace("\\", "/") + "'\n")
    if reencode:
        codec = ["-c:v", "libx264", "-preset", "fast", "-crf", "20",
                 "-pix_fmt", "yuv420p", "-r", str(FPS),
                 "-c:a", "aac", "-b:a", "192k"]
    else:
        codec = ["-c", "copy"]
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
         *codec, out_path],
        check=True,
    )


def build(scenes, out_path="output/final.mp4", subtitles=True):
    shutil.rmtree("temp", ignore_errors=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    clips = []

    for i, s in enumerate(scenes, 1):
        print(f"Scene {i}/{len(scenes)} is being prepared...")
        audio = f"temp/s{i}.mp3"
        asyncio.run(make_voice(s["narration"], audio, VOICE))
        dur = audio_duration(audio) + 0.3

        keywords = [k.strip() for k in str(s["keyword"]).split("|") if k.strip()]
        n = max(2, min(5, math.ceil(dur / SEGMENT_SECONDS)))
        sources = download_videos(keywords, f"temp/c{i}", count=n)
        seg_len = dur / len(sources)

        segs = []
        for j, src in enumerate(sources):
            seg = f"temp/s{i}_seg{j}.mp4"
            cut_segment(src, seg, seg_len)
            segs.append(seg)

        scene_video = f"temp/s{i}_video.mp4"
        concat(segs, scene_video, f"temp/s{i}_list.txt")

        srt_path = None
        if subtitles:
            srt_path = f"temp/s{i}.srt"
            make_srt(s["narration"], dur - 0.3, srt_path)

        clip = f"temp/s{i}.mp4"
        make_video(scene_video, audio, clip, srt_path)
        clips.append(clip)

    concat(clips, out_path, "temp/list.txt", reencode=True)
    return out_path


if __name__ == "__main__":
    print("Hazir:", build(SCENES))